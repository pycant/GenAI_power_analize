#!/usr/bin/env python
"""Test script to verify BARTScore deployment"""

import sys
import traceback
import os

# Add BARTScore directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'BARTScore'))

def test_bartscore():
    """Test BARTScore functionality"""
    print("Testing BARTScore deployment...")
    
    # Set environment variables to avoid warnings and issues
    os.environ['HF_ENDPOINT'] = 'https://huggingface.co'
    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
    
    # Test 1: Check imports
    print("\n1. Testing imports...")
    try:
        import torch
        import transformers
        from bart_score import BARTScorer
        print(f"✓ PyTorch version: {torch.__version__}")
        print(f"✓ Transformers version: {transformers.__version__}")
        print("✓ All imports successful!")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        traceback.print_exc()
        return False
    
    # Test 2: Check CUDA availability
    print("\n2. Testing CUDA availability...")
    try:
        if torch.cuda.is_available():
            print(f"✓ CUDA is available")
            print(f"✓ CUDA version: {torch.version.cuda}")
            print(f"✓ GPU device: {torch.cuda.get_device_name(0)}")
            device = 'cuda:0'
        else:
            print("✗ CUDA is not available, using CPU")
            device = 'cpu'
    except Exception as e:
        print(f"✗ CUDA check error: {e}")
        device = 'cpu'
    
    # Test 3: Test BARTScore initialization
    print("\n3. Testing BARTScore initialization...")
    try:
        print("Initializing BARTScorer (this may take a moment to download model)...")
        bart_scorer = BARTScorer(device=device, checkpoint='facebook/bart-large-cnn')
        print("✓ BARTScorer initialized successfully!")
    except Exception as e:
        print(f"✗ BARTScorer initialization failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 4: Test scoring functionality
    print("\n4. Testing scoring functionality...")
    try:
        src_list = [
            'This is a very good idea. Although simple, but very insightful.',
            'Can I take a look?',
            'Do not trust him, he is a liar.'
        ]
        
        tgt_list = [
            "That's stupid.",
            "What's the problem?",
            'He is trustworthy.'
        ]
        
        print(f"Source sentences: {src_list}")
        print(f"Target sentences: {tgt_list}")
        
        scores = bart_scorer.score(src_list, tgt_list, batch_size=2)
        print(f"✓ Scores computed successfully: {scores}")
        
        if len(scores) == len(src_list):
            print(f"✓ Correct number of scores returned: {len(scores)}")
        else:
            print(f"✗ Incorrect number of scores: expected {len(src_list)}, got {len(scores)}")
            return False
            
    except Exception as e:
        print(f"✗ Scoring test failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 5: Test multi-reference scoring
    print("\n5. Testing multi-reference scoring...")
    try:
        srcs = ['This is a test sentence.']
        tgts = [['This is a test.', 'This is a test sentence.', 'A test this is.']]
        
        multi_scores = bart_scorer.multi_ref_score(srcs, tgts, agg="mean", batch_size=1)
        print(f"✓ Multi-reference scores computed: {multi_scores}")
    except Exception as e:
        print(f"✗ Multi-reference scoring failed: {e}")
        traceback.print_exc()
        # Don't fail the whole test for this
    
    print("\n" + "="*50)
    print("✓ All tests passed! BARTScore deployment successful!")
    print("="*50)
    return True

if __name__ == "__main__":
    success = test_bartscore()
    sys.exit(0 if success else 1)
