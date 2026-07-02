@echo off
REM ------------------------------------------------------------
REM PCIe 5.0 – Chapter 7 Query Tool
REM Double‑click this batch to open the GUI (run_gui.py).
REM ------------------------------------------------------------

cd /d "%~dp0"

REM 检查Python是否存在
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
echo Python not found. Please install Python 3.14 or later.
echo.
echo Required for running the PCIe 5.0 Chapter 7 Query Tool GUI.
echo.
echo Press any key to exit...
pause >nul
exit /b 1
)

REM 设置Python路径以确保使用正确的解释器
set PYTHONPATH=%~dp0

REM 运行GUI助手，导入GUI并捕获错误
echo Running GUI...
python "run_gui.py"
echo GUI finished

echo.
echo GUI has closed. Press any key to exit...
pause
