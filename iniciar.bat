@echo off
cd /d "%~dp0"
if not exist frontend\dist\index.html (
  where npm >nul 2>nul
  if errorlevel 1 (
    echo Instale Node 22 ou superior para compilar a interface na primeira execucao.
    exit /b 1
  )
  call npm --prefix frontend ci
  if errorlevel 1 exit /b 1
  call npm run build
  if errorlevel 1 exit /b 1
)
if not exist .venv\Scripts\python.exe (
  python -m venv .venv
  if errorlevel 1 exit /b 1
)
.venv\Scripts\python.exe -m pip install -r requirements-verificado.txt
if errorlevel 1 exit /b 1
echo Abra http://localhost:8000. Para encerrar: Ctrl+C.
.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
