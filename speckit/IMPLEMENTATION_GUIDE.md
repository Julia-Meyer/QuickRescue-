# Speckit Implementation Guide
## Setting Up Standards in Your Project

This guide walks you through implementing Speckit standards in your project.

## 🚀 Phase 1: Foundation Setup (Week 1)

### Step 1: Choose Your Stack

Identify your primary technology stack:
- **Python**: Django, FastAPI, Flask
- **JavaScript**: React, Vue, Angular
- **Java**: Spring Boot, Quarkus
- **Go**: Gin, Echo
- **Other**: Include relevant frameworks

### Step 2: Code Quality Tools

#### Python Projects
```bash
# Installation
pip install black flake8 pylint isort autopep8

# Create .flake8 config
[flake8]
max-line-length = 100
exclude = .venv,venv,__pycache__

# Create pyproject.toml for Black
[tool.black]
line-length = 100

# Create .pylintrc
# Run: pylint --generate-rcfile > .pylintrc

# Pre-commit hook
pip install pre-commit

# Create .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

#### JavaScript/TypeScript Projects
```bash
# Installation
npm install --save-dev eslint prettier
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin

# Create .eslintrc.json
{
  "env": { "browser": true, "es2021": true, "node": true },
  "extends": ["eslint:recommended"],
  "parser": "@typescript-eslint/parser",
  "rules": {
    "no-unused-vars": "error",
    "no-console": "warn"
  }
}

# Create .prettierrc
{
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100
}

# Add to package.json
"scripts": {
  "lint": "eslint src/**/*.{js,ts,jsx,tsx}",
  "format": "prettier --write src/**/*.{js,ts,jsx,tsx}",
  "lint:fix": "eslint --fix src/**/*.{js,ts,jsx,tsx}"
}
```

### Step 3: Testing Infrastructure

#### Python (pytest)
```bash
# Installation
pip install pytest pytest-cov pytest-xdist

# Create pytest.ini
[pytest]
testpaths = tests
addopts = -v --cov=src --cov-report=html --tb=short
python_files = test_*.py

# Create conftest.py
import pytest

@pytest.fixture
def sample_data():
    return {"id": 1, "name": "Test"}

# Create tests/test_example.py
def test_addition():
    assert 1 + 1 == 2

# Run with coverage
pytest --cov=src --cov-report=html
```

#### JavaScript (Jest)
```bash
# Installation
npm install --save-dev jest @testing-library/react

# Create jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  collectCoverageFrom: ['src/**/*.{js,jsx,ts,tsx}'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};

# Create src/__tests__/example.test.js
describe('Calculator', () => {
  test('adds 1 + 1 to equal 2', () => {
    expect(1 + 1).toBe(2);
  });
});

# Add to package.json
"scripts": {
  "test": "jest",
  "test:watch": "jest --watch",
  "test:coverage": "jest --coverage"
}
```

### Step 4: Git Configuration

```bash
# .gitignore essentials
# Dependencies
node_modules/
venv/
.venv/
__pycache__/
*.pyc

# Build outputs
dist/
build/
.next/

# IDE
.vscode/
.idea/
*.swp

# Environment
.env
.env.local

# Coverage
coverage/
htmlcov/

# OS
.DS_Store
Thumbs.db
```

---

## 🔧 Phase 2: Enhancement Setup (Week 2)

### Step 1: CI/CD Configuration

#### GitHub Actions Setup
```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      
      - name: Lint
        run: |
          black --check .
          flake8 .
      
      - name: Test
        run: |
          pytest --cov=src
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Step 2: Static Analysis

#### SonarQube Setup
```yaml
# .github/workflows/sonarqube.yml
name: SonarQube

on: [push, pull_request]

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### Step 3: Security Scanning

```bash
# Install Snyk
npm install -g snyk

# Create .snyk file
snyk auth

# Add to CI/CD
snyk test --severity-threshold=high
```

### Step 4: Performance Monitoring

```yaml
# .github/workflows/performance.yml
name: Performance Check

on: [pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build
        run: npm run build
      
      - name: Lighthouse Check
        uses: treosh/lighthouse-ci-action@v10
        with:
          uploadArtifacts: true
          temporaryPublicStorage: true
```

---

## 📊 Phase 3: Monitoring & Measurement (Ongoing)

### Step 1: Create Measurement Dashboard

```python
# scripts/metrics.py
import json
from pathlib import Path
from datetime import datetime

class MetricsTracker:
    def __init__(self, metrics_file='metrics.json'):
        self.metrics_file = metrics_file
        self.metrics = self.load_metrics()
    
    def load_metrics(self):
        if Path(self.metrics_file).exists():
            with open(self.metrics_file) as f:
                return json.load(f)
        return {}
    
    def record_metric(self, name, value):
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            'value': value,
            'timestamp': datetime.now().isoformat()
        })
        
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def get_average(self, name, days=30):
        if name not in self.metrics:
            return None
        
        values = [m['value'] for m in self.metrics[name]]
        return sum(values) / len(values) if values else None

# Usage
tracker = MetricsTracker()
tracker.record_metric('test_coverage', 0.85)
tracker.record_metric('build_time', 45.2)
```

### Step 2: Regular Reviews

#### Weekly Review Template
```markdown
# Weekly Metrics Review - [Date]

## Code Quality
- [ ] SonarQube Score: ___/100
- [ ] Coverage: ___%
- [ ] Linting Issues: ___

## Performance
- [ ] Page Load Time (FCP): ___ms
- [ ] API Response Time: ___ms
- [ ] Build Time: ___s

## Testing
- [ ] Test Pass Rate: ___%
- [ ] Flaky Tests: ___
- [ ] New Tests Added: ___

## Security
- [ ] Critical Vulnerabilities: ___
- [ ] High Vulnerabilities: ___
- [ ] Security Scan Status: ___

## Trends & Actions
- [ ] Trend up/down/stable
- [ ] Action items for next week
- [ ] Blockers
```

---

## 🎓 Training & Onboarding

### New Developer Checklist
```bash
# Day 1: Setup
- [ ] Clone repository
- [ ] Install dependencies: pip install -r requirements-dev.txt
- [ ] Run tests: pytest
- [ ] Run linter: black . && flake8 .

# Day 2: Learning
- [ ] Read CONSTITUTION.md (Sections 1-4)
- [ ] Read QUICK_REFERENCE.md
- [ ] Review architecture documentation
- [ ] Pair program with team member

# Day 3+: First PR
- [ ] Pick small issue to fix
- [ ] Follow QUICK_REFERENCE.md checklist
- [ ] Submit PR with description
- [ ] Address review feedback
```

---

## 🔍 Compliance Checklist

### Per Repository
- [ ] .gitignore configured
- [ ] .eslintrc/.flake8 configured
- [ ] jest.config.js/pytest.ini configured
- [ ] CI workflow configured
- [ ] CODEOWNERS file created
- [ ] Contributing guidelines added
- [ ] README with setup instructions

### Per Branch
- [ ] Linting passes
- [ ] Tests pass (> 80% coverage)
- [ ] No console.log/debug statements
- [ ] Performance acceptable
- [ ] Security check passes
- [ ] Documentation updated

### Per Release
- [ ] Changelog updated
- [ ] Version bumped (semantic versioning)
- [ ] Documentation complete
- [ ] Performance baseline established
- [ ] Rollback procedure tested

---

## 📞 Common Issues & Solutions

### Issue: Tests are slow
**Solution:**
```python
# Run tests in parallel
pytest -n auto

# Run only modified tests
pytest --lf

# Use faster fixtures
@pytest.fixture(scope="session")
def expensive_fixture():
    return create_expensive_object()
```

### Issue: Coverage not meeting threshold
**Solution:**
```bash
# Find uncovered lines
pytest --cov --cov-report=html
# Open htmlcov/index.html to visualize

# Add missing tests for critical paths
pytest -v --cov --cov-report=term-missing
```

### Issue: CI/CD pipeline too slow
**Solution:**
```yaml
# Use caching
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

# Run jobs in parallel
jobs:
  lint:
    runs-on: ubuntu-latest
  test:
    runs-on: ubuntu-latest
  build:
    runs-on: ubuntu-latest
```

---

## 🚀 Next Steps

1. **Customize for your project** - Adapt configurations to your tech stack
2. **Get team buy-in** - Present Speckit standards to team
3. **Incremental adoption** - Implement Phase 1, then Phase 2, then Phase 3
4. **Continuous improvement** - Review quarterly and update standards
5. **Celebrate wins** - Recognize improvements in metrics and quality

---

**Created**: 2026-05-06  
**Version**: 1.0  
**Maintained by**: Architecture Team

