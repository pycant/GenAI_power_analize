@echo off
echo ========================================
echo 质量数据分析
echo ========================================
echo.

REM 激活conda环境
call conda activate bartscore

REM 设置UTF-8编码
set PYTHONUTF8=1

REM 运行分析
python analysis/qe_research/scripts/quality_data_analyzer.py

echo.
echo 分析完成!
pause
