"""
FHIR Client Service - Base Client with Error Handling
Handles all FHIR server communication with caching, retries, and circuit breaker
"""

import httpx
import logging
import json
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import asyncio
from functools import wraps
import hashlib
from app.utils.errors import (
    FHIRServerError,
    FHIRNotFoundError,
    FHIRValidationError,
    FHIRTimeoutError
)
import os

logger = logging.getLogger(__name__)

# ============================================================================
# FHIR CLIENT
# ============================================================================

class FHIRClient:
    """
    Base FHIR Client for communication with HAPI FHIR Server
    Features:
    - Error handling with circuit breaker
    - Request timeout handling
    - Response validation
    - Logging and audit trail
    """

    def __init__(
        self,
        base_url: str = None,
        timeout: float = 5.0,
        max_retries: int = 3
    ):
        """
        Initialize FHIR Client

        Args:
            base_url: FHIR Server URL (default: env FHIR_BASE_URL)
            timeout: Request timeout in seconds (default: 5.0)
            max_retries: Max retries on failure (default: 3)
        """
        self.base_url = base_url or os.getenv("FHIR_BASE_URL", "http://localhost:8080/fhir")
        self.timeout = timeout
        self.max_retries = max_retries
        self.circuit_breaker_open = False
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_reset_time = datetime.utcnow()

    def _check_circuit_breaker(self):
        """Check if circuit breaker is open"""
        if self.circuit_breaker_open:
            # Reset after 5 minutes
            if datetime.utcnow() - self.circuit_breaker_reset_time > timedelta(minutes=5):
                logger.info("Circuit breaker reset - attempting reconnection")
                self.circuit_breaker_open = False
                self.circuit_breaker_failures = 0
            else:
                raise FHIRServerError(
                    "FHIR server is temporarily unavailable. Circuit breaker is open.",
                    {"retry_after": 300}
                )

    def _record_failure(self):
        """Record a failure and potentially open circuit breaker"""
        self.circuit_breaker_failures += 1
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            logger.warning(f"Circuit breaker opened after {self.circuit_breaker_failures} failures")
            self.circuit_breaker_open = True
            self.circuit_breaker_reset_time = datetime.utcnow()

    def _record_success(self):
        """Record a success and reset failure counter"""
        self.circuit_breaker_failures = 0

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make HTTP request to FHIR server with retry logic

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: FHIR endpoint path
            params: Query parameters
            json_data: Request body
            retry_count: Current retry attempt

        Returns:
            Response JSON

        Raises:
            FHIRServerError: FHIR server error
            FHIRTimeoutError: Request timeout
            FHIRValidationError: Validation error
        """
        self._check_circuit_breaker()

        url = f"{self.base_url}/{endpoint}".rstrip("/")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"FHIR {method} request: {url}")

                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data
                )

            # Log response
            logger.debug(f"FHIR response: {response.status_code}")

            # Handle errors
            if response.status_code == 404:
                self._record_success()
                return {"resourceType": "Bundle", "entry": [], "total": 0}

            if response.status_code >= 400:
                self._record_failure()

                if response.status_code == 400:
                    raise FHIRValidationError(
                        response.json().get("issue", [{}])[0].get("diagnostics", "Invalid request")
                    )
                elif response.status_code == 401:
                    raise FHIRValidationError("FHIR server authentication failed")
                elif response.status_code >= 500:
                    raise FHIRServerError(
                        f"FHIR server error: {response.status_code}",
                        {"status_code": response.status_code}
                    )
                else:
                    raise FHIRValidationError(f"FHIR error: {response.status_code}")

            self._record_success()

            # Parse and return response
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response from FHIR server")
                raise FHIRServerError("Invalid JSON response from FHIR server")

        except asyncio.TimeoutError:
            self._record_failure()
            logger.error(f"FHIR request timeout after {self.timeout}s")
            raise FHIRTimeoutError()

        except httpx.ConnectError as e:
            self._record_failure()
            logger.error(f"FHIR server connection error: {str(e)}")

            if retry_count < self.max_retries:
                logger.info(f"Retrying FHIR request ({retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self._make_request(method, endpoint, params, json_data, retry_count + 1)

            raise FHIRServerError(f"FHIR server connection failed: {str(e)}")

        except Exception as e:
            self._record_failure()
            logger.error(f"FHIR request error: {str(e)}")
            raise FHIRServerError(f"FHIR request failed: {str(e)}")

    async def search(
        self,
        resource_type: str,
        **params
    ) -> Dict[str, Any]:
        """
        Search FHIR resources

        Args:
            resource_type: FHIR resource type (Patient, Medication, etc.)
            **params: Search parameters

        Returns:
            FHIR Bundle response
        """
        logger.info(f"FHIR search: {resource_type} with params {params}")
        return await self._make_request("GET", resource_type, params=params)

    async def get_resource(
        self,
        resource_type: str,
        resource_id: str
    ) -> Dict[str, Any]:
        """
        Get single FHIR resource

        Args:
            resource_type: FHIR resource type
            resource_id: Resource ID

        Returns:
            FHIR resource

        Raises:
            FHIRNotFoundError: Resource not found
        """
        logger.info(f"FHIR get: {resource_type}/{resource_id}")

        try:
            return await self._make_request(
                "GET",
                f"{resource_type}/{resource_id}"
            )
        except Exception as e:
            if "404" in str(e):
                raise FHIRNotFoundError(resource_type, resource_id)
            raise

    async def create_resource(
        self,
        resource: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create FHIR resource

        Args:
            resource: FHIR resource object

        Returns:
            Created resource with ID
        """
        resource_type = resource.get("resourceType")
        logger.info(f"FHIR create: {resource_type}")

        return await self._make_request(
            "POST",
            resource_type,
            json_data=resource
        )

    async def update_resource(
        self,
        resource_type: str,
        resource_id: str,
        resource: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update FHIR resource

        Args:
            resource_type: FHIR resource type
            resource_id: Resource ID
            resource: Updated resource object

        Returns:
            Updated resource
        """
        logger.info(f"FHIR update: {resource_type}/{resource_id}")

        return await self._make_request(
            "PUT",
            f"{resource_type}/{resource_id}",
            json_data=resource
        )

    def _generate_cache_key(
        self,
        resource_type: str,
        params: Dict[str, Any] = None
    ) -> str:
        """Generate cache key from resource type and params"""
        params_str = json.dumps(params or {}, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"fhir:{resource_type}:{params_hash}"


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_fhir_client: Optional[FHIRClient] = None

def get_fhir_client() -> FHIRClient:
    """Get or create singleton FHIR client"""
    global _fhir_client
    if _fhir_client is None:
        _fhir_client = FHIRClient()
    return _fhir_client

