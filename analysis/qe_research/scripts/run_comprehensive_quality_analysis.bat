@echo off
REM 运行综合质量分析脚本
REM 分析所有任务类型的质量数据并生成报告

echo ========================================
echo 综合质量数据分析
echo ========================================
echo.

REM 激活conda环境
call conda activate bartscore
if errorlevel 1 (
    echo 错误: 无法激活bartscore环境
    pause
    exit /b 1
)

REM 设置UTF-8编码
set PYTHONUTF8=1

REM 运行脚本
python analysis/qe_research/scripts/quality_data_analyzer.py

echo.
echo ========================================
echo 完成！
echo 报告: analysis/qe_research/results/quality_analysis/reports/quality_analysis_report.md
echo 图表: analysis/qe_research/results/quality_analysis/figures/
echo ========================================
pause
