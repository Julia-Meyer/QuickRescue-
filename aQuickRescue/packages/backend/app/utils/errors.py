"""
Custom Exception Classes and Error Handling
Speckit Compliance: Standardized error responses
"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import uuid
from datetime import datetime


class AppException(HTTPException):
    """Base application exception"""

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.request_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()

        detail = {
            "error": error_code,
            "message": message,
            "status": status_code,
            "timestamp": self.timestamp,
            "request_id": self.request_id
        }

        if details:
            detail["details"] = details

        super().__init__(status_code=status_code, detail=detail)


# ============================================================================
# 1. AUTHENTICATION ERRORS
# ============================================================================

class InvalidCredentialsError(AppException):
    """AUTH_001: Invalid credentials"""
    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(
            error_code="AUTH_001",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class TokenExpiredError(AppException):
    """AUTH_002: Token expired"""
    def __init__(self, message: str = "Token has expired"):
        super().__init__(
            error_code="AUTH_002",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class InvalidTokenError(AppException):
    """AUTH_003: Invalid token"""
    def __init__(self, message: str = "Invalid or malformed token"):
        super().__init__(
            error_code="AUTH_003",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class UnauthorizedError(AppException):
    """AUTH_004: Unauthorized access"""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            error_code="AUTH_004",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


# ============================================================================
# 2. PATIENT ERRORS
# ============================================================================

class PatientNotFoundError(AppException):
    """PATIENT_001: Patient not found"""
    def __init__(self, patient_id: str):
        super().__init__(
            error_code="PATIENT_001",
            message=f"Patient with ID '{patient_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class UnauthorizedAccessError(AppException):
    """PATIENT_002: Unauthorized access to patient data"""
    def __init__(self, message: str = "You do not have permission to access this patient's data"):
        super().__init__(
            error_code="PATIENT_002",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class EmergencyAccessNotEnabledError(AppException):
    """PATIENT_003: Emergency access not enabled"""
    def __init__(self):
        super().__init__(
            error_code="PATIENT_003",
            message="Patient has not enabled emergency access",
            status_code=status.HTTP_403_FORBIDDEN
        )


# ============================================================================
# 3. VALIDATION ERRORS
# ============================================================================

class InvalidEmailError(AppException):
    """VAL_001: Invalid email format"""
    def __init__(self, email: str):
        super().__init__(
            error_code="VAL_001",
            message=f"Invalid email format: {email}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class PasswordTooWeakError(AppException):
    """VAL_002: Password too weak"""
    def __init__(self):
        super().__init__(
            error_code="VAL_002",
            message="Password must be at least 8 characters with uppercase, lowercase, number, and special character",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class MissingFieldError(AppException):
    """VAL_003: Missing required field"""
    def __init__(self, field_name: str):
        super().__init__(
            error_code="VAL_003",
            message=f"Missing required field: {field_name}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class InvalidInputError(AppException):
    """VAL_004: Invalid input"""
    def __init__(self, message: str):
        super().__init__(
            error_code="VAL_004",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )


# ============================================================================
# 4. FHIR ERRORS
# ============================================================================

class FHIRServerError(AppException):
    """FHIR_001: FHIR server error"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            error_code="FHIR_001",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class FHIRNotFoundError(AppException):
    """FHIR_002: FHIR resource not found"""
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            error_code="FHIR_002",
            message=f"{resource_type} with ID '{resource_id}' not found in FHIR server",
            status_code=status.HTTP_404_NOT_FOUND
        )


class FHIRValidationError(AppException):
    """FHIR_003: FHIR validation error"""
    def __init__(self, message: str):
        super().__init__(
            error_code="FHIR_003",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class FHIRTimeoutError(AppException):
    """FHIR_004: FHIR server timeout"""
    def __init__(self):
        super().__init__(
            error_code="FHIR_004",
            message="FHIR server request timed out",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT
        )


# ============================================================================
# 5. RATE LIMITING ERRORS
# ============================================================================

class RateLimitError(AppException):
    """RATE_001: Rate limit exceeded"""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            error_code="RATE_001",
            message=f"Rate limit exceeded. Try again in {retry_after} seconds",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after}
        )


# ============================================================================
# 6. SERVER ERRORS
# ============================================================================

class InternalServerError(AppException):
    """SERVER_001: Internal server error"""
    def __init__(self, message: str = "An unexpected error occurred"):
        super().__init__(
            error_code="SERVER_001",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# ERROR CODE REFERENCE
# ============================================================================

ERROR_CODES = {
    # Auth
    "AUTH_001": "Invalid credentials",
    "AUTH_002": "Token expired",
    "AUTH_003": "Invalid token",
    "AUTH_004": "Unauthorized access",

    # Patient
    "PATIENT_001": "Patient not found",
    "PATIENT_002": "Unauthorized access to patient",
    "PATIENT_003": "Emergency access not enabled",

    # Validation
    "VAL_001": "Invalid email format",
    "VAL_002": "Password too weak",
    "VAL_003": "Missing required field",
    "VAL_004": "Invalid input",

    # FHIR
    "FHIR_001": "FHIR server error",
    "FHIR_002": "FHIR resource not found",
    "FHIR_003": "FHIR validation error",
    "FHIR_004": "FHIR server timeout",

    # Rate limiting
    "RATE_001": "Rate limit exceeded",

    # Server
    "SERVER_001": "Internal server error",
}

