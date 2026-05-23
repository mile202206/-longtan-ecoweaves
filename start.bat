@echo off
chcp 65001 >nul
title 龙潭EcoWeaves - 屏南非遗数字化平台

echo.
echo   ╔══════════════════════════════════════════╗
echo   ║     龙潭EcoWeaves - 屏南非遗数字化平台     ║
echo   ║        Longtan Village EcoWeaves          ║
echo   ╚══════════════════════════════════════════╝
echo.

:: ==============================
:: 1. 检测 Python
:: ==============================
set PYTHON=
for %%p in (python python3 py) do (
    where %%p >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON=%%p"
        goto :found_python
    )
)
:: py launcher 特殊处理
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON=py -3"
    goto :found_python
)

:: WorkBuddy 托管 Python (这台电脑)
set "WB_PYTHON=%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
if exist "%WB_PYTHON%" (
    set "PYTHON=%WB_PYTHON%"
    goto :found_python
)

:: WorkBuddy 托管 Python (备选路径)
set "WB_PYTHON2=%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe"
if exist "%WB_PYTHON2%" (
    set "PYTHON=%WB_PYTHON2%"
    goto :found_python
)

echo [错误] 未检测到 Python！请先安装 Python 3。
echo        下载地址: https://www.python.org/downloads/
echo        安装时务必勾选 "Add Python to PATH"
echo.
pause
exit /b 1

:found_python
%PYTHON% --version >nul 2>&1
echo [检测] Python 路径: %PYTHON%

:: ==============================
:: 2. 检查/安装依赖
:: ==============================
echo [检查] 正在检查依赖包...
%PYTHON% -c "import flask; import waitress" >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装依赖包 (flask + waitress)...
    %PYTHON% -m pip install flask waitress -q
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
%PYTHON% -m waitress --host=0.0.0.0 --port=5000 app:app

pause
