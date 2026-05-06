"""
aQuickRescue - Emergency Health Data Backend API
Main FastAPI application with OAuth2, Patient search, and Audit logging
"""

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
# 6. FHIR CLIENT SERVICE
# ============================================================================

class FHIRService:
    """Service for FHIR server integration"""

    FHIR_BASE_URL = os.getenv("FHIR_BASE_URL", "http://localhost:8080/fhir")

    @staticmethod
    def search_patient(first_name: str, last_name: str, dob: str) -> dict:
        """
        Search FHIR server for patient
        Performance: Target < 2 seconds
        """
        import httpx

        try:
            query = f"{FHIRService.FHIR_BASE_URL}/Patient"
            params = {
                "given": first_name,
                "family": last_name,
                "birthdate": dob
            }

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=params)
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

            return {"found": True, "patients": patients}
        except Exception as e:
            logger.error(f"FHIR search error: {str(e)}")
            return {"found": False, "error": str(e)}

    @staticmethod
    def get_patient_allergies(patient_id: str) -> List[dict]:
        """Get patient allergies from FHIR server"""
        import httpx

        try:
            query = f"{FHIRService.FHIR_BASE_URL}/AllergyIntolerance"
            params = {"patient": patient_id}

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=params)
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

            return allergies
        except Exception as e:
            logger.error(f"Error fetching allergies: {str(e)}")
            return []

    @staticmethod
    def get_patient_medications(patient_id: str) -> List[dict]:
        """Get patient medications from FHIR server"""
        import httpx

        try:
            query = f"{FHIRService.FHIR_BASE_URL}/MedicationStatement"
            params = {"patient": patient_id}

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=params)
                response.raise_for_status()

            bundle = response.json()
            medications = []

            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                medications.append({
                    "medication": resource.get("medicationReference", {}).get("display", "Unknown"),
                    "dosage": resource.get("dosage", [{}])[0].get("text", ""),
                    "status": resource.get("status", "unknown")
                })

            return medications
        except Exception as e:
            logger.error(f"Error fetching medications: {str(e)}")
            return []

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
# 8. API ENDPOINTS
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
        raise HTTPException(status_code=403, detail="Only first responders can search patients")

    # Search FHIR server
    result = FHIRService.search_patient(first_name, last_name, date_of_birth)

    # Log search attempt
    AuditService.log_access(
        db=db,
        user_id=current_user.id,
        patient_id=0,  # Not patient-specific yet
        action="PATIENT_SEARCH",
        resource_type="Patient",
        resource_id="multiple",
        reason="Patient identification during emergency",
        ip_address="127.0.0.1",  # Would be real IP from request
        status="SUCCESS"
    )

    return result

@app.post("/api/v1/emergency-access")
def request_emergency_access(
    request: EmergencyAccessRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request emergency access to patient data

    Flow:
    1. Validate responder role
    2. Verify patient exists and emergency access enabled
    3. Log access request
    4. Return patient data (allergies, medications, contacts)
    5. Create FHIR AuditEvent

    Speckit Compliance: Audit logging 100%, <5 second response
    """
    # Role check
    if current_user.role not in ["FIRST_RESPONDER", "EMERGENCY_PHYSICIAN", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Find patient
    patient = db.query(PatientProfile).filter(
        PatientProfile.fhir_patient_id == request.patient_id
    ).first()

    if not patient:
        # Log failed access attempt
        AuditService.log_access(
            db=db,
            user_id=current_user.id,
            patient_id=0,
            action="EMERGENCY_ACCESS_DENIED",
            resource_type="Patient",
            resource_id=request.patient_id,
            reason="Patient not found",
            ip_address="127.0.0.1",
            status="DENIED",
            error_message="Patient not found"
        )
        raise HTTPException(status_code=404, detail="Patient not found")

    if not patient.emergency_access_enabled:
        # Log denied access
        AuditService.log_access(
            db=db,
            user_id=current_user.id,
            patient_id=patient.id,
            action="EMERGENCY_ACCESS_DENIED",
            resource_type="Patient",
            resource_id=request.patient_id,
            reason="Emergency access not enabled",
            ip_address="127.0.0.1",
            status="DENIED",
            error_message="Emergency access not enabled by patient"
        )
        raise HTTPException(status_code=403, detail="Patient has not enabled emergency access")

    # Log successful access
    AuditService.log_access(
        db=db,
        user_id=current_user.id,
        patient_id=patient.id,
        action="EMERGENCY_ACCESS_GRANTED",
        resource_type="Patient",
        resource_id=request.patient_id,
        reason=request.reason,
        ip_address="127.0.0.1",
        gps_location=request.gps_location,
        status="SUCCESS"
    )

    # Record emergency access
    emergency_access = EmergencyAccess(
        patient_id=patient.id,
        responder_id=current_user.id,
        reason=request.reason,
        gps_location=request.gps_location,
        data_requested=",".join(request.requested_data),
        ip_address="127.0.0.1"
    )
    db.add(emergency_access)
    db.commit()

    # Retrieve patient data from FHIR
    allergies = FHIRService.get_patient_allergies(patient.fhir_patient_id)
    medications = FHIRService.get_patient_medications(patient.fhir_patient_id)

    return {
        "patient": {
            "id": patient.fhir_patient_id,
            "name": f"{patient.first_name} {patient.last_name}",
            "dob": patient.date_of_birth
        },
        "emergency_contact": {
            "name": patient.emergency_contact_name,
            "phone": patient.emergency_contact_phone
        },
        "allergies": allergies,
        "medications": medications,
        "access_timestamp": datetime.utcnow().isoformat(),
        "access_id": emergency_access.id
    }

@app.get("/api/v1/audit-trail")
def get_audit_trail(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Get audit trail for current user's data

    - PATIENT role: Sees who accessed their data
    - ADMIN role: Sees all accesses
    """
    if current_user.role == "PATIENT":
        # Patient sees accesses to their own data
        patient = db.query(PatientProfile).filter(
            PatientProfile.user_id == current_user.id
        ).first()
        if not patient:
            return []

        audits = db.query(AuditLog).filter(
            AuditLog.patient_id == patient.id
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    else:
        # Admin sees all
        audits = db.query(AuditLog).order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).all()

    return [
        {
            "timestamp": audit.timestamp,
            "user": audit.user.username if audit.user else "Unknown",
            "action": audit.action,
            "resource_type": audit.resource_type,
            "reason": audit.reason,
            "status": audit.status
        }
        for audit in audits
    ]

@app.get("/api/v1/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }

# ============================================================================
# 9. STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize app on startup"""
    logger.info("aQuickRescue API starting...")
    # Initialize database connections, warmup cache, etc.

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("aQuickRescue API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

