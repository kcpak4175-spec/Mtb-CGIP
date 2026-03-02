@echo off
chcp 65001 >nul
TITLE Mtb-Inhibitor Finder AI - 초기 환경 셋업
echo ==========================================
echo   Mtb-Inhibitor Finder AI 초기 환경 세팅
echo ==========================================
echo.
echo 이 작업은 서비스 실행에 필요한 Python 라이브러리를 설치합니다.
echo 인터넷 연결 상태를 확인해 주세요.
echo.

:: Python 설치 여부 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않거나 PATH에 등록되지 않았습니다.
    echo https://www.python.org 에서 Python 3.10 이상을 설치해 주세요.
    pause
    exit /b
)

echo [1/2] 최신 pip으로 업데이트 중...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [Warning] pip 업데이트 실패. 계속 진행합니다.
)

echo.
echo [2/2] 필요한 라이브러리 일괄 설치 중...
echo (chemprop 1.6.1, numpy 1.26.4, rdkit 등)
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [오류] 라이브러리 설치 중 문제가 발생했습니다.
    echo 인터넷 연결을 확인하거나, 관리자 권한으로 다시 실행해 보세요.
    pause
    exit /b
)

echo.
echo [점검] 설치된 주요 라이브러리 확인...
echo.
python -m pip list | findstr "fastapi uvicorn pandas rdkit torch chemprop numpy"

echo.
echo ==========================================
echo   모든 환경 셋업이 완료되었습니다!
echo   이제 'Mtb-Inhibitor Finder AI.bat'을 실행하세요.
echo ==========================================
echo.
pause
