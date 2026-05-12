@echo off
:: =============================================================================
:: run_client_example.cmd  —  DiT Colorize RPC Client example launcher (Windows)
::
:: The client connects to a running dit_rpc_server instance and colorizes
:: assets\santa_bw.png, saving the result as assets\santa_colorized.png.
:: The pipeline must already be loaded on the server.
::
:: Edit the USER CONFIGURATION block below before first use.
:: =============================================================================

:: ---------------------------------------------------------------------------
:: USER CONFIGURATION — adjust these variables to match your setup
:: ---------------------------------------------------------------------------

:: Conda environment name (used when PYTHON_EXE is not set)
set CONDA_ENV=dit-colorize

:: Explicit path to python.exe — leave empty to use the conda environment above
:: Example: set PYTHON_EXE=C:\Users\YourName\.conda\envs\dit-colorize\python.exe
set PYTHON_EXE=

:: Directory containing dit_client_example.py
:: Leave empty to use the directory of this script
set CLIENT_DIR=

:: Server host and port — must match the running dit_rpc_server instance
set HOST=127.0.0.1
set PORT=8765

:: Text prompt sent to the colorization model
set PROMPT=Colorize this photo, natural skin tones, vibrant environment. Maintain consistency and details.

:: Maximum long side in pixels before inference (0 = keep original size)
set IMG_SIZE=0

:: Number of inference steps
set STEPS=2

:: Use shared memory transport instead of PNG bytes (same-host only, lower latency)
:: Set to 1 to enable, 0 to use standard RPC
set USE_SHM=0

:: ---------------------------------------------------------------------------
:: RESOLVE PATHS
:: ---------------------------------------------------------------------------
if "%CLIENT_DIR%"=="" set CLIENT_DIR=%~dp0
if "%CLIENT_DIR:~-1%"=="\" set CLIENT_DIR=%CLIENT_DIR:~0,-1%

set CLIENT_SCRIPT=%CLIENT_DIR%\dit_client_example.py

if not exist "%CLIENT_SCRIPT%" (
    echo [ERROR] dit_client_example.py not found in: %CLIENT_DIR%
    echo         Set CLIENT_DIR to the correct directory.
    pause
    exit /b 1
)

:: ---------------------------------------------------------------------------
:: RESOLVE PYTHON EXECUTABLE
:: ---------------------------------------------------------------------------
if not "%PYTHON_EXE%"=="" goto :run

where conda >nul 2>&1
if %errorlevel%==0 (
    echo [INFO] Activating conda environment: %CONDA_ENV%
    call conda activate %CONDA_ENV% 2>nul
    if %errorlevel%==0 (
        set PYTHON_EXE=python
        goto :run
    )
    echo [WARN] conda activate failed — trying base python
)

set PYTHON_EXE=python

:run
:: ---------------------------------------------------------------------------
:: LAUNCH
:: ---------------------------------------------------------------------------
echo ============================================================
echo  DiT Colorize RPC Client — example
echo  Server      : %HOST%:%PORT%
echo  Transport   : %USE_SHM% (0=RPC 1=shared memory)
echo  Input       : %CLIENT_DIR%\assets\santa_bw.png
echo  Output      : %CLIENT_DIR%\assets\santa_colorized.png
echo ============================================================
echo.

if "%USE_SHM%"=="1" (
    "%PYTHON_EXE%" "%CLIENT_SCRIPT%" --host %HOST% --port %PORT% --prompt "%PROMPT%" --img-size %IMG_SIZE% --steps %STEPS% --use-shm
) else (
    "%PYTHON_EXE%" "%CLIENT_SCRIPT%" --host %HOST% --port %PORT% --prompt "%PROMPT%" --img-size %IMG_SIZE% --steps %STEPS%
)

echo.
if %errorlevel%==0 (
    echo [DONE] Colorization complete.
) else (
    echo [ERROR] Client exited with code %errorlevel%.
)
pause

