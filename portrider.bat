@echo off
chcp 65001

:: 检查是否安装了sshtunnel
python -c "import sshtunnel" 2>nul
if %errorlevel% neq 0 (
    echo 缺少依赖，正在安装...
    echo 默认通过清华源安装...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if %errorlevel% neq 0 (
        echo 依赖安装失败，请检查网络或requirements.txt文件。
        pause
        exit /b 1
    )
) else (
    echo 依赖已满足，跳过安装步骤....
)

:: 运行主程序
python main.py
pause
