@echo off
REM 运行质量评分表格生成脚本
REM 生成以模型为列、指标为行的质量评分表格

echo ========================================
echo 质量评分表格生成
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
python analysis/qe_research/scripts/create_quality_score_tables.py

echo.
echo ========================================
echo 完成！
echo 输出目录: analysis/qe_research/results/quality_scores/
echo ========================================
pause
