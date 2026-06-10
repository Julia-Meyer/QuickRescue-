#!/bin/bash
# Speckit Phase 1 Setup Script for aQuickRescue
# Version: 1.0
# This script sets up all Speckit Phase 1 requirements

set -e  # Exit on error

echo " Starting Speckit Phase 1 Setup for aQuickRescue..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"
if [[ ! "$PYTHON_VERSION" > "3.10" ]]; then
    echo -e "${RED}❌ Python 3.11+ required${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python version OK${NC}"
echo ""

# Install/upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip
echo -e "${GREEN}✅ pip upgraded${NC}"
echo ""

# Install Git pre-commit
echo -e "${BLUE}Installing pre-commit...${NC}"
pip install pre-commit
echo -e "${GREEN}✅ pre-commit installed${NC}"
echo ""

# Install Python dependencies
echo -e "${BLUE}Installing Python dependencies from requirements.txt...${NC}"
pip install -r packages/backend/requirements.txt || pip install -r backend/requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Setup pre-commit hooks
echo -e "${BLUE}Setting up git pre-commit hooks...${NC}"
pre-commit install
echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"
echo ""

# Run pre-commit on all files (first time)
echo -e "${BLUE}Running pre-commit on all files (first time setup)...${NC}"
pre-commit run --all-files || echo -e "${YELLOW}⚠️  Some issues found (see above)${NC}"
echo ""

# Create test directories if they don't exist
echo -e "${BLUE}Setting up test directories...${NC}"
mkdir -p packages/backend/tests backend/tests
echo -e "${GREEN}✅ Test directories ready${NC}"
echo ""

# Verify configuration files
echo -e "${BLUE}Verifying Speckit Phase 1 configuration files...${NC}"

files_to_check=(
    ".flake8"
    ".pre-commit-config.yaml"
    "pytest.ini"
    ".bandit"
    "pyproject.toml"
)

all_files_exist=true
for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file exists${NC}"
    else
        echo -e "${RED}❌ $file missing${NC}"
        all_files_exist=false
    fi
done
echo ""

if [ "$all_files_exist" = false ]; then
    echo -e "${RED}❌ Some configuration files are missing${NC}"
    exit 1
fi

# Run quick verification
echo -e "${BLUE}Verifying tools...${NC}"
echo "Black: $(black --version)"
echo "Flake8: $(flake8 --version | head -n1)"
echo "isort: $(isort --version)"
echo "mypy: $(mypy --version)"
echo "Bandit: $(bandit --version | head -n1)"
echo "Pytest: $(pytest --version | head -n1)"
echo ""

echo -e "${GREEN}✅ All tools verified${NC}"
echo ""

# Summary
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Speckit Phase 1 Setup Complete! ✨${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Read SPECKIT_PHASE1_STATUS.md for details"
echo "2. Run: pytest packages/backend/tests -v --cov"
echo "3. Try pre-commit: pre-commit run --all-files"
echo "4. Make changes and commit (pre-commit will run automatically)"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  black packages/backend/       # Format code"
echo "  isort packages/backend/       # Sort imports"
echo "  flake8 packages/backend/      # Lint"
echo "  mypy packages/backend/app     # Type check"
echo "  bandit -r packages/backend/   # Security scan"
echo "  pytest --cov                  # Run tests with coverage"
echo "  pre-commit run --all-files    # Run pre-commit checks"
echo ""
echo -e "${YELLOW}ℹ️  Git pre-commit hooks are now active!${NC}"
echo "   They will run automatically before each commit."
echo ""
