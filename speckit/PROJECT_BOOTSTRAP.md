# Speckit Project Bootstrap Checklist
## New Project Setup Template

Use this checklist when starting a new project to ensure all Speckit standards are in place from day one.

---

## 📋 Pre-Project Planning

- [ ] Project name and repository created
- [ ] Technology stack confirmed with team
- [ ] Team members assigned
- [ ] Development environment specified (Python 3.11+, Node 18+, etc.)
- [ ] Project timeline and milestones defined
- [ ] Speckit standards assigned (all sections apply)

---

## 🏗️ Repository Setup

### Basic Configuration
- [ ] `.gitignore` created and configured
- [ ] `README.md` with project description, setup, and architecture
- [ ] `LICENSE` file added
- [ ] `CODEOWNERS` file with team assignments
- [ ] `CONTRIBUTING.md` with guidelines

### Branch Strategy
- [ ] `main` branch protected with require PRs
- [ ] `develop` branch created
- [ ] Branch naming convention documented
- [ ] CI/CD status checks required

---

## 🧹 Code Quality Setup

### Linting & Formatting

**Python:**
- [ ] `requirements.txt` or `pyproject.toml` created
- [ ] `requirements-dev.txt` with dev tools (black, flake8, pytest)
- [ ] `.flake8` configuration file
- [ ] `pyproject.toml` with Black config
- [ ] `pre-commit` hooks configured
- [ ] `.pre-commit-config.yaml` in repository

**JavaScript/TypeScript:**
- [ ] `package.json` with proper metadata
- [ ] `.eslintrc.json` configured
- [ ] `.prettierrc` configured
- [ ] `tsconfig.json` if using TypeScript
- [ ] npm scripts for lint, format, test added
- [ ] `.npmrc` with registry and settings

**Other Languages:**
- [ ] Language-specific linter configured
- [ ] Style guide enforced via tooling
- [ ] Pre-commit hooks enabled

### Code Quality Gates
- [ ] SonarQube project created (if applicable)
- [ ] Code quality threshold set (≥80 score)
- [ ] Complexity limits configured
- [ ] Duplication detection enabled

---

## 🧪 Testing Infrastructure

### Test Framework Setup

**Python (pytest):**
- [ ] `pytest.ini` configured with test paths
- [ ] `pytest-cov` added to dev requirements
- [ ] Coverage threshold set to 80%
- [ ] Coverage report generation configured (HTML, XML)
- [ ] Test fixtures created in `conftest.py`
- [ ] `tests/` directory structure created

**JavaScript (Jest):**
- [ ] `jest.config.js` created
- [ ] Test environment configured (jsdom/node)
- [ ] Coverage collection configured
- [ ] Coverage thresholds set
- [ ] Test utilities setup
- [ ] `__tests__/` or `.test.js` files organized

### Testing Practices
- [ ] Example unit test created (shows proper structure)
- [ ] Example integration test created
- [ ] Mocking strategy documented
- [ ] Test data fixtures prepared
- [ ] Test naming convention established

---

## 📊 CI/CD Pipeline

### GitHub Actions (or equivalent)

#### Workflow Files Created:
- [ ] `.github/workflows/lint.yml` - Linting check
- [ ] `.github/workflows/test.yml` - Test execution
- [ ] `.github/workflows/build.yml` - Build process
- [ ] `.github/workflows/coverage.yml` - Coverage reporting
- [ ] `.github/workflows/security.yml` - Security scanning

#### Pipeline Configuration:
- [ ] Triggers configured (push, PR)
- [ ] Node/Python version specified
- [ ] Dependency caching configured
- [ ] Artifacts uploaded (coverage, build)
- [ ] Status checks required for PR
- [ ] Coverage reports visible in PRs

### Status Checks Required:
- [ ] Linting
- [ ] Tests (must pass)
- [ ] Coverage (≥80%)
- [ ] Security scan
- [ ] Build success

---

## 🔒 Security Setup

### Dependency Management
- [ ] Dependency file locked (`package-lock.json`, `poetry.lock`, `requirements.lock`)
- [ ] Snyk account created
- [ ] Snyk configured in CI/CD
- [ ] `.snyk` policy file created
- [ ] Scheduled dependency update checks set

### Secrets & Environment
- [ ] `.env.example` created (no real secrets)
- [ ] Environment variables documented
- [ ] GitHub Secrets/repository settings configured
- [ ] No hardcoded credentials in code
- [ ] API keys and tokens properly managed

### Security Headers & Configuration
- [ ] CORS configured appropriately
- [ ] Security headers set
- [ ] Input validation prepared
- [ ] SQL injection prevention documented
- [ ] XSS protection configured (if applicable)

---

## 📈 Performance Setup

### Performance Monitoring
- [ ] Baseline performance metrics documented
- [ ] Performance budget defined:
  - [ ] Bundle size limit
  - [ ] API response time SLA
  - [ ] Page load time targets
  - [ ] Database query limits
- [ ] APM (Application Performance Monitoring) configured (optional for MVP)

### Build Optimization
- [ ] Code splitting strategy planned
- [ ] Bundle analysis configured
- [ ] Asset optimization configured (images, fonts)
- [ ] Caching strategies defined
- [ ] Monitoring targets set

---

## 📚 Documentation

### Code Documentation
- [ ] Docstring template created
- [ ] Architecture Decision Records (ADRs) directory setup
- [ ] API documentation template (if API project)
- [ ] README with:
  - [ ] Project description
  - [ ] Setup instructions
  - [ ] Running the application
  - [ ] Running tests
  - [ ] Contributing guidelines
  - [ ] Architecture overview
  - [ ] API endpoints (if applicable)
  - [ ] Troubleshooting

### Project Documentation
- [ ] `/docs` folder created
- [ ] Architecture diagram added
- [ ] System design document
- [ ] Database schema documented
- [ ] API specification (OpenAPI/Swagger if applicable)

---

## 🎨 Frontend Setup (If Applicable)

### Design System
- [ ] Design system/component library identified
- [ ] Design tokens configured
- [ ] Component storybook setup (optional but recommended)
- [ ] Accessibility audit performed
- [ ] WCAG 2.1 AA compliance verified

### UI/UX Standards
- [ ] Common components created
- [ ] Color palette documented
- [ ] Typography system defined
- [ ] Layout breakpoints defined
- [ ] Responsive design tested

---

## 🗄️ Backend Setup (If Applicable)

### API Design
- [ ] API specifications defined (REST/GraphQL)
- [ ] Endpoint documentation created
- [ ] Error response format standardized
- [ ] Authentication method chosen (OAuth, JWT, etc.)
- [ ] Authorization scheme (RBAC/ABAC) decided

### Database
- [ ] Database technology chosen
- [ ] Schema designed and documented
- [ ] Indexes planned
- [ ] Backup and recovery strategy defined
- [ ] Migration strategy (if applicable)

### Server Configuration
- [ ] Environment variables documented
- [ ] Logging configuration
- [ ] Error tracking setup (Sentry, etc.)
- [ ] Rate limiting configured
- [ ] Monitoring configured

---

## 📋 Initial Code Examples

### Create Example Files

**Python Example (`src/example.py`):**
```python
"""
Example module demonstrating code standards.

This module shows proper structure, naming, and documentation.
"""

def calculate_total(items: list[float], discount: float = 0) -> float:
    """
    Calculate total with optional discount.
    
    Args:
        items: List of item prices
        discount: Discount as decimal (0-1)
    
    Returns:
        Total price after discount
        
    Example:
        >>> calculate_total([10, 20, 30], 0.1)
        54.0
    """
    subtotal = sum(items)
    return subtotal * (1 - discount)


if __name__ == "__main__":
    print(calculate_total([10, 20, 30], 0.1))
```

**Test Example (`tests/test_example.py`):**
```python
import pytest
from src.example import calculate_total


def test_calculate_total_without_discount():
    """Test total calculation without discount."""
    result = calculate_total([10, 20, 30])
    assert result == 60.0


def test_calculate_total_with_discount():
    """Test total calculation with discount."""
    result = calculate_total([10, 20, 30], 0.1)
    assert result == 54.0


def test_calculate_total_empty_list():
    """Test total calculation with empty items list."""
    result = calculate_total([])
    assert result == 0.0
```

---

## ✅ Team Onboarding

### For Each Team Member:
- [ ] Add to GitHub repository
- [ ] Install development environment
- [ ] Clone repository and verify build
- [ ] Run tests locally
- [ ] Read README thoroughly
- [ ] Review CONSTITUTION.md (Sections 1-4)
- [ ] Review QUICK_REFERENCE.md
- [ ] Pair program on first task
- [ ] Make first PR following standards

---

## 🚀 Launch Checklist

### Pre-Launch Review:
- [ ] All linting passes
- [ ] Test coverage ≥ 80%
- [ ] No security vulnerabilities
- [ ] Performance targets met
- [ ] Documentation complete
- [ ] CI/CD pipeline green
- [ ] Team has signed off on standards adoption

### Launch Actions:
- [ ] Create release tag
- [ ] Update CHANGELOG
- [ ] Notify stakeholders
- [ ] Setup monitoring/alerting
- [ ] Establish status dashboard
- [ ] Schedule retrospective

---

## 📊 Setup Verification

Run these commands to verify setup:

```bash
# Verify linting
npm run lint          # or: black --check . && flake8 .

# Verify tests
npm test              # or: pytest

# Verify coverage
npm run test:coverage # or: pytest --cov

# Verify build
npm run build         # or: python -m py_compile src/

# Display coverage report
pytest --cov --cov-report=html
open htmlcov/index.html
```

**All checks should pass before moving forward.**

---

## 📝 Sign-Off

When setup is complete, team lead should confirm:

- [ ] All checklist items completed
- [ ] Team trained on standards
- [ ] CI/CD validated
- [ ] First PR review process validated
- [ ] Project ready for development

**Project Setup Completed By**: _______________  
**Date**: _______________  
**Team Lead Approval**: _______________  

---

**Template Version**: 1.0  
**Created**: 2026-05-06  
**Based on**: Speckit Constitution v1.0

---

## 📞 Support

Questions during setup? Check:
1. README.md in this speckit folder
2. QUICK_REFERENCE.md for common issues
3. IMPLEMENTATION_GUIDE.md for detailed steps
4. Ask architecture team for tech-specific questions

