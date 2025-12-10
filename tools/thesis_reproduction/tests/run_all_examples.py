#!/usr/bin/env python
"""Run all BARTScore examples to verify deployment"""

import os
import sys
import subprocess

def run_example(script_name, description):
    """Run a Python script and capture its output"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Print output
        if result.stdout:
            print("Output:")
            print(result.stdout[:2000])  # Limit output length
        
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr[:1000])
        
        if result.returncode == 0:
            print(f"\n✓ {description} completed successfully")
            return True
        else:
            print(f"\n✗ {description} failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n✗ Error running {description}: {e}")
        return False

def main():
    print("BARTScore Examples Verification")
    print("=" * 60)
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Test directory: {os.path.dirname(os.path.abspath(__file__))}")
    
    # List of examples to run
    examples = [
        ("test_bartscore_deployment.py", "BARTScore Deployment Verification"),
        ("example_usage.py", "BARTScore Example Usage (Based on Paper)"),
    ]
    
    success_count = 0
    total_count = len(examples)
    
    for script_name, description in examples:
        if run_example(script_name, description):
            success_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total examples: {total_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_count - success_count}")
    
    if success_count == total_count:
        print("\n✓ All examples completed successfully!")
        print("\nBARTScore is fully deployed and ready for use.")
        print("\nKey files created:")
        print("1. tools/thesis_reproduction/BARTScore/BARTScore_USAGE_GUIDE.md")
        print("   - Detailed usage guide based on BARTScore paper")
        print("2. tools/thesis_reproduction/tests/example_usage.py")
        print("   - Comprehensive examples covering all usage modes")
        print("3. tools/thesis_reproduction/tests/test_bartscore_deployment.py")
        print("   - Deployment verification script")
        print("\nTo use BARTScore in your projects:")
        print("1. Activate conda environment: conda activate bartscore")
        print("2. Import: from bart_score import BARTScorer")
        print("3. Initialize: scorer = BARTScorer(device='cuda:0')")
        print("4. Score: scores = scorer.score(sources, targets)")
    else:
        print(f"\n⚠ {total_count - success_count} example(s) failed.")
        print("Check the error messages above for troubleshooting.")
    
    return 0 if success_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main())
