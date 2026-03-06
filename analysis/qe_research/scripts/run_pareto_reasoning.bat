@echo off
REM Reasoning任务帕累托前沿分析
REM 使用熵权法对人工评分进行加权，分析质量-能耗-速度的帕累托前沿

echo ================================================================================
echo Reasoning任务帕累托前沿分析
echo ================================================================================
echo.

REM 设置UTF-8编码
set PYTHONUTF8=1

REM 激活conda环境
call conda activate bartscore

REM 运行脚本
python analysis/qe_research/scripts/pareto_analysis_reasoning.py

echo.
echo ================================================================================
echo 完成！
echo 输出目录: analysis/qe_research/results/pareto_analysis/reasoning/
echo ================================================================================
echo.

pause
