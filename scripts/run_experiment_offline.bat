@echo off
REM 运行实验（离线模式，使用缓存的 BARTScore）
echo 设置离线模式...
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1

echo 激活 conda 环境...
call conda activate bartscore

echo 运行实验...
python experiments/experiment_runner.py --config data/experiments_gemma3/test_cases.json --output-dir data/experiments_gemma3

echo.
echo 实验完成！
pause
