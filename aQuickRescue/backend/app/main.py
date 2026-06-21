"""aQuickRescue - Emergency Health Data Backend API"""
import os, logging
from datetime import datetime, timedelta, date
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Date, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "aQuickRescue.db")

# Die Datenbank immer an diesem festen Ort erstellen/suchen
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True) if "sqlite" in DATABASE_URL else create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    patients = relationship("PatientProfile", back_populates="owner")
    emergency_access = relationship("EmergencyAccess", back_populates="responder")
    audit_events = relationship("AuditLog", back_populates="user")
class PatientProfile(Base):
    __tablename__ = "patient_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    fhir_patient_id = Column(String, unique=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    date_of_birth = Column(Date)
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    emergency_access_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("User", back_populates="patients")
    emergency_accesses = relationship("EmergencyAccess", back_populates="patient")
class EmergencyAccess(Base):
    __tablename__ = "emergency_access"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), index=True)
    responder_id = Column(Integer, ForeignKey("users.id"), index=True)
    reason = Column(Text)
    gps_location = Column(String, nullable=True)
    accessed_at = Column(DateTime, default=datetime.utcnow)
    data_requested = Column(String)
    status = Column(String, default="GRANTED")
    ip_address = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    patient = relationship("PatientProfile", back_populates="emergency_accesses")
    responder = relationship("User", back_populates="emergency_access")
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), nullable=True)
    action = Column(String)
    resource_type = Column(String)
    resource_id = Column(String)
    reason = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address = Column(String, nullable=True)
    gps_location = Column(String, nullable=True)
    status = Column(String)
    error_message = Column(String, nullable=True)
    user = relationship("User", back_populates="audit_events")

class AccessLog(Base):
    __tablename__ = "access_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    resource_type = Column(String)
    resource_id = Column(String)
    access_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    access_duration = Column(Integer, nullable=True)

class RolePermission(Base):
    __tablename__ = "role_permissions"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, index=True)
    resource_type = Column(String)
    action = Column(String)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables created successfully")
except Exception as e:
    logger.error(f"✗ Error creating database tables: {e}")
class UserLogin(BaseModel):
    username: str
    password: str
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
security = HTTPBearer()
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def verify_token(token: str, db: Session) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    return user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    return verify_token(credentials.credentials, db)
class AuditService:
    @staticmethod
    def log_access(db: Session, user_id: int, patient_id: Optional[int], action: str, resource_type: str,
                   resource_id: str, reason: str, ip_address: str = "127.0.0.1", status: str = "SUCCESS",
                   error_message: Optional[str] = None, gps_location: Optional[str] = None):
        try:
            audit_entry = AuditLog(user_id=user_id, patient_id=patient_id, action=action, resource_type=resource_type,
                                  resource_id=resource_id, reason=reason, ip_address=ip_address, status=status,
                                  error_message=error_message, gps_location=gps_location, timestamp=datetime.utcnow())
            db.add(audit_entry)
            db.commit()
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            try:
                db.rollback()
            except:
                pass
app = FastAPI(title="aQuickRescue API", description="Emergency Health Data Access API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:5173",
        "http://localhost:5173",
        "https://127.0.0.1:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error(f"Unexpected error: {type(exc).__name__} - {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "SERVER_001", "message": "An unexpected error occurred", "status": 500})
@app.get("/health")
async def health_check():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(status_code=503, content={"status": "unhealthy", "database": "disconnected", "error": str(e), "timestamp": datetime.utcnow().isoformat()})
@app.get("/api/v1/health")
async def api_health_check():
    return {"status": "running", "version": "0.1.0", "timestamp": datetime.utcnow().isoformat()}
@app.post("/api/v1/auth/login")
def login(request: UserLogin, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == request.username).first()
        if not user or not verify_password(request.password, user.hashed_password):
            logger.warning(f"Failed login attempt: {request.username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token({"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer", "user": {"id": user.id, "username": user.username, "role": user.role}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("aQuickRescue API Starting...")
    logger.info(f"Database: {DATABASE_URL}")
    logger.info("=" * 60)
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        logger.info("✓ Database connection successful")

        # --- TEST-USER AUTOMATISCH ANLEGEN ---
        # Prüfen, ob admin1 bereits existiert
        admin_exists = db.query(User).filter(User.username == "admin1").first()
        if not admin_exists:
            logger.info("ℹ No admin user found. Creating initial 'admin1' account...")
            test_admin = User(
                username="admin1",
                email="admin@aquickrescue.de",
                role="admin",
                hashed_password=hash_password("123456"),  # Dein Testpasswort
                is_active=True
            )
            db.add(test_admin)
            db.commit()
            logger.info("✓ Initial admin user 'admin1' created successfully (Password: 123456)")
        # --------------------------------------

        db.close()
    except Exception as e:
        logger.error(f"✗ Database startup configuration failed: {e}")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
