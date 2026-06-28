@echo off
REM ============================================================
REM  Dr. Phil's Quant Lab - Options Pricer  (one-click launcher)
REM  Double-click this file to start the app in your browser.
REM  First run creates a local virtual env and installs deps
REM  (a few minutes); later runs start instantly.
REM ============================================================
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [setup] Creating local virtual environment ^(first run only^)...
  py -3 -m venv .venv 2>nul || python -m venv .venv
  if errorlevel 1 (
    echo [error] Could not create the virtual environment.
    echo         Make sure Python 3.12+ is installed and on PATH.
    pause
    exit /b 1
  )
  call ".venv\Scripts\activate.bat"
  echo [setup] Upgrading pip...
  python -m pip install --upgrade pip
  echo [setup] Installing dependencies from requirements.txt...
  pip install -r requirements.txt
  if errorlevel 1 (
    echo [error] Dependency install failed. See messages above.
    pause
    exit /b 1
  )
) else (
  call ".venv\Scripts\activate.bat"
)

echo.
echo [run] Launching Quant Lab... your browser will open at http://localhost:8501
echo       Press Ctrl+C in this window to stop the app.
echo.
streamlit run main.py

endlocal
