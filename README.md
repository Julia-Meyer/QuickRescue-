# 🏥 aQuickRescue
## Emergency Health Data Access Application

![Status](https://img.shields.io/badge/Status-Under%20Development-yellow)
![Speckit Compliant](https://img.shields.io/badge/Speckit-Compliant-blue)
![License](https://img.shields.io/badge/License-Proprietary-red)
![HIPAA Ready](https://img.shields.io/badge/HIPAA-Ready-brightgreen)

---

## 📖 Overview

**aQuickRescue** is a FHIR-compliant, secure emergency health data mobile application that enables rapid access to critical patient information during life-threatening medical emergencies.

**Vision**: In a medical emergency, first responders should have 30-second access to a patient's critical health data (allergies, current medications, emergency contacts) with full audit logging and patient consent.

### Problem Statement
- ⏱️ First responders spend critical minutes locating patient health data
- ⚠️ Allergies and medication interactions are missed
- 📋 No audit trail of emergency access
- 🔒 Privacy concerns about unauthorized data sharing

### Solution
- **Smart Patient Search**: Find patients by name + DOB in < 2 seconds
- **One-Click Emergency Access**: Retrieve critical data in < 5 seconds
- **Automatic Audit Logging**: Every access logged for compliance
- **Patient Control**: Patients enable/disable emergency access
- **Real-Time Notifications**: Patients notified when data is accessed

---

## 🏗️ Project Structure

```
QuickRescue-/
├── backend/                    # Python FastAPI backend
│   ├── app/                   # Application code
│   │   ├── config/            # Configuration (LOINC, SNOMED)
│   │   ├── services/          # FHIR services
│   │   └── utils/             # Utilities
│   ├── database/              # Schema files
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   └── init_db.py             # Database initialization
├── frontend/                  # Vite + Vanilla JS frontend
│   ├── src/                   # Frontend source code
│   ├── package.json          # Node.js dependencies
│   └── vite.config.js        # Vite configuration
├── shared/                    # Shared utilities and types
├── aQuickRescue/              # Legacy configuration files and docs
├── speckit/                   # Speckit compliance materials
├── docker-compose.yml         # Docker services
├── pytest.ini                 # Python testing config
├── package.json               # Root npm configuration
└── setup.sh / setup.ps1       # Setup scripts
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** >= 18.0.0
- **Python** >= 3.11
- **npm** >= 9.0.0

### Installation

#### 1. Clone and Install Dependencies

**Windows (PowerShell):**
```powershell
cd QuickRescue-
.\setup.ps1
```

**Linux/macOS (Bash):**
```bash
cd QuickRescue-
chmod +x setup.sh
./setup.sh
```

#### 2. Manual Installation (if scripts fail)

```bash
# Install Node dependencies
npm install
npm install --workspace=frontend
npm install --workspace=shared

# Install Python dependencies
pip install -r backend/requirements.txt
```

### Running the Application

#### Start Frontend (Dev Server)
```bash
npm run dev --workspace=frontend
# Opens http://localhost:5173
```

#### Start Backend (in another terminal)
```bash
cd backend
python -m uvicorn app.main:app --reload
# API available at http://localhost:8000
```

#### Docker Setup
```bash
docker-compose up -d
```

---

## 📊 Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLite
- **API Standards**: FHIR (Fast Healthcare Interoperability Resources)
- **Authentication**: OAuth2 / JWT
- **Security**: SSL/TLS, Encryption, Rate Limiting
- **Monitoring**: Prometheus, Sentry

### Frontend
- **Framework**: Vite + Vanilla JavaScript
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Database**: sql.js (SQLite in browser)
- **Quality**: ESLint, Prettier, Vitest

### Infrastructure
- **Containerization**: Docker
- **Pre-commit Hooks**: Black, Flake8, isort, mypy, Bandit
- **Testing**: pytest, vitest
- **Compliance**: Speckit Phase 1

---

## 🔐 Security & Compliance

- ✅ **HIPAA Compliance**: Healthcare data protection standards
- ✅ **FHIR Standard**: Healthcare data interoperability
- ✅ **Audit Logging**: Complete access trail
- ✅ **Encryption**: Data in transit and at rest
- ✅ **Authentication**: Secure OAuth2/JWT
- ✅ **Pre-commit Checks**: Security scanning with Bandit

---

## 📚 Documentation

- **Backend**: See `/backend/README.md`
- **Frontend**: See `/frontend/README.md`
- **FHIR Integration**: See `/aQuickRescue/FHIR_INTEGRATION_GUIDE.md`
- **Database Schema**: See `/backend/database/schema.sql`
- **Speckit Compliance**: See `/speckit/`

---

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend/app

# Run specific test file
pytest backend/tests/test_fhir_integration.py -v
```

### Frontend Tests
```bash
# Run tests
npm test --workspace=frontend

# With coverage
npm run test:coverage --workspace=frontend

# UI mode
npm run test:ui --workspace=frontend
```

### Linting & Code Quality
```bash
# Format code
npm run format
black backend/

# Lint
npm run lint
flake8 backend/

# Type checking
mypy backend/app

# Security scan
bandit -r backend/

# Pre-commit checks
pre-commit run --all-files
```

---

## 👥 Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Responder | responder1 | password123 |
| Patient | patient1 | password123 |
| Admin | admin1 | password123 |

---

## 📋 API Endpoints

### Core Endpoints
- `GET /api/patients/{id}` - Get patient data
- `GET /api/patients/{id}/allergies` - Get allergies
- `GET /api/patients/{id}/medications` - Get medications
- `GET /api/patients/{id}/observations` - Get observations
- `POST /api/audit/access` - Log access

For full API documentation:
```bash
# Visit: http://localhost:8000/docs (Swagger UI)
```

---

## 🐛 Troubleshooting

### Frontend shows nothing
- [ ] Check if Node.js is installed: `node --version`
- [ ] Reinstall dependencies: `npm install --workspace=frontend`
- [ ] Clear cache: `rm -rf node_modules && npm install`
- [ ] Start dev server: `npm run dev --workspace=frontend`

### Backend won't start
- [ ] Check Python version: `python --version` (needs >= 3.11)
- [ ] Install dependencies: `pip install -r backend/requirements.txt`
- [ ] Check database: `python backend/init_db.py`
- [ ] Start server: `python -m uvicorn app.main:app --reload`

### Database connection issues
- [ ] Verify PostgreSQL is running: `docker-compose up -d`
- [ ] Check .env files for correct credentials
- [ ] Initialize schema: `python backend/init_db.py`

---

## 🔄 Development Workflow

1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Make changes**: Edit code in frontend/ or backend/
3. **Run tests**: `pytest` and `npm test`
4. **Format code**: `npm run format` and `black backend/`
5. **Commit**: Pre-commit hooks will validate automatically
6. **Push**: `git push origin feature/your-feature`
7. **Create PR**: Submit pull request

---

## 📦 Available Scripts

```bash
# Root level
npm run install:all          # Install all dependencies
npm run dev                  # Start frontend dev server
npm run build               # Build all packages
npm run test                # Run all tests
npm run lint                # Lint code
npm run lint:fix            # Fix linting issues
npm run format              # Format code
npm run backend:requirements # Install backend deps
npm run backend:test        # Run backend tests

# Frontend specific
npm run dev --workspace=frontend      # Dev server
npm run build --workspace=frontend    # Build
npm test --workspace=frontend         # Tests
npm run lint --workspace=frontend     # Lint
npm run lint:fix --workspace=frontend # Fix lint issues
npm run format --workspace=frontend   # Format

# Backend specific (from backend/ directory)
python -m uvicorn app.main:app --reload  # Dev server
pytest                                   # Tests
black .                                  # Format
flake8 .                                 # Lint
mypy app                                 # Type check
```

---

## 🤝 Contributing

1. Follow the coding standards (ESLint, Black, Flake8)
2. Write tests for new features
3. Update documentation
4. Ensure all tests pass
5. Submit pull request

---

## 📝 License

Proprietary - All rights reserved

---

## 📞 Support

For issues or questions:
1. Check existing documentation in `/aQuickRescue/`
2. Review API docs at `http://localhost:8000/docs`
3. Check test files for usage examples

---

**Last Updated**: 2024
**Status**: Under Development
**Speckit Version**: Phase 1 Compliant

