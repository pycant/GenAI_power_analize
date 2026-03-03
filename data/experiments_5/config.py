# Experiment 5 Configuration
# Generated: 2026-03-02 22:43:13

TEMPERATURE = 0.7
TOP_P = 0.9
NUM_CTX = 8192
SEED = 42
KEEPALIVE = "5m"
WARMUP = True
RUNS = 1

# Models to evaluate
MODELS = ['qwen3:4b', 'qwen3:8b', 'deepseek-r1:8b', 'gemma3:4b']

# Test cases source
TEST_CASES_SOURCE = "data/test_cases/test_cases_comprehensive.json"
