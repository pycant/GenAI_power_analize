@echo off
chcp 65001 > nul
echo ========================================
echo Pareto Analysis V3 索引文档生成器
echo ========================================
echo.

cd /d "%~dp0..\..\..\"

echo 📂 当前目录: %CD%
echo.

echo 🔍 检查 Python 环境...
python --version
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python，请确保 Python 已安装并添加到 PATH
    pause
    exit /b 1
)
echo.

echo 📝 生成索引文档...
python analysis\qe_research\scripts\generate_pareto_v3_index.py

if errorlevel 1 (
    echo.
    echo ❌ 生成失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ 索引文档生成完成！
echo ========================================
echo.
echo 📄 输出文件: analysis\qe_research\results\pareto_analysis_v3\INDEX.md
echo.

pause
