@echo off
echo ================================================================================
echo 原始数据(raw.json)深度分析
echo ================================================================================
echo.

REM 激活conda环境
call conda activate bartscore

REM 设置UTF-8编码
set PYTHONUTF8=1

REM 运行分析脚本
python analysis/qe_research/scripts/raw_data_analyzer_complete.py

echo.
echo ================================================================================
echo 分析完成!
echo 报告位置: analysis/qe_research/results/raw_analysis/reports/raw_analysis_report.md
echo 图表位置: analysis/qe_research/results/raw_analysis/figures/
echo ================================================================================
pause
