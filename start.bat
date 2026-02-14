@echo off
echo 正在启动手势识别鼠标控制器...
echo.

REM 激活conda环境
call conda activate finger-mouse

REM 检查环境是否激活成功
if errorlevel 1 (
    echo 错误：无法激活finger-mouse环境
    echo 请确保已创建该conda环境
    echo 运行: conda create -n finger-mouse python=3.8
    pause
    exit /b 1
)

REM 运行程序
python main.py

REM 程序结束后暂停
pause
