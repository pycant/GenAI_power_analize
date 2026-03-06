@echo off
REM 生成任务-模型透视表
REM 6个CSV文件：GPU能耗、token数量、TTFT、回答时间、显存占用、GPU占用

echo ================================================================================
echo 任务-模型透视表生成
echo ================================================================================
echo.

REM 激活conda环境
call conda activate bartscore

REM 设置UTF-8编码
set PYTHONUTF8=1

REM 运行脚本
python analysis/qe_research/scripts/create_pivot_tables.py

echo.
echo ================================================================================
echo 完成！查看结果：
echo   - 表格: analysis/qe_research/results/pivot_tables/
echo   - 报告: analysis/qe_research/results/pivot_tables/pivot_tables_summary.md
echo ================================================================================
echo.

pause
