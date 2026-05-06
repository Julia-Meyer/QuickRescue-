# 🏗️ Speckit-Compliant Project Structure Template

This document shows how to organize a project according to Speckit standards.

---

## Python Project Structure Example

```
my-project/
├── 📄 README.md                 # Project documentation
├── 📄 CONTRIBUTING.md           # Contribution guidelines
├── 📄 LICENSE                   # License file
├── 📄 CODEOWNERS                # Code ownership
│
├── 📁 .github/
│   └── workflows/
│       ├── lint.yml             # Linting checks
│       ├── test.yml             # Test execution
│       ├── coverage.yml         # Coverage reporting
│       └── security.yml         # Security scanning
│
├── 📁 src/                      # Source code
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── config.py                # Configuration
│   ├── utils.py                 # Utilities
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   └── user_service.py
│   ├── api/                     # API routes (if applicable)
│   │   ├── __init__.py
│   │   └── routes.py
│   └── middleware/              # Middleware (if applicable)
│       ├── __init__.py
│       └── auth.py
│
├── 📁 tests/                    # Test files
│   ├── conftest.py              # Pytest configuration & fixtures
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_utils.py
│   │   └── test_models.py
│   ├── integration/             # Integration tests
│   │   ├── __init__.py
│   │   └── test_services.py
│   └── e2e/                     # End-to-end tests
│       ├── __init__.py
│       └── test_workflows.py
│
├── 📁 docs/                     # Documentation
│   ├── architecture.md          # Architecture decisions
│   ├── api.md                   # API documentation
│   ├── setup.md                 # Setup instructions
│   └── troubleshooting.md       # Troubleshooting guide
│
├── 📁 scripts/                  # Build & utility scripts
│   ├── setup.sh                 # Project setup
│   ├── run_tests.sh             # Test runner
│   └── lint.sh                  # Linting script
│
├── 📄 requirements.txt          # Production dependencies
├── 📄 requirements-dev.txt      # Development dependencies
├── 📄 .flake8                   # Flake8 configuration
├── 📄 .gitignore                # Git ignore rules
├── 📄 .pre-commit-config.yaml   # Pre-commit hooks
├── 📄 pytest.ini                # Pytest configuration
├── 📄 pyproject.toml            # Project metadata & Black config
├── 📄 setup.py                  # Setup configuration
└── 📄 .env.example              # Environment variables template
```

---

## JavaScript/TypeScript Project Structure Example

```
my-webapp/
├── 📄 README.md
├── 📄 CONTRIBUTING.md
├── 📄 LICENSE
├── 📄 CODEOWNERS
│
├── 📁 .github/
│   └── workflows/
│       ├── lint.yml
│       ├── test.yml
│       ├── build.yml
│       └── security.yml
│
├── 📁 src/
│   ├── index.tsx                # Entry point
│   ├── App.tsx                  # Main app component
│   ├── config.ts                # Configuration
│   │
│   ├── components/              # Reusable components
│   │   ├── Button.tsx
│   │   ├── Modal.tsx
│   │   └── Layout.tsx
│   │
│   ├── pages/                   # Page components
│   │   ├── Home.tsx
│   │   ├── Dashboard.tsx
│   │   └── NotFound.tsx
│   │
│   ├── services/                # API services
│   │   ├── api.ts
│   │   ├── auth.service.ts
│   │   └── user.service.ts
│   │
│   ├── hooks/                   # Custom React hooks
│   │   ├── useAuth.ts
│   │   └── useFetch.ts
│   │
│   ├── utils/                   # Utilities
│   │   ├── helpers.ts
│   │   └── validators.ts
│   │
│   ├── context/                 # React context
│   │   └── AuthContext.tsx
│   │
│   ├── types/                   # TypeScript types
│   │   ├── index.ts
│   │   └── api.ts
│   │
│   └── styles/                  # CSS/SCSS
│       ├── global.css
│       └── variables.css
│
├── 📁 __tests__/                # Test files
│   ├── unit/
│   │   ├── helpers.test.ts
│   │   └── validators.test.ts
│   ├── integration/
│   │   └── api.integration.test.ts
│   └── e2e/
│       └── flows.e2e.test.ts
│
├── 📁 public/                   # Static files
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
│
├── 📁 docs/                     # Documentation
│   ├── architecture.md
│   ├── components.md
│   └── setup.md
│
├── 📄 package.json
├── 📄 package-lock.json
├── 📄 tsconfig.json
├── 📄 .eslintrc.json
├── 📄 .prettierrc
├── 📄 jest.config.js
├── 📄 webpack.config.js         # If using Webpack
├── 📄 .gitignore
├── 📄 .env.example
└── 📄 .env.local.example
```

---

## Backend (Node.js/Express) Project Structure

```
my-api/
├── 📄 README.md
├── 📄 CONTRIBUTING.md
├── 📄 LICENSE
│
├── 📁 .github/workflows/        # CI/CD workflows
│
├── 📁 src/
│   ├── index.ts                 # Entry point
│   ├── app.ts                   # Express app
│   ├── config.ts                # Configuration
│   │
│   ├── routes/                  # API routes
│   │   ├── auth.routes.ts
│   │   ├── users.routes.ts
│   │   └── products.routes.ts
│   │
│   ├── controllers/             # Request handlers
│   │   ├── auth.controller.ts
│   │   └── users.controller.ts
│   │
│   ├── services/                # Business logic
│   │   ├── auth.service.ts
│   │   └── users.service.ts
│   │
│   ├── models/                  # Database models
│   │   ├── User.ts
│   │   └── Product.ts
│   │
│   ├── middleware/              # Express middleware
│   │   ├── auth.middleware.ts
│   │   └── errorHandler.ts
│   │
│   ├── utils/                   # Utilities
│   │   ├── logger.ts
│   │   └── validators.ts
│   │
│   ├── types/                   # TypeScript types
│   │   └── index.ts
│   │
│   └── database/                # Database
│       ├── connection.ts
│       └── migrations/
│           └── 001_initial.sql
│
├── 📁 tests/
│   ├── unit/
│   │   └── services.test.ts
│   ├── integration/
│   │   └── api.integration.test.ts
│   └── fixtures/
│       └── test-data.ts
│
├── 📁 docs/
│   ├── api.md                   # API documentation (Swagger)
│   ├── architecture.md
│   └── database-schema.md
│
├── 📄 package.json
├── 📄 package-lock.json
├── 📄 tsconfig.json
├── 📄 .eslintrc.json
├── 📄 .prettierrc
├── 📄 jest.config.js
├── 📄 .env.example
├── 📄 .gitignore
└── 📄 docker-compose.yml        # Local development (optional)
```

---

## Configuration Files Reference

### `.flake8` (Python)
```ini
[flake8]
max-line-length = 100
exclude = .venv,venv,__pycache__,.git
ignore = E203,W503
```

### `.eslintrc.json` (JavaScript)
```json
{
  "env": { "browser": true, "es2021": true, "node": true },
  "extends": ["eslint:recommended"],
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint"],
  "rules": {
    "no-unused-vars": "error",
    "no-console": "warn"
  }
}
```

### `pytest.ini` (Python)
```ini
[pytest]
testpaths = tests
addopts = -v --cov=src --cov-report=html --tb=short
python_files = test_*.py
```

### `jest.config.js` (JavaScript)
```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  collectCoverageFrom: ['src/**/*.{ts,tsx}'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

### `tsconfig.json` (TypeScript)
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "tests"]
}
```

### `.prettierrc` (Code Formatting)
```json
{
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2,
  "semi": true,
  "bracketSpacing": true
}
```

---

## Important Files Explained

### 📄 `.gitignore`
```
# Dependencies
node_modules/
venv/
__pycache__/
*.egg-info/

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

# Tests
coverage/
htmlcov/

# OS
.DS_Store
```

### 📄 `.env.example`
```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# API Keys (example only - never commit real keys)
API_KEY=example_key_here
SECRET_KEY=example_secret_here

# Environment
NODE_ENV=development
DEBUG=false
```

### 📄 `CODEOWNERS`
```
# Code ownership for reviews
* @team-lead @tech-lead
/src/auth/ @security-team
/src/api/ @backend-team
/src/components/ @frontend-team
```

---

## Directory Naming Conventions

| Directory | Usage | Example |
|-----------|-------|---------|
| `src/` | Source code | Application code |
| `tests/` | Test files | Unit, integration, e2e tests |
| `docs/` | Documentation | Architecture, setup guides |
| `.github/` | GitHub-specific | Workflows, issue templates |
| `public/` | Static files | HTML, images, fonts |
| `scripts/` | Utility scripts | Setup, build, deploy |
| `config/` | Configuration | Environment configs |
| `db/` | Database | Migrations, schema |

---

## File Organization Best Practices

✅ **Do:**
- Group files by feature/domain (domain-driven)
- Keep test files close to source code
- Use consistent naming conventions
- Organize by concern (models, services, components)
- Separate concerns (logic vs presentation)

❌ **Don't:**
- Create massive single files
- Mix concerns (business logic in components)
- Use ambiguous directory names
- Create overly nested structures
- Duplicate code across projects

---

## Naming Conventions

### Python
```python
# Variables & functions: snake_case
variable_name = 42
def calculate_total():
    pass

# Classes: PascalCase
class UserService:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
```

### JavaScript/TypeScript
```javascript
// Variables & functions: camelCase
const userName = "John";
function calculateTotal() {}

// Classes & Components: PascalCase
class UserService {}
function UserProfile() {}

// Constants: UPPER_SNAKE_CASE
const MAX_RETRIES = 3;
```

---

## Getting Started with This Template

1. **Copy the relevant structure** - Choose Python, JavaScript, or Backend template
2. **Adjust to your needs** - Add/remove directories as needed
3. **Create configuration files** - Use provided examples
4. **Initialize git** - `git init` and add `.gitignore`
5. **Set up tooling** - Follow IMPLEMENTATION_GUIDE.md
6. **Create documentation** - Fill in placeholder docs
7. **Add team members** - Update CODEOWNERS
8. **First commit** - Structure is ready for development

---

## Monorepo Structure (if applicable)

```
monorepo/
├── packages/
│   ├── shared/                  # Shared utilities
│   │   └── src/
│   ├── api/                     # Backend service
│   │   └── src/
│   ├── web/                     # Frontend application
│   │   └── src/
│   └── cli/                     # Command-line tool
│       └── src/
├── .github/workflows/           # Shared workflows
├── docs/                        # Shared documentation
├── .eslintrc.json               # Shared config
└── package.json                 # Root package.json
```

---

## Project Setup Script (`setup.sh`)

```bash
#!/bin/bash
set -e

echo "🚀 Setting up project..."

# Install dependencies
echo "📦 Installing dependencies..."
npm install  # or: pip install -r requirements.txt

# Setup pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
pre-commit install  # or: npx husky install

# Run initial checks
echo "✅ Running initial checks..."
npm run lint
npm run test

# Setup environment
echo "📋 Setting up environment..."
cp .env.example .env

echo "✨ Setup complete! You're ready to start coding."
echo ""
echo "Next steps:"
echo "  1. Update .env with your configuration"
echo "  2. Review README.md for project details"
echo "  3. Check CONTRIBUTING.md for guidelines"
echo "  4. Run: npm start"
```

---

**Template Version**: 1.0  
**Created**: 2026-05-06  
**Based on**: Speckit Constitution v1.0

For more details, see the main documentation:
- Implementation Guide (tools setup)
- Project Bootstrap (new project checklist)
- Quick Reference (daily development guide)

