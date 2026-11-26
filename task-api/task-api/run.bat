@echo off
setlocal
cd /d "%~dp0"
title Task API

set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

rem ---- 1. Check kung naay Python na ---------------------------------
call :find_python
if defined PY goto have_python

echo [INFO] Wala pa ma-install ang Python. Ginainstall na...

where winget >nul 2>nul
if %errorlevel%==0 (
    winget install --id Python.Python.3.12 --source winget --silent --accept-package-agreements --accept-source-agreements
)
call :find_python
if defined PY goto have_python

rem ---- Fallback: direct download gikan sa python.org ------------------
echo [INFO] Napakyas ang winget. Gidownload direct ang Python installer...
set "INSTALLER=%TEMP%\python-3.12.10-amd64.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe' -OutFile '%INSTALLER%'"
if not exist "%INSTALLER%" (
    echo [ERROR] Napakyas ang download sa Python. Susiha imong internet.
    pause
    exit /b 1
)
"%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
call :find_python
if not defined PY (
    echo [ERROR] Napakyas ang install sa Python.
    pause
    exit /b 1
)

:have_python
echo [OK] Gamit nga Python: %PY%
"%PY%" --version

rem ---- 2. Install dependencies -----------------------------------------
echo.
echo [INFO] Ginainstall ang dependencies...
"%PY%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Napakyas ang pag-install sa requirements.
    pause
    exit /b 1
)

rem ---- 3. Run ang server ----------------------------------------------
echo.
echo [INFO] Nagstart ang server sa http://127.0.0.1:8000/docs
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:8000/docs"
"%PY%" -m uvicorn app.main:app --reload

pause
exit /b 0

rem ---- Helper: pangitaa ang working Python -----------------------------
:find_python
set "PY="
rem Sulayan ang PATH una (dili Microsoft Store stub)
python -c "import sys" >nul 2>nul && set "PY=python"
if not defined PY if exist "%PYEXE%" set "PY=%PYEXE%"
goto :eof
