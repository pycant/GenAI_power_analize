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
call conda activate base

REM 设置UTF-8编码
set PYTHONUTF8=1

REM 运行分析

python analysis\qe_research\scripts\pareto_analysis_code.py
python analysis\qe_research\scripts\pareto_analysis_creative.py
python analysis\qe_research\scripts\pareto_analysis_math.py
python analysis\qe_research\scripts\pareto_analysis_qa.py
python analysis\qe_research\scripts\pareto_analysis_reasoning.py
python analysis\qe_research\scripts\pareto_analysis_summary.py
python analysis\qe_research\scripts\pareto_analysis_translation.py

echo.
echo ========================================
echo 分析完成！
echo 查看结果：../results/pareto_analysis/%TASK%/
echo ========================================

pause
