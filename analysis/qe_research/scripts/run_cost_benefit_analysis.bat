@echo off
REM 成本效益分析批处理脚本
REM 运行第5章完整分析

echo ========================================
echo 第5章: 成本效益分析与选择策略
echo ========================================
echo.

REM 激活conda环境
echo 激活conda环境: bartscore
call conda activate bartscore
if errorlevel 1 (
    echo 错误: 无法激活conda环境
    pause
    exit /b 1
)

REM 设置UTF-8编码
set PYTHONUTF8=1

REM 运行分析脚本
echo.
echo 开始运行成本效益分析...
echo.
python generate_cost_benefit_report.py

if errorlevel 1 (
    echo.
    echo 错误: 分析执行失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 分析完成!
echo ========================================
echo.
echo 结果保存在: analysis/qe_research/results/cost_benefit_analysis/
echo.
echo 主要输出文件:
echo   - SECTION_5_COST_BENEFIT_ANALYSIS_REPORT.md (完整报告)
echo   - cost_benefit_scatter.png (成本-质量散点图)
echo   - marginal_benefit_curve.png (边际效益曲线)
echo   - scenario_comparison.png (场景对比图)
echo.

pause
