"""
aQuickRescue - Emergency Health Data Backend API
Main FastAPI application with OAuth2, Patient search, and Audit logging
"""

import fastapi
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging (JSON format for Speckit compliance)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import new services and error handlers
from app.utils.errors import (
    AppException,
    InvalidCredentialsError,
    TokenExpiredError,
    InvalidTokenError,
    UnauthorizedError,
    PatientNotFoundError,
    EmergencyAccessNotEnabledError
)
from app.services.fhir_patient import get_patient_service
from app.services.fhir_medication import get_medication_service
from app.services.fhir_allergy import get_allergy_service
from app.services.fhir_summary import get_summary_service
from app.services.fhir_service import FHIRService

# ============================================================================
# 1. DATABASE SETUP
# ============================================================================

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel, Field, EmailStr

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/aQuickRescue")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# 2. DATABASE MODELS
# ============================================================================

class User(Base):
    """User model - Patient, Responder, Admin"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String)  # PATIENT, FIRST_RESPONDER, PHYSICIAN, ADMIN
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patients = relationship("PatientProfile", back_populates="owner")
    emergency_access = relationship("EmergencyAccess", back_populates="responder")
    audit_events = relationship("AuditLog", back_populates="user")

class PatientProfile(Base):
    """Patient profile - extended patient data"""
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    fhir_patient_id = Column(String, unique=True, index=True)  # Reference to FHIR Patient
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    date_of_birth = Column(String)
    emergency_contact_name = Column(String)
    emergency_contact_phone = Column(String)
    emergency_access_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="patients")
    emergency_accesses = relationship("EmergencyAccess", back_populates="patient")

class EmergencyAccess(Base):
    """Emergency access request - when responder accesses patient data"""
    __tablename__ = "emergency_access"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), index=True)
    responder_id = Column(Integer, ForeignKey("users.id"), index=True)
    reason = Column(Text)
    gps_location = Column(String)  # Latitude, Longitude
    accessed_at = Column(DateTime, default=datetime.utcnow)
    data_requested = Column(String)  # JSON: ["Allergies", "Medications", "Contacts"]
    status = Column(String, default="GRANTED")  # GRANTED, DENIED, EXPIRED
    ip_address = Column(String)

    # Relationships
    patient = relationship("PatientProfile", back_populates="emergency_accesses")
    responder = relationship("User", back_populates="emergency_access")

class AuditLog(Base):
    """Audit Log - FHIR AuditEvent equivalent"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), index=True)
    action = Column(String)  # CREATE, READ, UPDATE, DELETE, EMERGENCY_ACCESS
    resource_type = Column(String)  # Patient, AllergyIntolerance, Medication, etc.
    resource_id = Column(String)
    reason = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address = Column(String)
    gps_location = Column(String, nullable=True)
    status = Column(String)  # SUCCESS, DENIED, FAILED
    error_message = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_events")

# Create all tables
Base.metadata.create_all(bind=engine)

# ============================================================================
# 3. PYDANTIC MODELS (Request/Response)
# ============================================================================

class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str

class PatientSearchRequest(BaseModel):
    """Search patient by name and DOB"""
    first_name: str
    last_name: str
    date_of_birth: str  # YYYY-MM-DD

class EmergencyAccessRequest(BaseModel):
    """Request emergency access to patient data"""
    patient_id: str  # FHIR Patient ID or local ID
    reason: str = Field(..., min_length=10, max_length=500)
    requested_data: List[str]  # ["Allergies", "Medications", "Contacts"]
    gps_location: Optional[str] = None

class PatientResponse(BaseModel):
    """Patient data response"""
    fhir_patient_id: str
    first_name: str
    last_name: str
    date_of_birth: str
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    allergies: List[dict] = []
    medications: List[dict] = []

    class Config:
        orm_mode = True

class AuditLogResponse(BaseModel):
    """Audit log entry response"""
    id: int
    user: str
    action: str
    resource_type: str
    timestamp: datetime
    reason: Optional[str]
    status: str

    class Config:
        orm_mode = True

# ============================================================================
# 4. SECURITY & AUTHENTICATION
# ============================================================================

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from typing import Dict

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, db: Session) -> User:
    """Verify JWT token and return user"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security),
                          db: Session = Depends(get_db)) -> User:
    """Dependency: Get current authenticated user"""
    return verify_token(credentials.credentials, db)

def check_role(required_role: str):
    """Role-based access control"""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and required_role != "ANY":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# ============================================================================
# 5. AUDIT LOGGING SERVICE
# ============================================================================

class AuditService:
    """Service for logging all data access (HIPAA compliance)"""

    @staticmethod
    def log_access(
        db: Session,
        user_id: int,
        patient_id: int,
        action: str,
        resource_type: str,
        resource_id: str,
        reason: str,
        ip_address: str,
        status: str = "SUCCESS",
        error_message: Optional[str] = None,
        gps_location: Optional[str] = None
    ):
        """
        Log every access to patient data
        Speckit Compliance: Security requirement - 100% audit trail
        """
        audit_entry = AuditLog(
            user_id=user_id,
            patient_id=patient_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            reason=reason,
            ip_address=ip_address,
            status=status,
            error_message=error_message,
            gps_location=gps_location,
            timestamp=datetime.utcnow()
        )
        db.add(audit_entry)
        db.commit()

        # Log to structured logger (JSON format for ELK/Datadog)
        logger.info({
            "event": "patient_data_access",
            "user_id": user_id,
            "patient_id": patient_id,
            "action": action,
            "resource_type": resource_type,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status
        })

# ============================================================================
# 6. FHIR CLIENT SERVICE (Mock.Health Integration)
# ============================================================================

class MockHealthService:
    """Service for Mock.Health FHIR API integration"""

    # Load Mock.Health config from env
    HAPI_BASE_URL = os.getenv("FHIR_BASE_URL", "https://hapi.fhir.org/baseR4")
    MOCK_HEALTH_API_URL = os.getenv("MOCK_HEALTH_API_URL", "https://api.mock.health")
    MOCK_HEALTH_FHIR_URL = os.getenv("MOCK_HEALTH_FHIR_URL", "https://api.mock.health/fhir")
    MOCK_HEALTH_API_KEY = os.getenv("MOCK_HEALTH_API_KEY", "")

    # Cache TTLs (seconds)
    TTL_PATIENT = int(os.getenv("CACHE_TTL_PATIENT", 3600))
    TTL_MEDICATIONS = int(os.getenv("CACHE_TTL_MEDICATIONS", 1800))
    TTL_ALLERGIES = int(os.getenv("CACHE_TTL_ALLERGIES", 1800))
    TTL_CONDITIONS = int(os.getenv("CACHE_TTL_CONDITIONS", 3600))
    TTL_RELATED = int(os.getenv("CACHE_TTL_RELATED", 3600))

    @staticmethod
    def _get_headers():
        """Get HTTP headers with Mock.Health API key"""
        return {
            "Authorization": f"Bearer {MockHealthService.MOCK_HEALTH_API_KEY}",
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json"
        }

    @staticmethod
    def _build_url(resource_type: str):
        """Build FHIR resource URL for Mock.Health"""
        return f"{MockHealthService.MOCK_HEALTH_FHIR_URL}/{resource_type}"


class FHIRService:
    """Service for FHIR server integration (delegates to MockHealthService)"""

    FHIR_BASE_URL = MockHealthService.MOCK_HEALTH_FHIR_URL
    # cache TTLs (seconds)
    TTL_PATIENT = int(os.getenv("CACHE_TTL_PATIENT", 3600))
    TTL_MEDICATIONS = int(os.getenv("CACHE_TTL_MEDICATIONS", 1800))
    TTL_ALLERGIES = int(os.getenv("CACHE_TTL_ALLERGIES", 1800))
    TTL_CONDITIONS = int(os.getenv("CACHE_TTL_CONDITIONS", 3600))
    TTL_RELATED = int(os.getenv("CACHE_TTL_RELATED", 3600))

    @staticmethod
    def search_patient(first_name: str, last_name: str, dob: str) -> dict:
        """
        Search Mock.Health FHIR server for patient
        Performance: Target < 2 seconds
        """
        import httpx

        try:
            query = MockHealthService._build_url("Patient")
            params = {}
            if first_name:
                params["given"] = first_name
            if last_name:
                params["family"] = last_name
            if dob:
                params["birthdate"] = dob

            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=params, headers=headers)
                response.raise_for_status()

            bundle = response.json()

            if bundle.get("total", 0) == 0:
                return {"found": False, "patients": []}

            patients = []
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                patients.append({
                    "id": resource.get("id"),
                    "name": " ".join([
                        name.get("given", [""])[0]
                        for name in resource.get("name", [])
                    ]),
                    "birthDate": resource.get("birthDate")
                })

            logger.info(f"Found {len(patients)} patients matching criteria")
            return {"found": True, "patients": patients}
        except Exception as e:
            logger.error(f"Mock.Health FHIR search error: {str(e)}")
            return {"found": False, "error": str(e)}

    @staticmethod
    def get_patient_allergies(patient_id: str) -> List[dict]:
        """Get patient allergies from Mock.Health FHIR server"""
        import httpx

        try:
            query = MockHealthService._build_url("AllergyIntolerance")
            params = {"patient": patient_id}
            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=params, headers=headers)
                response.raise_for_status()

            bundle = response.json()
            allergies = []

            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                code = resource.get("code", {}).get("coding", [{}])[0]
                allergies.append({
                    "code": code.get("code"),
                    "display": code.get("display"),
                    "criticality": resource.get("criticality", "unknown")
                })

            logger.info(f"Retrieved {len(allergies)} allergies for patient {patient_id}")
            return allergies
        except Exception as e:
            logger.error(f"Error fetching allergies from Mock.Health: {str(e)}")
            return []

    @staticmethod
    def get_patient_medications(patient_id: str) -> List[dict]:
        """Get patient medications (MedicationStatement) from Mock.Health FHIR server"""
        import httpx

        try:
            query = MockHealthService._build_url("MedicationStatement")
            params = {"patient": patient_id}
            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=params, headers=headers)
                response.raise_for_status()

            bundle = response.json()
            medications = []

            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                medications.append({
                    "id": resource.get("id"),
                    "medication": resource.get("medicationReference", {}).get("display", "Unknown"),
                    "dosage": resource.get("dosage", [{}])[0].get("text", ""),
                    "status": resource.get("status", "unknown")
                })

            logger.info(f"Retrieved {len(medications)} medications for patient {patient_id}")
            return medications
        except Exception as e:
            logger.error(f"Error fetching medications from Mock.Health: {str(e)}")
            return []

    @staticmethod
    def get_patient(patient_id: str) -> dict:
        """Get a single Patient resource from Mock.Health FHIR"""
        import httpx
        try:
            key = f"patient:{patient_id}"
            # Try cache if available
            try:
                from packages.backend.app.services.cache import cache
                cached = cache.get(key)
                if cached:
                    logger.info(f"Cache hit for patient {patient_id}")
                    return cached
            except Exception:
                cached = None

            query = MockHealthService._build_url(f"Patient/{patient_id}")
            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, headers=headers)
                response.raise_for_status()

            resource = response.json()

            # Cache
            try:
                from packages.backend.app.services.cache import cache
                cache.set(key, resource, FHIRService.TTL_PATIENT)
            except Exception:
                pass

            logger.info(f"Retrieved patient {patient_id} from Mock.Health")
            return resource
        except Exception as e:
            logger.error(f"Error fetching patient {patient_id} from Mock.Health: {str(e)}")
            return {}

    @staticmethod
    def get_medication_statements(patient_id: str, params: Dict = None) -> dict:
        import httpx
        try:
            key = f"meds:{patient_id}:{str(params)}"
            try:
                from packages.backend.app.services.cache import cache
                cached = cache.get(key)
                if cached:
                    logger.info(f"Cache hit for medication statements {patient_id}")
                    return cached
            except Exception:
                cached = None

            query = MockHealthService._build_url("MedicationStatement")
            query_params = {"patient": patient_id}
            if params:
                query_params.update(params)

            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=query_params, headers=headers)
                response.raise_for_status()

            bundle = response.json()

            try:
                from packages.backend.app.services.cache import cache
                cache.set(key, bundle, FHIRService.TTL_MEDICATIONS)
            except Exception:
                pass

            logger.info(f"Retrieved {bundle.get('total', 0)} medication statements for patient {patient_id}")
            return bundle
        except Exception as e:
            logger.error(f"Error fetching medication statements for {patient_id}: {str(e)}")
            return {"entry": []}

    @staticmethod
    def get_conditions(patient_id: str, params: Dict = None) -> dict:
        import httpx
        try:
            key = f"conds:{patient_id}:{str(params)}"
            try:
                from packages.backend.app.services.cache import cache
                cached = cache.get(key)
                if cached:
                    logger.info(f"Cache hit for conditions {patient_id}")
                    return cached
            except Exception:
                cached = None

            query = MockHealthService._build_url("Condition")
            query_params = {"patient": patient_id}
            if params:
                query_params.update(params)

            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=query_params, headers=headers)
                response.raise_for_status()

            bundle = response.json()

            try:
                from packages.backend.app.services.cache import cache
                cache.set(key, bundle, FHIRService.TTL_CONDITIONS)
            except Exception:
                pass

            logger.info(f"Retrieved {bundle.get('total', 0)} conditions for patient {patient_id}")
            return bundle
        except Exception as e:
            logger.error(f"Error fetching conditions for {patient_id}: {str(e)}")
            return {"entry": []}

    @staticmethod
    def get_related_persons(patient_id: str, params: Dict = None) -> dict:
        import httpx
        try:
            key = f"related:{patient_id}:{str(params)}"
            try:
                from packages.backend.app.services.cache import cache
                cached = cache.get(key)
                if cached:
                    logger.info(f"Cache hit for related persons {patient_id}")
                    return cached
            except Exception:
                cached = None

            query = MockHealthService._build_url("RelatedPerson")
            query_params = {"patient": patient_id}
            if params:
                query_params.update(params)

            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=query_params, headers=headers)
                response.raise_for_status()

            bundle = response.json()

            try:
                from packages.backend.app.services.cache import cache
                cache.set(key, bundle, FHIRService.TTL_RELATED)
            except Exception:
                pass

            logger.info(f"Retrieved {bundle.get('total', 0)} related persons for patient {patient_id}")
            return bundle
        except Exception as e:
            logger.error(f"Error fetching related persons for {patient_id}: {str(e)}")
            return {"entry": []}

# ============================================================================
# 7. FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="aQuickRescue API",
    description="Emergency Health Data Access API - FHIR & Audit Compliant",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# GLOBAL ERROR HANDLERS
# ============================================================================

@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    """Handle custom application exceptions"""
    logger.error(f"App exception: {exc.error_code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "status": exc.status_code,
            "timestamp": exc.timestamp,
            "request_id": exc.request_id,
            **({"details": exc.details} if exc.details else {})
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {type(exc).__name__} - {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "SERVER_001",
            "message": "An unexpected error occurred",
            "status": 500
        }
    )

# ============================================================================
# 8. FHIR INTEGRATION ENDPOINTS (TASK-3.6 through TASK-3.10)
# ============================================================================

# -------- FHIR Patient Endpoints (TASK-3.6) --------

@app.get("/api/v1/fhir/patients")
async def search_fhir_patients(
    given: Optional[str] = None,
    family: Optional[str] = None,
    birthdate: Optional[str] = None,
    email: Optional[str] = None,
    identifier: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search FHIR Patient resources
    
    Access Control: FIRST_RESPONDER, PHYSICIAN, ADMIN only
    Performance: Target < 2 seconds
    """
    if current_user.role not in ["FIRST_RESPONDER", "EMERGENCY_PHYSICIAN", "ADMIN"]:
        raise UnauthorizedError("Only first responders can search patients")
    
    # Log search attempt
    AuditService.log_access(
        db=db,
        user_id=current_user.id,
        patient_id=0,
        action="FHIR_PATIENT_SEARCH",
        resource_type="Patient",
        resource_id="multiple",
        reason=f"Patient search: {given} {family}",
        ip_address="127.0.0.1",
        status="SUCCESS"
    )
    
    patient_service = get_patient_service()
    return await patient_service.search_patients(
        given=given,
        family=family,
        birthdate=birthdate,
        email=email,
        identifier=identifier,
        limit=limit,
        offset=offset
    )


@app.get("/api/v1/fhir/patients/{patient_id}")
async def get_fhir_patient(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get single FHIR Patient by ID
    """
    if current_user.role not in ["FIRST_RESPONDER", "EMERGENCY_PHYSICIAN", "ADMIN", "PATIENT"]:
        raise UnauthorizedError()
    
    # Log access
    AuditService.log_access(
        db=db,
        user_id=current_user.id,
        patient_id=0,
        action="FHIR_PATIENT_READ",
        resource_type="Patient",
        resource_id=patient_id,
        reason="Get patient details",
        ip_address="127.0.0.1",
        status="SUCCESS"
    )
    
    patient_service = get_patient_service()
    return await patient_service.get_patient(patient_id)


# -------- FHIR Allergy Endpoints (TASK-3.8) - CRITICAL --------

@app.get("/api/v1/fhir/allergies")
async def get_patient_allergies(
    patient: str,
    clinical_status: Optional[str] = "active",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient allergies - CRITICAL for emergency responders
    
    Returns critical allergies with severity flags
    """
    if current_user.role not in ["FIRST_RESPONDER", "EMERGENCY_PHYSICIAN", "ADMIN"]:
        raise UnauthorizedError()
    
    # Extract patient ID
    patient_id = patient.split("/")[-1] if "/" in patient else patient
    
    # Log access (important!)
    AuditService.log_access(
        db=db,
        user_id=current_user.id,
        patient_id=0,
        action="FHIR_ALLERGY_READ",
        resource_type="AllergyIntolerance",
        resource_id=patient_id,
        reason="Emergency access - check allergies",
        ip_address="127.0.0.1",
        status="SUCCESS"
    )
    
    allergy_service = get_allergy_service()
    return await allergy_service.get_patient_allergies(
        patient_id=patient_id,
        clinical_status=clinical_status
    )


# -------- FHIR Medication Endpoints (TASK-3.7) --------

@app.get("/api/v1/fhir/medications")
async def get_patient_medications(
    patient: str,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient medications from MedicationDispense
    """
    if current_user.role not in ["FIRST_RESPONDER", "EMERGENCY_PHYSICIAN", "ADMIN"]:
        raise UnauthorizedError()
    
    # Extract patient ID
    patient_id = patient.split("/")[-1] if "/" in patient else patient
    
    # Log access
    AuditService.log_access(
        db=db,
        user_id=current_user.id,
        patient_id=0,
        action="FHIR_MEDICATION_READ",
        resource_type="MedicationDispense",
        resource_id=patient_id,
        reason="Get patient medications",
        ip_address="127.0.0.1",
        status="SUCCESS"
    )
    
    medication_service = get_medication_service()
    return await medication_service.get_patient_medications(
        patient_id=patient_id,
        status=status
    )


# -------- FHIR Emergency Summary Endpoint (TASK-3.10) - CRITICAL --------

@app.get("/api/v1/fhir/patient-summary/{patient_id}")
async def get_emergency_patient_summary(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive patient summary for emergency responders
    
    CRITICAL ENDPOINT - Returns everything needed in < 3 seconds
    Includes allergies, medications, conditions, vital signs
    
    Performance Target: < 3 seconds
    """
    if current_user.role not in ["FIRST_RESPONDER", "EMERGENCY_PHYSICIAN", "ADMIN"]:
        raise UnauthorizedError("Only emergency responders can access patient summary")
    
    # Log emergency access
    AuditService.log_access(
        db=db,
        user_id=current_user.id,
        patient_id=0,
        action="EMERGENCY_SUMMARY_ACCESS",
        resource_type="Patient",
        resource_id=patient_id,
        reason="Emergency patient summary access",
        ip_address="127.0.0.1",
        status="SUCCESS"
    )
    
    summary_service = get_summary_service()
    summary = await summary_service.get_patient_summary(patient_id)
    
    # Log response time warning if slow
    if summary.get("response_time_ms", 0) >= 3000:
        logger.warning(f"Emergency summary response time: {summary['response_time_ms']:.0f}ms (exceeds 3s target)")
    
    return summary


# ============================================================================
# 9. API ENDPOINTS (ORIGINAL)
# ============================================================================

@app.post("/api/v1/auth/login")
def login(request: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint - OAuth2 compatible

    Returns JWT access token valid for 15 minutes
    """
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        # Log failed attempt
        logger.warning(f"Failed login attempt: {request.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }

@app.get("/api/v1/patients/search")
def search_patients(
    first_name: str,
    last_name: str,
    date_of_birth: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search FHIR server for patient by name and DOB

    Access Control: FIRST_RESPONDER, PHYSICIAN, ADMIN only
    Audit: Logged
    Performance: Target < 2 seconds
    """
    # Check if user is responder or higher
    if current_user.role not in ["FIRST_RESPONDER", "EMERGENCY_PHYSICIAN", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    params = {}
    if status:
        params["status"] = status

    bundle = FHIRService.get_medication_statements(patient, params)

    AuditService.log_access(
        db=db,
                *** End Patch
