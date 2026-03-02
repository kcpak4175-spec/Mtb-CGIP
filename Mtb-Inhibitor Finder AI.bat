@echo off
:: 한글 깨짐 방지
chcp 65001 >nul
TITLE Mtb-Inhibitor Finder AI Server
echo ==========================================
echo   Mtb-Inhibitor Finder AI Service Starting
echo ==========================================
echo.
cd /d "%~dp0"

:: 8000번 포트를 사용 중인 기존 프로세스가 있다면 종료 (중복 실행 방지)
echo 기존 실행 중인 서버 프로세스 확인 및 정리 중...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a 2>nul

echo AI 모델 로딩 및 서버 시작 중...
echo 약 7초 후 브라우저가 자동으로 실행됩니다.
echo.

:: 브라우저 자동 실행 (서버가 열릴 때까지 대기)
start /b cmd /c "for /l %%i in (1,1,30) do (timeout /t 1 >nul & netstat -an | find "8000" | find "LISTENING" >nul && start http://localhost:8000 && exit)"

:: 서버 실행 (Mtb_Inhibitor_Web/backend 디렉토리의 main.py 실행)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --app-dir Mtb_Inhibitor_Web/backend

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] 서버가 정상적으로 시작되지 않았습니다. 의존성을 확인해 주세요.
    pause
)
