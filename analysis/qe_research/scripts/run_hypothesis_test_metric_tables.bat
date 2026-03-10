@echo off
chcp 65001 > nul
echo ================================================================================
echo GPU能耗模型间差异假设检验分析
echo ================================================================================
echo.

cd /d "%~dp0..\..\..\"

echo 激活conda环境...
call conda activate bartscore
if errorlevel 1 (
    echo 错误: 无法激活conda环境 bartscore
    pause
    exit /b 1
)

echo.
echo 运行假设检验分析...
python analysis/qe_research/scripts/hypothesis_test_metric_tables.py

if errorlevel 1 (
    echo.
    echo 错误: 分析执行失败
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo 分析完成!
echo ================================================================================
echo.
echo 结果位置:
echo   - 表格: analysis/qe_research/results/raw_analysis/tables/
echo   - 图表: analysis/qe_research/results/raw_analysis/figures/
echo   - 报告: analysis/qe_research/results/raw_analysis/reports/GPU_ENERGY_MODEL_HYPOTHESIS_TESTING_REPORT.md
echo.
pause
