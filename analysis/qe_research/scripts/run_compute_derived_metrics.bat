@echo off
REM 计算派生指标
REM 从基础指标表格计算派生指标：token速度、能效比等

echo ================================================================================
echo 计算派生指标
echo ================================================================================
echo.

REM 设置UTF-8编码
set PYTHONUTF8=1

REM 激活conda环境
call conda activate bartscore

REM 运行脚本
python analysis/qe_research/scripts/compute_derived_metrics.py

echo.
echo ================================================================================
echo 完成！
echo 输出目录: analysis/qe_research/results/derived_metrics/
echo ================================================================================
echo.

pause
