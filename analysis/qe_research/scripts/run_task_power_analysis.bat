@echo off
chcp 65001 > nul
echo ========================================
echo 任务功率曲线分析
echo ========================================
echo.

set PYTHONUTF8=1
python analysis/qe_research/scripts/plot_task_power_curves.py

echo.
echo 按任意键退出...
pause > nul
