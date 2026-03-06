@echo off
REM 创建模型性能指标对比表格
REM 生成6个CSV文件：能耗、token数、TTFT、回答时间、显存、GPU占用

echo ================================================================================
echo 创建模型性能指标对比表格
echo ================================================================================
echo.

REM 设置UTF-8编码
set PYTHONUTF8=1

REM 激活conda环境
call conda activate bartscore

REM 运行脚本
python analysis/qe_research/scripts/create_metric_tables.py

echo.
echo ================================================================================
echo 完成！
echo 输出目录: analysis/qe_research/results/metric_tables/
echo ================================================================================
echo.

pause
