"""aQuickRescue - Emergency Health Data Backend API"""
import os, logging
from datetime import datetime, timedelta, date
from typing import Optional, List, Any
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import DateTime, Boolean, ForeignKey, Text, Date, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from collections import Counter
import collections

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "aQuickRescue.db")

DATABASE_URL = f"sqlite:///{DB_PATH}"
SQLALCHEMY_DATABASE_URL = DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    allergies = Column(String)  # z.B. "Penicillin, Pollen"
    medications = Column(String)  # z.B. "Ibuprofen 400mg, Metoprolol 50mg"
    conditions = Column(String)  # z.B. "Bluthochdruck, Asthma"
    gp_name = Column(String)  # Name des Hausarztes
    gp_phone = Column(String)  # Telefon Hausarzt
    emergency_contact_phone = Column(String, default="+49 17656781893")
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    fhir_patient_id = Column(String, unique=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    date_of_birth = Column(Date)
    blood_type = Column(String)
    gender = Column(String, nullable=True)
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


@app.get("/api/v1/patients/search")
def search_patients(query: str, db: Session = Depends(get_db)):
    # Falls nach einer ID (Zahl) gesucht wird
    if query.isdigit():
        patient = db.query(PatientProfile).filter(PatientProfile.id == int(query)).all()
        return patient

    # Falls nach Namen gesucht wird (sucht in Vor- und Nachname)
    patients = db.query(PatientProfile).filter(
        (PatientProfile.first_name.ilike(f"%{query}%")) |
        (PatientProfile.last_name.ilike(f"%{query}%"))
    ).all()

    return patients

@app.get("/api/v1/dashboard/data")
async def get_dashboard_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Patientenanzahl
    patient_count = db.query(Patient).count()

    # 2. Letzte 5 Notfallzugriffe (Beispiel-Query)
    recent_access = db.query(EmergencyAccess).order_by(EmergencyAccess.timestamp.desc()).limit(5).all()

    return {
        "total_patients": patient_count,
        "recent_access": [
            {"id": acc.id, "patient_name": acc.patient_name, "time": acc.timestamp}
            for acc in recent_access
        ]
    }
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error(f"Unexpected error: {type(exc).__name__} - {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "SERVER_001", "message": "An unexpected error occurred", "status": 500})
@app.get("/api/v1/logs") # exakt dieser Pfad!
async def get_logs(db: Session = Depends(get_db)):
    # Deine Logik, um die letzten Zugriffe zu holen
    return {"status": "ok", "logs": []}
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

class FrontendLog(BaseModel):
    level: str = "INFO"
    message: str
    timestamp: str = None

# Der fehlende POST-Endpunkt
@app.post("/api/v1/logs")
def receive_frontend_logs(log: FrontendLog):
    # Druckt das Protokoll aus dem Browser direkt in dein Backend-Terminal
    print(f"🖥️ Frontend-Log: {log.message}")
    return {"status": "success", "message": "Log gespeichert"}


from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import Counter


# ... Deine bestehenden Importe (PatientProfile, get_db, etc.) ...

@app.get("/api/v1/dashboard/stats")  # Exakt der Pfad mit /v1/ wie im Frontend!
def get_dashboard_stats(db: Session = Depends(get_db)):
    try:
        patients = db.query(PatientProfile).all()
        total_patients = len(patients)

        # 1. Fehlersicherer Check für Notfallzugriff (fängt enabled vs anabled ab)
        access_enabled = 0
        for p in patients:
            if getattr(p, 'emergency_access_enabled', False) or getattr(p, 'emergency_access_anabled', False):
                access_enabled += 1
        access_disabled = total_patients - access_enabled

        # 2. Fehlersicheres Auswerten der Allergien
        all_allergies = []
        for p in patients:
            # Holt 'allergies' oder alternativ 'allergy', falls es im Modell Einzahl ist
            allergy_data = getattr(p, 'allergies', getattr(p, 'allergy', None))
            if allergy_data and allergy_data != "Keine bekannt":
                all_allergies.extend([a.strip() for a in allergy_data.split(",")])

        top_allergies = Counter(all_allergies).most_common(5)

        # 3. Fehlersicheres Auswerten der Vorerkrankungen
        all_conditions = []
        for p in patients:
            # Holt 'condition' oder alternativ 'conditions'
            condition_data = getattr(p, 'condition', getattr(p, 'conditions', None))
            if condition_data and condition_data != "Keine chronischen Erkrankungen":
                all_conditions.extend([c.strip() for c in condition_data.split(",")])

        top_conditions = Counter(all_conditions).most_common(5)

        # Rückgabe exakt so strukturiert, wie es das Frontend erwartet
        return {
            "summary": {
                "total_patients": total_patients,
                "access_enabled": access_enabled,
                "access_disabled": access_disabled,
            },
            "top_allergies": [{"name": name, "count": count} for name, count in top_allergies],
            "top_conditions": [{"name": name, "count": count} for name, count in top_conditions]
        }

    except Exception as e:
        # Falls irgendwas schiefgeht, sehen wir den Fehler in der Terminal-Konsole
        print(f"🚨 FEHLER IM DASHBOARD-ENDPOINT: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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


# Das Schema (akzeptiert jetzt ID als Zahl ODER Text, um Fehler zu vermeiden)
class EmergencyAccessPayload(BaseModel):
    patient_id: Any
    reason: str


@app.post("/api/v1/emergency-access")
def create_emergency_access(payload: EmergencyAccessPayload, db: Session = Depends(get_db)):
    print(f"--- NOTFALLZUGRIFF GESTARTET FÜR ID: {payload.patient_id} ---")
    print(f"Grund eingegeben: {payload.reason}")

    # 1. Protokollierung in der Datenbank (Sicher verpackt)
    try:
        # HINWEIS: Wenn 'AuditLog' bei dir anders heißt, hier anpassen!
        new_log = AuditLog(
            action="BREAK_THE_GLASS",
            details=f"Notfall-Zugriff auf Patient #{payload.patient_id}. Grund: {payload.reason}",
            timestamp=datetime.utcnow()
        )
        db.add(new_log)
        db.commit()
        print("✅ Audit-Log erfolgreich gespeichert.")
    except Exception as db_err:
        print(f"⚠️ Audit-Log konnte nicht gespeichert werden (Modellname falsch?): {db_err}")
        db.rollback()  # Verhindert, dass die DB blockiert

    # 2. Patienten abrufen
    # HINWEIS: Wenn dein Modell 'Patient' statt 'PatientProfile' heißt, hier anpassen!
    try:
        patient = db.query(PatientProfile).filter(PatientProfile.id == payload.patient_id).first()

        if not patient:
            print(f"❌ Patient mit ID {payload.patient_id} wurde in der DB nicht gefunden.")
            raise HTTPException(status_code=404, detail="Patient nicht gefunden")

        print(f"✅ Patient {patient.first_name} gefunden. Sende Daten an Frontend...")

        # 3. Daten zurückgeben (Achte darauf, dass die Bezeichnungen links zu deiner DB passen!)
        return {
            "status": "success",
            "medical_data": {
                "allergies": getattr(patient, 'allergies', 'Keine bekannten Allergien'),
                "medications": getattr(patient, 'medications', 'Keine Dauermedikation'),
                "conditions": getattr(patient, 'medical_conditions', 'Keine chronischen Vorerkrankungen')
            }
        }

    except Exception as e:
        print(f"💥 Kritischer Fehler im Endpunkt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):  # Passe get_db an dein Setup an
    patients = db.query(PatientProfile).all()
    total_patients = len(patients)

    # 1. Notfallzugriff-Status zählen
    access_enabled = sum(1 for p in patients if p.emergency_access_enabled)
    access_disabled = total_patients - access_enabled

    # 2. Häufigste Allergien auswerten (da sie als Komma-String gespeichert sind)
    all_allergies = []
    for p in patients:
        if p.allergies and p.allergies != "Keine bekannt":
            # Splittet den String auf, falls mehrere Allergien existieren
            all_allergies.extend([a.strip() for a in p.allergies.split(",")])

    allergy_counts = Counter(all_allergies).most_common(5)  # Top 5 Allergien

    # 3. Häufigste Vorerkrankungen auswerten
    all_conditions = []
    for p in patients:
        if p.condition and p.condition != "Keine chronischen Erkrankungen":
            all_conditions.extend([c.strip() for c in p.condition.split(",")])

    condition_counts = Counter(all_conditions).most_common(5)

    return {
        "summary": {
            "total_patients": total_patients,
            "access_enabled": access_enabled,
            "access_disabled": access_disabled,
        },
        "top_allergies": [{"name": name, "count": count} for name, count in allergy_counts],
        "top_conditions": [{"name": name, "count": count} for name, count in condition_counts],
        # Liefert die letzten 5 registrierten Patienten für eine "Recent Activity"-Liste
        "recent_patients": [
            {
                "id": p.id,
                "name": f"{p.first_name} {p.last_name}",
                "created_at": p.created_at.strftime("%d.%m.%Y") if p.created_at else None
            } for p in patients[-5:]
        ]
    }
