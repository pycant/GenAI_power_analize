# -*- coding: utf-8 -*-
"""测试BERTScore导入"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

print("Testing bert_score import...")

try:
    import bert_score
    print(f"✅ bert_score imported successfully, version: {bert_score.__version__}")
except ImportError as e:
    print(f"❌ ImportError: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")

try:
    from bert_score import score
    print("✅ bert_score.score imported successfully")
    
    # 测试实际调用
    P, R, F1 = score(
        ["This is a test."], 
        ["This is a test."], 
        lang='en', 
        device='cpu',
        verbose=False
    )
    print(f"✅ BERTScore test successful: P={P.item():.4f}, R={R.item():.4f}, F1={F1.item():.4f}")
    
except ImportError as e:
    print(f"❌ ImportError when importing score: {e}")
except Exception as e:
    print(f"❌ Error during BERTScore calculation: {e}")
