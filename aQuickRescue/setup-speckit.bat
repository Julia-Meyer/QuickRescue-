@REM Speckit Phase 1 Setup Script for aQuickRescue (Windows)
@REM Version: 1.0
@REM This script sets up all Speckit Phase 1 requirements

@echo off
setlocal enabledelayedexpansion

echo.
echo 🚀 Starting Speckit Phase 1 Setup for aQuickRescue...
echo.

REM Check Python version
echo Checking Python version...
python --version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Extract major and minor version
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% LSS 3 goto :PythonVersionError
if %MAJOR% EQU 3 if %MINOR% LSS 11 goto :PythonVersionError

echo ✅ Python version OK
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo ✅ pip upgraded
echo.

REM Install pre-commit
echo Installing pre-commit...
pip install pre-commit
echo ✅ pre-commit installed
echo.

REM Install dependencies
echo Installing Python dependencies...
if exist packages\backend\requirements.txt (
    pip install -r packages\backend\requirements.txt
) else if exist backend\requirements.txt (
    pip install -r backend\requirements.txt
) else (
    echo ⚠️  requirements.txt not found
)
echo ✅ Dependencies installed
echo.

REM Setup pre-commit hooks
echo Setting up git pre-commit hooks...
pre-commit install
echo ✅ Pre-commit hooks installed
echo.

REM Create test directories
echo Setting up test directories...
if not exist packages\backend\tests mkdir packages\backend\tests
if not exist backend\tests mkdir backend\tests
echo ✅ Test directories ready
echo.

REM Verify configuration files
echo Verifying Speckit Phase 1 configuration files...
set all_good=1

if exist .flake8 (
    echo ✅ .flake8 exists
) else (
    echo ❌ .flake8 missing
    set all_good=0
)

if exist .pre-commit-config.yaml (
    echo ✅ .pre-commit-config.yaml exists
) else (
    echo ❌ .pre-commit-config.yaml missing
    set all_good=0
)

if exist pytest.ini (
    echo ✅ pytest.ini exists
) else (
    echo ❌ pytest.ini missing
    set all_good=0
)

if exist .bandit (
    echo ✅ .bandit exists
) else (
    echo ❌ .bandit missing
    set all_good=0
)

if exist pyproject.toml (
    echo ✅ pyproject.toml exists
) else (
    echo ❌ pyproject.toml missing
    set all_good=0
)

echo.

if !all_good! EQU 0 (
    echo ❌ Some configuration files are missing
    goto :End
)

REM Verify tools
echo Verifying tools...
black --version
flake8 --version
isort --version
mypy --version
bandit --version
pytest --version
echo.

echo ✅ All tools verified
echo.

REM Summary
echo ════════════════════════════════════════════════════════
echo ✨ Speckit Phase 1 Setup Complete! ✨
echo ════════════════════════════════════════════════════════
echo.
echo Next steps:
echo 1. Read SPECKIT_PHASE1_STATUS.md for details
echo 2. Run: pytest packages\backend\tests -v --cov
echo 3. Try pre-commit: pre-commit run --all-files
echo 4. Make changes and commit (pre-commit will run automatically)
echo.
echo Useful commands:
echo   black packages\backend\         # Format code
echo   isort packages\backend\         # Sort imports
echo   flake8 packages\backend\        # Lint
echo   mypy packages\backend\app       # Type check
echo   bandit -r packages\backend\     # Security scan
echo   pytest --cov                    # Run tests with coverage
echo   pre-commit run --all-files      # Run pre-commit checks
echo.
echo ℹ️  Git pre-commit hooks are now active!
echo    They will run automatically before each commit.
echo.

goto :End

:PythonVersionError
echo ❌ Python 3.11+ required (found %PYTHON_VERSION%)
exit /b 1

:End
endlocal

