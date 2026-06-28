@echo off
REM ============================================================
REM  Dr. Phil's Quant Lab - Options Pricer  (one-click launcher)
REM  Double-click this file to start the app in your browser.
REM
REM  Uses Python 3.12 on purpose: the pinned dependencies
REM  (numpy<2.3 etc., required by vnstock) ship prebuilt wheels
REM  for 3.12 but NOT for 3.13/3.14, which would force a slow
REM  source build that needs a C/Visual Studio compiler.
REM ============================================================
setlocal
cd /d "%~dp0"

REM --- require Python 3.12 ---
py -3.12 --version >nul 2>&1
if errorlevel 1 (
  echo [error] Python 3.12 was not found via the "py" launcher.
  echo         This app needs Python 3.12 ^(newer 3.13/3.14 have no
  echo         prebuilt packages for the pinned dependencies yet^).
  echo         Get it here: https://www.python.org/downloads/release/python-31210/
  echo.
  pause
  exit /b 1
)

REM --- decide whether the environment needs (re)building ---
set "NEED_SETUP="
if not exist ".venv\Scripts\python.exe" set "NEED_SETUP=1"
if not defined NEED_SETUP (
  ".venv\Scripts\python.exe" -c "import streamlit, numpy, vnstock" >nul 2>&1 || set "NEED_SETUP=1"
)

if defined NEED_SETUP (
  if exist ".venv" rmdir /s /q ".venv"
  echo [setup] Creating Python 3.12 environment and installing
  echo         dependencies ^(first run only, a few minutes^)...
  py -3.12 -m venv .venv
  call ".venv\Scripts\activate.bat"
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  if errorlevel 1 (
    echo [error] Dependency install failed. See the messages above.
    pause
    exit /b 1
  )
) else (
  call ".venv\Scripts\activate.bat"
)

REM --- skip Streamlit's first-run "Email:" onboarding prompt ---
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
  if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"
  > "%USERPROFILE%\.streamlit\credentials.toml" echo [general]
  >> "%USERPROFILE%\.streamlit\credentials.toml" echo email = ""
)

echo.
echo [run] Launching Quant Lab... your browser will open at http://localhost:8501
echo       Keep this window open while using the app; press Ctrl+C to stop.
echo.
streamlit run main.py

endlocal
