"""
FHIR Patient Service
Handles patient search and retrieval from HAPI FHIR Server
"""

import logging
from typing import Dict, List, Optional, Any
from app.services.fhir_client import get_fhir_client
from app.utils.errors import PatientNotFoundError, FHIRValidationError
import asyncio

logger = logging.getLogger(__name__)


class FHIRPatientService:
    """
    Service for FHIR Patient resource operations
    TASK-3.6 Implementation
    """

    @staticmethod
    async def search_patients(
        given: Optional[str] = None,
        family: Optional[str] = None,
        birthdate: Optional[str] = None,
        email: Optional[str] = None,
        identifier: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for patients in FHIR server

        Args:
            given: First name
            family: Last name
            birthdate: Date of birth (YYYY-MM-DD)
            email: Email address
            identifier: MRN or other identifier (system|value)
            limit: Result limit (max 100)
            offset: Pagination offset

        Returns:
            List of patients matching criteria
        """
        client = get_fhir_client()

        # Build search parameters
        params = {}

        if given:
            params["given"] = given
        if family:
            params["family"] = family
        if birthdate:
            params["birthdate"] = birthdate
        if email:
            params["email"] = email
        if identifier:
            params["identifier"] = identifier

        params["_count"] = min(limit, 100)
        params["_offset"] = offset

        logger.info(f"Searching patients with params: {params}")

        try:
            bundle = await client.search("Patient", **params)

            patients = []
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                patients.append(_format_patient(resource))

            return {
                "success": True,
                "total": bundle.get("total", 0),
                "count": len(patients),
                "offset": offset,
                "limit": limit,
                "patients": patients
            }

        except Exception as e:
            logger.error(f"Patient search error: {str(e)}")
            raise

    @staticmethod
    async def get_patient(patient_id: str) -> Dict[str, Any]:
        """
        Get single patient by ID

        Args:
            patient_id: FHIR Patient ID

        Returns:
            Formatted patient object

        Raises:
            PatientNotFoundError: If patient not found
        """
        client = get_fhir_client()

        logger.info(f"Getting patient: {patient_id}")

        try:
            patient = await client.get_resource("Patient", patient_id)
            return _format_patient(patient)

        except Exception as e:
            logger.error(f"Get patient error: {str(e)}")
            if "404" in str(e):
                raise PatientNotFoundError(patient_id)
            raise

    @staticmethod
    async def create_patient(patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new patient in FHIR server

        Args:
            patient_data: Patient resource data

        Returns:
            Created patient with ID
        """
        client = get_fhir_client()

        # Add resource type
        patient_data["resourceType"] = "Patient"

        logger.info(f"Creating patient: {patient_data.get('name', [{}])[0].get('text', 'Unknown')}")

        try:
            created = await client.create_resource(patient_data)
            return _format_patient(created)

        except Exception as e:
            logger.error(f"Create patient error: {str(e)}")
            raise

    @staticmethod
    async def update_patient(
        patient_id: str,
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update existing patient

        Args:
            patient_id: FHIR Patient ID
            patient_data: Updated patient data

        Returns:
            Updated patient
        """
        client = get_fhir_client()

        patient_data["resourceType"] = "Patient"
        patient_data["id"] = patient_id

        logger.info(f"Updating patient: {patient_id}")

        try:
            updated = await client.update_resource("Patient", patient_id, patient_data)
            return _format_patient(updated)

        except Exception as e:
            logger.error(f"Update patient error: {str(e)}")
            raise


# ============================================================================
# FORMATTING HELPERS
# ============================================================================

def _format_patient(resource: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format FHIR Patient resource for API response
    """
    names = resource.get("name", [])
    name_obj = names[0] if names else {}

    telecoms = resource.get("telecom", [])
    phone = next((t.get("value") for t in telecoms if t.get("system") == "phone"), None)
    email = next((t.get("value") for t in telecoms if t.get("system") == "email"), None)

    addresses = resource.get("address", [])
    address_obj = addresses[0] if addresses else {}

    return {
        "id": resource.get("id"),
        "given_name": " ".join(name_obj.get("given", [])) if name_obj else "",
        "family_name": name_obj.get("family", "") if name_obj else "",
        "birth_date": resource.get("birthDate"),
        "gender": resource.get("gender"),
        "phone": phone,
        "email": email,
        "address": {
            "line": " ".join(address_obj.get("line", [])) if address_obj else "",
            "city": address_obj.get("city") if address_obj else "",
            "state": address_obj.get("state") if address_obj else "",
            "postal_code": address_obj.get("postalCode") if address_obj else "",
            "country": address_obj.get("country") if address_obj else ""
        } if address_obj else None,
        "identifiers": [
            {
                "system": ident.get("system"),
                "value": ident.get("value"),
                "type": ident.get("type", {}).get("text", "")
            }
            for ident in resource.get("identifier", [])
        ]
    }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_patient_service: Optional[FHIRPatientService] = None

def get_patient_service() -> FHIRPatientService:
    """Get singleton patient service"""
    global _patient_service
    if _patient_service is None:
        _patient_service = FHIRPatientService()
    return _patient_service

