@echo off
REM 完整批量实验执行脚本 - 包含量化对比
REM 包含 Ollama 和 HuggingFace 模型（4-bit 和 8-bit 量化）
REM 使用 --skip-bartscore 跳过质量评估，仅收集效率指标
REM 自动跳过已完成的实验

echo ========================================
echo 完整批量实验执行脚本（含量化对比）
echo ========================================
echo.
echo 将依次运行以下 12 个模型配置的实验:
echo.
echo Ollama 模型 (4个):
echo   1. gemma3:4b (Q4_K_M)
echo   2. qwen3:4b (Q4_K_M)
echo   3. qwen3:8b (Q4_K_M)
echo   4. deepseek-r1:8b (Q4_K_M)
echo.
echo HuggingFace 模型 - 量化对比 (8个):
echo   5. Gemma 2B (4-bit)
echo   6. Gemma 2B (8-bit)
echo   7. Phi-3 Mini 3.8B (4-bit)
echo   8. Phi-3 Mini 3.8B (8-bit)
echo   9. Qwen 2.5 3B (4-bit)
echo   10. Qwen 2.5 3B (8-bit)
echo   11. Qwen 2.5 7B (4-bit)
echo   12. Qwen 2.5 7B (8-bit)
echo.
echo 每个配置 40 个任务，预计总时间: 15-20 小时
echo.
echo 注意: 已完成的实验将自动跳过
echo.
pause

REM 激活 conda 环境
call conda activate bartscore

echo.
echo ========================================
echo 第一部分: Ollama 模型 (4个)
echo ========================================

REM 1. Gemma3 4B (Ollama)
echo.
echo ========================================
echo [1/12] 检查 Gemma3 4B (Ollama) 实验...
echo ========================================
if exist "data\gemma_4b_ol_q4km\experiment_results_*_summary.json" (
    echo [SKIP] 实验已完成，跳过
    goto skip_gemma_4b_ol
)
echo [RUN] 开始运行实验...
python experiments/experiment_runner.py --config data/gemma_4b_ol_q4km/test_cases.json --output-dir data/gemma_4b_ol_q4km --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Gemma3 4B 实验失败
    pause
    exit /b 1
)
:skip_gemma_4b_ol

REM 2. Qwen3 4B (Ollama)
echo.
echo ========================================
echo [2/12] 检查 Qwen3 4B (Ollama) 实验...
echo ========================================
if exist "data\qwen_4b_ol_q4km\experiment_results_*_summary.json" (
    echo [SKIP] 实验已完成，跳过
    goto skip_qwen_4b_ol
)
echo [RUN] 开始运行实验...
python experiments/experiment_runner.py --config data/qwen_4b_ol_q4km/test_cases.json --output-dir data/qwen_4b_ol_q4km --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Qwen3 4B 实验失败
    pause
    exit /b 1
)
:skip_qwen_4b_ol

REM 3. Qwen3 8B (Ollama)
echo.
echo ========================================
echo [3/12] 检查 Qwen3 8B (Ollama) 实验...
echo ========================================
if exist "data\qwen_8b_ol_q4km\experiment_results_*_summary.json" (
    echo [SKIP] 实验已完成，跳过
    goto skip_qwen_8b_ol
)
echo [RUN] 开始运行实验...
python experiments/experiment_runner.py --config data/qwen_8b_ol_q4km/test_cases.json --output-dir data/qwen_8b_ol_q4km --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Qwen3 8B 实验失败
    pause
    exit /b 1
)
:skip_qwen_8b_ol

REM 4. DeepSeek-R1 8B (Ollama)
echo.
echo ========================================
echo [4/12] 检查 DeepSeek-R1 8B (Ollama) 实验...
echo ========================================
if exist "data\deepseek_8b_ol_q4km\experiment_results_*_summary.json" (
    echo [SKIP] 实验已完成，跳过
    goto skip_deepseek_8b_ol
)
echo [RUN] 开始运行实验...
python experiments/experiment_runner.py --config data/deepseek_8b_ol_q4km/test_cases.json --output-dir data/deepseek_8b_ol_q4km --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] DeepSeek-R1 8B 实验失败
    pause
    exit /b 1
)
:skip_deepseek_8b_ol

echo.
echo ========================================
echo 第二部分: HuggingFace 模型 - 量化对比 (8个)
echo ========================================

REM 5. Gemma 2B 4-bit (HF)
echo.
echo ========================================
echo [5/12] 检查 Gemma 2B (HF, 4-bit) 实验...
echo ========================================
if exist "data\gemma_2b_hf_4bit\experiment_results_*_summary.json" (
    echo [SKIP] 实验已完成，跳过
    goto skip_gemma_2b_4bit
)
echo [RUN] 开始运行实验...
python experiments/experiment_runner.py --config data/gemma_2b_hf_4bit/test_cases.json --output-dir data/gemma_2b_hf_4bit --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Gemma 2B HF 4-bit 实验失败
    pause
    exit /b 1
)
:skip_gemma_2b_4bit

REM 6. Gemma 2B 8-bit (HF)
echo.
echo ========================================
echo [6/12] 检查 Gemma 2B (HF, 8-bit) 实验...
echo ========================================
if exist "data\gemma_2b_hf_8bit\experiment_results_*_summary.json" (
    echo [SKIP] 实验已完成，跳过
    goto skip_gemma_2b_8bit
)
echo [RUN] 开始运行实验...
python experiments/experiment_runner.py --config data/gemma_2b_hf_8bit/test_cases.json --output-dir data/gemma_2b_hf_8bit --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Gemma 2B HF 8-bit 实验失败
    pause
    exit /b 1
)
:skip_gemma_2b_8bit

REM 7. Phi-3 Mini 4-bit (HF)
echo.
echo ========================================
echo [7/12] 检查 Phi-3 Mini 3.8B (HF, 4-bit) 实验...
echo ========================================
if exist "data\phi3_4b_hf_4bit\experiment_results_*_summary.json" (
    echo [SKIP] 实验已完成，跳过
    goto skip_phi3_4b_4bit
)
echo [RUN] 开始运行实验...
python experiments/experiment_runner.py --config data/phi3_4b_hf_4bit/test_cases.json --output-dir data/phi3_4b_hf_4bit --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Phi-3 Mini HF 4-bit 实验失败
    pause
    exit /b 1
)
:skip_phi3_4b_4bit

REM 8. Phi-3 Mini 8-bit (HF)
echo.
echo ========================================
echo [8/12] 检查 Phi-3 Mini 3.8B (HF, 8-bit) 实验...
echo ========================================
if exist "data\phi3_4b_hf_8bit\experiment_results_*_summary.json" (
    echo [SKIP] 实验已完成，跳过
    goto skip_phi3_4b_8bit
)
echo [RUN] 开始运行实验...
python experiments/experiment_runner.py --config data/phi3_4b_hf_8bit/test_cases.json --output-dir data/phi3_4b_hf_8bit --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Phi-3 Mini HF 8-bit 实验失败
    pause
    exit /b 1
)
:skip_phi3_4b_8bit

REM 9. Qwen 2.5 3B 4-bit (HF)
echo.
echo ========================================
echo [9/12] 检查 Qwen 2.5 3B (HF, 4-bit) 实验...
echo ========================================
if exist "data\qwen25_3b_hf_4bit\experiment_results_*_summary.json" (
    echo [SKIP] 实验已完成，跳过
    goto skip_qwen25_3b_4bit
)
echo [RUN] 开始运行实验...
python experiments/experiment_runner.py --config data/qwen25_3b_hf_4bit/test_cases.json --output-dir data/qwen25_3b_hf_4bit --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Qwen 2.5 3B HF 4-bit 实验失败
    pause
    exit /b 1
)
:skip_qwen25_3b_4bit

REM 10. Qwen 2.5 3B 8-bit (HF)
echo.
echo ========================================
echo [10/12] 检查 Qwen 2.5 3B (HF, 8-bit) 实验...
echo ========================================
if exist "data\qwen25_3b_hf_8bit\experiment_results_*_summary.json" (
    echo [SKIP] 实验已完成，跳过
    goto skip_qwen25_3b_8bit
)
echo [RUN] 开始运行实验...
python experiments/experiment_runner.py --config data/qwen25_3b_hf_8bit/test_cases.json --output-dir data/qwen25_3b_hf_8bit --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Qwen 2.5 3B HF 8-bit 实验失败
    pause
    exit /b 1
)
:skip_qwen25_3b_8bit

REM 11. Qwen 2.5 7B 4-bit (HF)
echo.
echo ========================================
echo [11/12] 检查 Qwen 2.5 7B (HF, 4-bit) 实验...
echo ========================================
if exist "data\qwen25_7b_hf_4bit\experiment_results_*_summary.json" (
    echo [SKIP] 实验已完成，跳过
    goto skip_qwen25_7b_4bit
)
echo [RUN] 开始运行实验...
python experiments/experiment_runner.py --config data/qwen25_7b_hf_4bit/test_cases.json --output-dir data/qwen25_7b_hf_4bit --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Qwen 2.5 7B HF 4-bit 实验失败
    pause
    exit /b 1
)
:skip_qwen25_7b_4bit

REM 12. Qwen 2.5 7B 8-bit (HF)
echo.
echo ========================================
echo [12/12] 检查 Qwen 2.5 7B (HF, 8-bit) 实验...
echo ========================================
if exist "data\qwen25_7b_hf_8bit\experiment_results_*_summary.json" (
    echo [SKIP] 实验已完成，跳过
    goto skip_qwen25_7b_8bit
)
echo [RUN] 开始运行实验...
python experiments/experiment_runner.py --config data/qwen25_7b_hf_8bit/test_cases.json --output-dir data/qwen25_7b_hf_8bit --skip-bartscore
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Qwen 2.5 7B HF 8-bit 实验失败
    pause
    exit /b 1
)
:skip_qwen25_7b_8bit

echo.
echo ========================================
echo 所有实验完成！
echo ========================================
echo.
echo Ollama 模型结果:
echo   - data/gemma_4b_ol_q4km/
echo   - data/qwen_4b_ol_q4km/
echo   - data/qwen_8b_ol_q4km/
echo   - data/deepseek_8b_ol_q4km/
echo.
echo HuggingFace 模型结果 (量化对比):
echo   Gemma 2B:
echo     - data/gemma_2b_hf_4bit/
echo     - data/gemma_2b_hf_8bit/
echo   Phi-3 Mini 3.8B:
echo     - data/phi3_4b_hf_4bit/
echo     - data/phi3_4b_hf_8bit/
echo   Qwen 2.5 3B:
echo     - data/qwen25_3b_hf_4bit/
echo     - data/qwen25_3b_hf_8bit/
echo   Qwen 2.5 7B:
echo     - data/qwen25_7b_hf_4bit/
echo     - data/qwen25_7b_hf_8bit/
echo.
echo 量化对比分析:
echo   - 每个 HF 模型都有 4-bit 和 8-bit 两个版本
echo   - 可以分析量化对质量和效率的影响
echo   - 总计 12 个模型配置，480 个任务
echo.
pause
