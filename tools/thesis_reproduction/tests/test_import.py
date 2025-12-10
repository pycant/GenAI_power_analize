import sys
import torch
sys.path.insert(0, 'tools/thesis_reproduction/BARTScore')

try:
    from bart_score import BARTScorer
    print('BARTScore module imported successfully!')
    
    # Test basic functionality
    scorer = BARTScorer(device='cuda:0' if torch.cuda.is_available() else 'cpu')
    print(f'BARTScorer initialized on device: {scorer.device}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
