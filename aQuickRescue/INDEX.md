# 📑 aQuickRescue Documentation Index

This folder contains important configuration files, compliance materials, and reference documentation for the aQuickRescue project.

## 🔍 Quick Navigation

### 🚀 Getting Started
**Start here**: See `/README.md` at the project root for:
- Installation instructions
- Quick start guide
- API endpoints
- Troubleshooting

### 📚 Active Documentation
- **`SPECIFICATION.md`** - Complete project specification and requirements
- **`FHIR_INTEGRATION_GUIDE.md`** - FHIR standard integration details
- **`FHIR_IMPLEMENTATION_REPORT.md`** - Implementation status and standards compliance
- **`SNOMED_CT_IMPROVEMENTS.md`** - SNOMED CT coding system improvements
- **`SPECKIT_PHASE1_STATUS.md`** - Speckit compliance status and metrics

### ⚙️ Configuration Files
- **`.flake8`** - Python linting configuration
- **`.bandit`** - Security testing configuration
- **`.pre-commit-config.yaml`** - Git pre-commit hooks
- **`.env`** - Environment variables (keep private!)
- **`env/`** - Environment configuration examples

### 📊 Diagrams & Architecture
- **`diagrams/`** - UML and architecture diagrams:
  - `activity_diagram.puml` - Activity flows
  - `class_diagram.puml` - Class structures
  - `component_diagram.puml` - System components
  - `sequence_diagram.puml` - API sequences
  - `state_diagram.puml` - State machines
  - `use_case_diagram.puml` - Use cases

### 🔐 Compliance & Security
- **`.github/`** - GitHub Actions CI/CD workflows

### 📦 Backend Code
See `/backend/` for:
- FastAPI application code
- FHIR service implementations
- Database schemas
- Python tests
- Requirements and dependencies

### 🎨 Frontend Code
See `/frontend/` for:
- Vite application code
- JavaScript/HTML templates
- Frontend tests
- npm dependencies

### 🔄 Build & Setup
See root level for:
- `package.json` - Root npm configuration
- `pytest.ini` - Python testing configuration
- `docker-compose.yml` - Docker services
- `Dockerfile` - Container image
- `setup.sh` - Linux/macOS setup script
- `setup.ps1` - Windows PowerShell setup script

---

## 📦 Archived Documentation

Old or historical documents have been moved to `_ARCHIVE/` to keep this folder clean:
- Historical implementation reports
- Completion status documents
- Database setup guides (superseded by code)
- Legacy task lists
- Analysis documents

These may be useful for reference but are not part of the active development workflow.

---

## 🔗 Related Folders

- **`/speckit/`** - Speckit compliance framework and documentation
- **`/backend/`** - Python backend application
- **`/frontend/`** - JavaScript frontend application
- **`/shared/`** - Shared utilities and types

---

## 📝 How to Use This Folder

1. **For project overview**: Read `SPECIFICATION.md`
2. **For FHIR compliance**: Check `FHIR_INTEGRATION_GUIDE.md`
3. **For architecture**: See `diagrams/` folder
4. **For compliance status**: See `SPECKIT_PHASE1_STATUS.md`
5. **For security**: Review `.bandit` configuration

---

**Last Updated**: 2024
**Current Status**: Phase 1 - Speckit Compliant

