@echo off

set VENV_NAME="venv_windows"
set PATH_VENV_ACTIVATE_SCRIPT="%~dp0/%VENV_NAME%/Scripts/activate.bat"

REM Validate python 3.8 is installed
echo [INFO] Checking if python-3.8 is installed...
py -3.8 --version >NUL 2>NUL
if errorlevel 1 (
    echo [ERROR] Python 3.8 is not installed. Please go on python.org to install it.
    goto end
)

REM Create virtualenv
if not exist %PATH_VENV_ACTIVATE_SCRIPT% (
    echo [INFO] Creating virtual environment...
    py -3.8 -m venv %VENV_NAME%
)

REM Validate virtualenv
if not exist %PATH_VENV_ACTIVATE_SCRIPT% (
    echo [ERROR] File %PATH_VENV_ACTIVATE_SCRIPT%. don't exist. Please contact support.
    goto end
)

REM Activate virtualenv
echo [INFO] Activate virtual environment...
call %PATH_VENV_ACTIVATE_SCRIPT%
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment. Please contact support.
    goto end
)

REM Install poetry
echo [INFO] Installing poetry...
pip install poetry
if errorlevel 1 (
    echo [ERROR] Failed to install poetry. Please contact support.
    goto end
)

REM Install dependencies
echo [INFO] Installing dependencies...
poetry install --no-dev
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies. Please contact support.
    goto end
)

REM Launch
echo [INFO] Starting application...
python -m csp4cg
if errorlevel 1 (
    echo [ERROR] Failed to start application. Please contact support.
)

:end
pause
