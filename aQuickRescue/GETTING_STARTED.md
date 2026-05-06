# 🚀 aQuickRescue - Getting Started & Deployment Guide

## 📋 Quick Navigation

- [Local Development Setup](#local-development-setup)
- [Running the Application](#running-the-application)
- [Understanding the Architecture](#understanding-the-architecture)
- [Speckit Standards Compliance](#speckit-standards-compliance)
- [Testing & Quality](#testing--quality)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## 🛠️ Local Development Setup

### Prerequisites

- **macOS/Linux**: bash, git, docker, docker-compose
- **Windows**: WSL2, bash, git, docker-desktop, docker-compose
- **Python**: 3.11+ (if running without Docker)
- **Node.js**: 18+ (for frontend development)

### 1. Clone & Setup Repository

```bash
# Clone the repository
git clone https://github.com/yourorg/aQuickRescue.git
cd aQuickRescue

# Create .env from template
cp .env.example .env

# Update environment variables (IMPORTANT for security!)
nano .env  # or use your preferred editor
# Change SECRET_KEY, DATABASE_URL, FHIR_BASE_URL to production values
```

### 2. Option A: Docker Setup (Recommended)

```bash
# Start all services
docker-compose up -d

# Wait 30 seconds for services to initialize
sleep 30

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f backend-api

# Run tests
docker-compose exec backend-api pytest

# Access services
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - FHIR: http://localhost:8080/fhir
# - Database UI: http://localhost:8081
```

### 3. Option B: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
export DATABASE_URL="postgresql://user:password@localhost/aQuickRescue_db"
export FHIR_BASE_URL="http://localhost:8080/fhir"
export SECRET_KEY="your-secret-key-here"

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm start

# App opens at http://localhost:3000
```

---

## ▶️ Running the Application

### Using Docker Compose (All-in-One)

```bash
# Start everything
docker-compose up -d

# Tail logs from API
docker-compose logs -f backend-api

# Execute commands in containers
docker-compose exec backend-api bash

# Stop everything
docker-compose down
```

### Manual Backend (Development)

```bash
# Terminal 1: Start FastAPI
cd backend
uvicorn app.main:app --reload

# Terminal 2: Database shell
psql -U aquickrescue -d aQuickRescue_db
```

### Testing Emergency Access Workflow

```bash
# 1. Login as first responder (in API docs or with curl)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "responder_alice",
    "password": "password123"
  }'
# Returns: {"access_token": "...", "token_type": "bearer"}

# 2. Search for patient
curl -X GET "http://localhost:8000/api/v1/patients/search?first_name=John&last_name=Doe&date_of_birth=1980-05-20" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Request emergency access
curl -X POST http://localhost:8000/api/v1/emergency-access \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "Patient-12345",
    "reason": "Patient unconscious - checking allergies",
    "requested_data": ["Allergies", "Medications"]
  }'

# 4. View audit trail
curl -X GET http://localhost:8000/api/v1/audit-trail \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🏗️ Understanding the Architecture

### System Components

```
┌──────────────────────────────┐
│   Mobile App (React Native)  │
│ (Patient, First Responder)   │
└──────────────┬───────────────┘
               │ HTTPS + OAuth2
┌──────────────▼───────────────┐
│    FastAPI Backend (8000)    │
│  - Auth Service              │
│  - Patient Service           │
│  - Emergency Access Service  │
│  - Audit Service             │
└──────────────┬───────────────┘
       ┌───────┼───────┐
       │       │       │
┌──────▼──┐ ┌──▼──────┐ ┌─────▼──────┐
│ Postgres │ │ FHIR   │ │  Audit Log │
│(5432)   │ │Server  │ │   Database │
│         │ │(8080)  │ │            │
└─────────┘ └────────┘ └────────────┘
```

### Data Flow

```
Patient Application:
1. User logs in (OAuth2)
2. Enables emergency access (backend stores flag)

First Responder Application:
1. First responder logs in
2. Searches patient by name + DOB
   → System logs: PATIENT_SEARCH audit event
3. Clicks "Emergency Access"
4. Enters reason
   → System validates emergency access is enabled
   → System logs: EMERGENCY_ACCESS_GRANTED audit event
   → System retrieves allergies & medications from FHIR
   → System returns data to responder
5. Responder sees critical health information
   → Patient receives real-time notification (async)

Audit Trail:
Every access logged to audit_logs table with:
- WHO: Responder ID, Name
- WHAT: Patient ID, Data retrieved
- WHEN: Timestamp
- WHERE: IP, GPS location
- WHY: Access reason
```

---

## ✅ Speckit Standards Compliance

### Code Quality

```bash
# Run linting
docker-compose exec backend-api flake8 app/
docker-compose exec backend-api black --check app/

# Fix formatting
docker-compose exec backend-api black app/

# Type checking
docker-compose exec backend-api mypy app/ --strict

# Security check
docker-compose exec backend-api bandit -r app/
```

### Testing

```bash
# Run all tests with coverage
docker-compose exec backend-api pytest \
  --cov=app \
  --cov-report=html \
  --cov-report=term-missing

# View coverage report
open htmlcov/index.html

# Run specific test
docker-compose exec backend-api pytest tests/test_main.py::TestEmergencyAccess -v

# Run with verbose output
docker-compose exec backend-api pytest -v -s
```

### Performance

```bash
# Load test with locust
pip install locust
locust -f backend/tests/locustfile.py --host=http://localhost:8000

# Or with k6
k6 run backend/tests/load-test.js
```

---

## 🧪 Testing & Quality

### Test Coverage Requirements (Speckit)

| Component | Target | Current |
|-----------|--------|---------|
| Unit Tests | >= 80% | [run tests] |
| API Endpoints | >= 75% | [run tests] |
| Critical Paths | 100% | [manual review] |
| Integration | >= 60% | [run tests] |

### Running Tests

```bash
# All tests
pytest

# Specific test class
pytest tests/test_main.py::TestEmergencyAccess

# Specific test
pytest tests/test_main.py::TestEmergencyAccess::test_emergency_access_logs_audit_event

# With output
pytest -v -s

# With coverage
pytest --cov=app --cov-report=html

# In CI/CD pipeline
pytest --cov=app --cov-report=xml  # Uploads to codecov
```

### Quality Metrics

```bash
# SonarQube analysis (local)
pip install sonarqube-api

# Generate reports
pytest --cov=app --cov-report=xml
flake8 app/ --format=json > flake8-report.json
```

---

## 🚀 Deployment

### Production Checklist

- [ ] All tests passing (coverage >= 80%)
- [ ] Linting passes (no warnings)
- [ ] Security audit completed (no critical CVEs)
- [ ] Performance tested (load test 1000 concurrent)
- [ ] HIPAA compliance verified
- [ ] Database backups configured
- [ ] Monitoring/alerting setup
- [ ] Documentation complete
- [ ] Team trained on runbooks

### Environment Variables (Production)

```bash
# Database (AWS RDS PostgreSQL)
DATABASE_URL=postgresql://prod_user:SECURE_PASSWORD@prod-db.aws.amazon.com:5432/aquickrescue_prod

# Security
SECRET_KEY=very_long_secure_random_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# FHIR Server (can be managed service)
FHIR_BASE_URL=https://fhir.example.com

# CORS
CORS_ORIGINS=https://app.example.com,https://admin.example.com

# Monitoring
SENTRY_DSN=https://key@sentry.io/project-id
LOG_LEVEL=INFO  # Not DEBUG in production!
```

### Docker Deployment

```bash
# Build image
docker build -t aquickrescue:latest backend/

# Tag for registry
docker tag aquickrescue:latest your-registry/aquickrescue:latest

# Push to registry
docker push your-registry/aquickrescue:latest

# Deploy to Kubernetes (example)
kubectl apply -f backend/k8s/deployment.yaml
```

### AWS Deployment (Example)

```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ECR_REGISTRY

docker push YOUR_ECR_REGISTRY/aquickrescue:latest

# Deploy to ECS/Fargate
aws ecs update-service \
  --cluster aquickrescue-prod \
  --service aquickrescue-api \
  --force-new-deployment
```

---

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Connect directly
psql -h localhost -U aquickrescue -d aquickrescue_db

# If connection refused:
# 1. Wait longer for container startup (30 seconds)
# 2. Check port 5432 isn't already in use
# 3. Restart: docker-compose down -v && docker-compose up -d
```

### API Not Responding

```bash
# Check if container is running
docker-compose ps backend-api

# View logs
docker-compose logs backend-api

# Check port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Restart API
docker-compose restart backend-api
```

###  Tests Failing

```bash
# Ensure database is clean
docker-compose down -v
docker-compose up -d

# Run tests with verbose output
pytest -v -s tests/

# Run specific failing test
pytest tests/test_main.py::TestEmergencyAccess::test_name -v

# Check logs during test
docker-compose logs -f backend-api
```

### FHIR Server Connection Failed

```bash
# Test FHIR server health
curl http://localhost:8080/fhir/metadata

# Check FHIR logs
docker-compose logs fhir-server

# Verify connection string in .env
echo $FHIR_BASE_URL
```

---

## 📈 Monitoring & Logging

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend-api backend-api

# Last 50 lines
docker-compose logs --tail=50 backend-api

# Since specific time
docker-compose logs --since 30m backend-api
```

### Structured Logging

Backend logs are JSON-formatted for ELK/Datadog:

```json
{
  "timestamp": "2026-05-06T14:32:45Z",
  "level": "INFO",
  "event": "patient_data_access",
  "user_id": 123,
  "patient_id": 456,
  "action": "EMERGENCY_ACCESS_GRANTED",
  "status": "SUCCESS"
}
```

### Metrics

```bash
# Access Prometheus metrics
curl http://localhost:9090

# Query example
# Total API requests: rate(http_requests_total[5m])
# Error rate: rate(http_requests_failed[5m])
# Response time: histogram_quantile(0.95, http_request_duration_seconds)
```

---

## 🔄 Development Workflow

### Creating a Feature

```bash
# 1. Create feature branch
git checkout -b feature/patient-notifications

# 2. Make changes
# Edit app/services/notification.py
# Add tests in tests/test_notifications.py

# 3. Run quality checks
docker-compose exec backend-api bash -c "
  black app/ &&
  flake8 app/ &&
  pytest --cov=app tests/
"

# 4. Commit with descriptive message
git add app/ tests/
git commit -m "Add patient notifications for emergency access (fixes #123)"

# 5. Push and open PR
git push origin feature/patient-notifications
# Open PR on GitHub
```

### Code Review Checklist

- [ ] Tests passing (coverage >= 80%)
- [ ] Code style follows Speckit standards
- [ ] Security implications considered
- [ ] Performance impact acceptable
- [ ] Documentation updated
- [ ] No hardcoded secrets or PII

---

## 📞 Support & Documentation

| Resource | Link |
|----------|------|
| Technical Specification | [SPECIFICATION.md](./SPECIFICATION.md) |
| Architecture Decisions | [docs/architecture.md](./docs/architecture.md) |
| API Documentation | http://localhost:8000/docs |
| HIPAA Compliance | [docs/hipaa-checklist.md](./docs/hipaa-checklist.md) |
| Security Guide | [docs/security.md](./docs/security.md) |

---

## ✨ Next Steps

1. **Local Development**: Follow Option A or B above
2. **Run Tests**: `docker-compose exec backend-api pytest --cov`
3. **Explore API**: Open http://localhost:8000/docs
4. **Try Features**: Use curl commands above to test workflows
5. **Contribute**: Create PR following development workflow

---

**Version**: 0.1.0  
**Last Updated**: 2026-05-06  
**Speckit Framework**: ✅ Compliant (Code Quality, Testing, UX, Performance)

🎉 Welcome to aQuickRescue!

