@echo off
REM 快速运行帕累托前沿分析
REM 使用方法: run_pareto_analysis.bat [task_name]

setlocal

set TASK=%1
if "%TASK%"=="" set TASK=reasoning

echo ========================================
echo 帕累托前沿分析：%TASK%任务
echo ========================================

REM 激活conda环境
call conda activate bartscore

REM 设置UTF-8编码
set PYTHONUTF8=1

REM 运行分析
python pareto_metrics_calculator.py
python pareto_robustness_analyzer.py

echo.
echo ========================================
echo 分析完成！
echo 查看结果：../results/pareto_analysis/%TASK%/
echo ========================================

pause
