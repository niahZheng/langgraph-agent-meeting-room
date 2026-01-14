@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   多人会议聊天室启动脚本
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [信息] Python环境检查通过
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo [警告] 未找到虚拟环境，正在创建...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo [信息] 虚拟环境创建成功
    echo.
    
    REM 安装依赖
    echo [信息] 正在安装依赖包...
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 安装依赖包失败
        pause
        exit /b 1
    )
    echo [信息] 依赖包安装完成
    echo.
) else (
    REM 检查Streamlit是否已安装
    if not exist "venv\Scripts\streamlit.exe" (
        echo [信息] 正在安装依赖包...
        venv\Scripts\python.exe -m pip install --upgrade pip
        venv\Scripts\python.exe -m pip install -r requirements.txt
        if errorlevel 1 (
            echo [错误] 安装依赖包失败
            pause
            exit /b 1
        )
        echo [信息] 依赖包安装完成
        echo.
    )
)

echo ========================================
echo   启动会议聊天室...
echo ========================================
echo.
echo [提示] 浏览器将自动打开应用
echo [提示] 如果未自动打开，请访问: http://localhost:8501
echo.
echo [提示] 按 Ctrl+C 停止应用
echo.

REM 直接使用虚拟环境中的streamlit.exe
venv\Scripts\streamlit.exe run meeting_app.py

pause
