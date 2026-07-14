# 启动脚本（Windows）
@echo off
echo ============================================
echo    HoloOrb Backend - Development Server
echo ============================================
echo.

REM 创建虚拟环境（如果不存在）
if not exist "venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
)

REM 激活虚拟环境
echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

REM 安装依赖
echo [3/3] Installing dependencies...
pip install -r requirements.txt

REM 启动服务
echo.
echo Starting HoloOrb API server on http://localhost:5000 ...
python app.py

pause
