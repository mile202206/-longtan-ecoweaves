@echo off
chcp 65001 >nul
title 龙潭EcoWeaves - 屏南非遗数字化平台

echo.
echo   ╔════════════════════════════════════════╗
echo   ║     龙潭EcoWeaves - 屏南非遗数字化平台     ║
echo   ║        Longtan Village EcoWeaves          ║
echo   ╚════════════════════════════════════════╝
echo.

:: ==============================
:: 1. 设置 Python 路径（写死，避免检测失败）
:: ==============================
set "PYTHON=C:\Users\23938\.workbuddy\binaries\python\versions\3.13.12\python.exe"
if not exist "%PYTHON%" (
    echo [错误] 未找到 Python: %PYTHON%
    echo         请通过 WorkBuddy 安装 Python 3.13+。
    pause
    exit /b 1
)
echo [检测] Python 路径: %PYTHON%

:: ==============================
:: 2. 检查/安装依赖
:: ==============================
echo [检查] 正在检查依赖包...
"%PYTHON%" -c "import flask; import waitress" >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装依赖包 (flask + waitress)...
    "%PYTHON%" -m pip install flask waitress -q
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请检查网络连接后重试。
        pause
        exit /b 1
    )
    echo [完成] 依赖安装成功！
) else (
    echo [完成] 依赖包已就绪。
)

:: ==============================
:: 3. 启动服务器
:: ==============================
echo.
echo   ┌──────────────────────────────────────────┐
echo   │  服务器启动中...                          │
echo   │  访问地址: http://localhost:5000           │
echo   │  按 Ctrl+C 停止服务器                      │
echo   └──────────────────────────────────────────┘
echo.

:: 延迟 2 秒后自动打开浏览器
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000"

:: 启动 waitress 生产服务器
"%PYTHON%" -m waitress --host=0.0.0.0 --port=5000 app:app

pause
