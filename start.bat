@echo off
echo === 龙潭EcoWeaves - 屏南非遗数字化平台 ===
echo.
echo Starting server at http://localhost:5000
echo Press Ctrl+C to stop
echo.
C:\Users\23938\.workbuddy\binaries\python\envs\default\Scripts\waitress-serve.exe --host=0.0.0.0 --port=5000 app:app
pause
