@echo off
:: =============================================================================
:: run_colorize_client_GUI.cmd   :   CMNET2 Colorize Client GUI launcher (Windows)
::
:: Usage:
::   run_colorize_client_GUI.cmd
::
:: Edit the USER CONFIGURATION block below before first use.
:: =============================================================================

:: ---------------------------------------------------------------------------
:: USER CONFIGURATION  :  adjust these variables to match your setup
:: ---------------------------------------------------------------------------

:: Explicit path to python.exe  :  leave empty to auto-detect
:: Example: set PYTHON_EXE=C:\DiTServerRPC\.venv\Scripts\python.exe
set PYTHON_EXE=

:: ---------------------------------------------------------------------------
:: RESOLVE PATHS
:: ---------------------------------------------------------------------------

:: Determine the GUI directory (where this script lives)
set GUI_DIR=%~dp0
:: Remove trailing backslash
if "%GUI_DIR:~-1%"=="\" set GUI_DIR=%GUI_DIR:~0,-1%

:: The project root is one level above GUI/
set PROJECT_DIR=%GUI_DIR%\..
pushd "%PROJECT_DIR%"
set PROJECT_DIR=%CD%
popd

set CLIENT_SCRIPT=%GUI_DIR%\CMNET2_colorize_client_GUI.py

if not exist "%CLIENT_SCRIPT%" (
    echo [ERROR] File CMNET2_colorize_client_GUI.py not found in: %GUI_DIR%
    pause
    exit /b 1
)

:: ---------------------------------------------------------------------------
:: RESOLVE PYTHON EXECUTABLE
:: ---------------------------------------------------------------------------
if not "%PYTHON_EXE%"=="" goto :run

:: 1) Local .venv in the project root (shared with the DiT server)
if exist "%PROJECT_DIR%\.venv\Scripts\python.exe" (
    set PYTHON_EXE=%PROJECT_DIR%\.venv\Scripts\python.exe
    goto :run
)

:: 2) Fallback: use python from PATH
set PYTHON_EXE=python

:run
:: ---------------------------------------------------------------------------
:: LAUNCH
:: ---------------------------------------------------------------------------
echo ============================================================
echo  CMNET2 Colorize Client GUI
echo  Script dir : %GUI_DIR%
echo  Python     : %PYTHON_EXE%
echo ============================================================
echo.

"%PYTHON_EXE%" "%CLIENT_SCRIPT%"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] GUI exited with code %errorlevel%.
    pause
)