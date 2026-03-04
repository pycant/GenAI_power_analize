@echo off
REM 批量运行所有模型的实验
REM 使用 --skip-bartscore 跳过质量评估，仅收集效率指标

echo ========================================
echo 批量实验执行脚本
echo ========================================
echo.
echo 将依次运行以下模型的实验:
echo   1. gemma3:4b
echo   2. qwen3:4b
echo   3. qwen3:8b
echo   4. deepseek-r1:8b
echo.
echo 每个模型 40 个任务，预计总时间: 4-6 小时
echo.
pause

REM 激活 conda 环境
call conda activate bartscore

REM 1. Gemma3 4B
echo.
echo ========================================
echo [1/4] 运行 Gemma3 4B 实验...
echo ========================================
python experiments/experiment_runner.py --config data/experiments_gemma3/test_cases.json --output-dir data/experiments_gemma3 --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Gemma3 4B 实验失败
    pause
    exit /b 1
)

REM 2. Qwen3 4B
echo.
echo ========================================
echo [2/4] 运行 Qwen3 4B 实验...
echo ========================================
python experiments/experiment_runner.py --config data/experiments_qwen3_4b/test_cases.json --output-dir data/experiments_qwen3_4b --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Qwen3 4B 实验失败
    pause
    exit /b 1
)

REM 3. Qwen3 8B
echo.
echo ========================================
echo [3/4] 运行 Qwen3 8B 实验...
echo ========================================
python experiments/experiment_runner.py --config data/experiments_qwen3_8b/test_cases.json --output-dir data/experiments_qwen3_8b --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Qwen3 8B 实验失败
    pause
    exit /b 1
)

REM 4. DeepSeek-R1 8B
echo.
echo ========================================
echo [4/4] 运行 DeepSeek-R1 8B 实验...
echo ========================================
python experiments/experiment_runner.py --config data/experiments_deepseek_r1_8b/test_cases.json --output-dir data/experiments_deepseek_r1_8b --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] DeepSeek-R1 8B 实验失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 所有实验完成！
echo ========================================
echo.
echo 结果保存在以下目录:
echo   - data/experiments_gemma3/
echo   - data/experiments_qwen3_4b/
echo   - data/experiments_qwen3_8b/
echo   - data/experiments_deepseek_r1_8b/
echo.
pause
