@echo off
REM 翻译任务帕累托前沿分析（增强版）运行脚本

echo ========================================
echo 翻译任务帕累托前沿分析（增强版）
echo ========================================
echo.

REM 激活conda环境
call conda activate bartscore

REM 设置UTF-8编码
set PYTHONUTF8=1

REM 运行分析脚本
python analysis/qe_research/scripts/pareto_analysis_translation_enhanced.py

echo.
echo ========================================
echo 分析完成！
echo ========================================
echo.
echo 输出目录: analysis/qe_research/results/pareto_analysis/translation/
echo.

pause
