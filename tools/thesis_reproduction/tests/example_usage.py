#!/usr/bin/env python
"""Example usage of BARTScore for text evaluation - Based on BARTScore Paper"""

import os
import sys
# Set environment variables to avoid warnings
os.environ['HF_ENDPOINT'] = 'https://huggingface.co'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

# Add BARTScore directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'BARTScore'))

from bart_score import BARTScorer

def main():
    print("BARTScore Example Usage - Based on BARTScore Paper")
    print("=" * 70)
    
    # Initialize BARTScorer with GPU support
    print("\n1. Initializing BARTScorer...")
    try:
        bart_scorer = BARTScorer(device='cuda:0', checkpoint='facebook/bart-large-cnn')
        print("   ✓ BARTScorer initialized on GPU")
    except Exception as e:
        print(f"   ⚠ GPU not available, using CPU: {e}")
        bart_scorer = BARTScorer(device='cpu', checkpoint='facebook/bart-large-cnn')
        print("   ✓ BARTScorer initialized on CPU")
    
    # Section 1: Demonstrating BARTScore's Four Usage Modes (from paper)
    print("\n" + "=" * 70)
    print("SECTION 1: BARTScore's Four Usage Modes (as described in paper)")
    print("=" * 70)
    
    # Example 1.1: Faithfulness (s→h) - Factuality and Relevance
    print("\n1.1 Faithfulness (s→h) - Evaluating factuality and relevance")
    print("   Input: Source text (s)")
    print("   Output: Generated text/Hypothesis (h)")
    print("   Use case: Fact-checking, content consistency")
    
    source_texts = [
        "The Eiffel Tower is located in Paris, France.",
        "Photosynthesis converts sunlight into chemical energy.",
        "Shakespeare wrote Hamlet in the early 17th century."
    ]
    
    hypotheses = [
        "The Eiffel Tower is in Paris.",  # Faithful
        "Plants use photosynthesis to make food from light.",  # Faithful  
        "Shakespeare authored Romeo and Juliet in 1597.",  # Partially faithful (wrong play)
    ]
    
    faithfulness_scores = bart_scorer.score(source_texts, hypotheses, batch_size=2)
    
    for i, (src, hyp, score) in enumerate(zip(source_texts, hypotheses, faithfulness_scores)):
        print(f"\n   Example {i+1}:")
        print(f"   Source: {src}")
        print(f"   Hypothesis: {hyp}")
        print(f"   Faithfulness score: {score:.4f}")
        print(f"   Interpretation: {'More faithful' if score < -3.0 else 'Less faithful'} (lower/negative is better)")
    
    # Example 1.2: Precision (r→h) - Evaluating precision
    print("\n\n1.2 Precision (r→h) - Evaluating precision against reference")
    print("   Input: Reference text (r)")
    print("   Output: Generated text (h)")
    print("   Use case: Summary evaluation, translation quality")
    
    references = [
        "The quick brown fox jumps over the lazy dog.",
        "Artificial intelligence is revolutionizing healthcare diagnostics.",
        "Renewable energy sources reduce carbon emissions significantly."
    ]
    
    generated_texts = [
        "A fast brown fox leaps over a sleepy dog.",  # High precision
        "AI is changing medical diagnosis.",  # Medium precision
        "Solar power cuts CO2 output.",  # Lower precision (simplified)
    ]
    
    precision_scores = bart_scorer.score(references, generated_texts, batch_size=2)
    
    for i, (ref, gen, score) in enumerate(zip(references, generated_texts, precision_scores)):
        print(f"\n   Example {i+1}:")
        print(f"   Reference: {ref}")
        print(f"   Generated: {gen}")
        print(f"   Precision score: {score:.4f}")
    
    # Example 1.3: Recall (h→r) - Evaluating semantic coverage  
    print("\n\n1.3 Recall (h→r) - Evaluating semantic coverage")
    print("   Input: Generated text (h)")
    print("   Output: Reference text (r)")
    print("   Use case: Content completeness, information recall")
    print("   Note: This requires swapping input/output compared to precision")
    
    # For recall, we swap the inputs: generated text as source, reference as target
    recall_scores = bart_scorer.score(generated_texts, references, batch_size=2)
    
    for i, (gen, ref, score) in enumerate(zip(generated_texts, references, recall_scores)):
        print(f"\n   Example {i+1}:")
        print(f"   Generated: {gen}")
        print(f"   Reference: {ref}")
        print(f"   Recall score: {score:.4f}")
        print(f"   Interpretation: Higher recall = better semantic coverage")
    
    # Example 1.4: F-score (r↔h) - Combined evaluation
    print("\n\n1.4 F-score (r↔h) - Combined precision and recall")
    print("   Bidirectional evaluation between reference and generated text")
    print("   Use case: Overall quality assessment")
    
    # Calculate F-score as harmonic mean of precision and recall
    for i in range(len(references)):
        precision = precision_scores[i]
        recall = recall_scores[i]
        # Simple harmonic mean (actual implementation may differ)
        f_score = 2 * precision * recall / (precision + recall) if (precision + recall) != 0 else 0
        print(f"\n   Example {i+1}:")
        print(f"   Precision: {precision:.4f}, Recall: {recall:.4f}")
        print(f"   Approx F-score: {f_score:.4f}")
    
    # Section 2: Application Examples from Paper
    print("\n" + "=" * 70)
    print("SECTION 2: Application Examples (Inspired by BARTScore Paper)")
    print("=" * 70)
    
    # Example 2.1: Summarization Evaluation
    print("\n2.1 Text Summarization Evaluation")
    document = """
    Artificial intelligence (AI) refers to the simulation of human intelligence in machines 
    that are programmed to think like humans and mimic their actions. The term may also be 
    applied to any machine that exhibits traits associated with a human mind such as 
    learning and problem-solving. The ideal characteristic of artificial intelligence is 
    its ability to rationalize and take actions that have the best chance of achieving 
    a specific goal. AI research has been divided into subfields that often fail to 
    communicate with each other. These sub-fields are based on technical considerations, 
    such as particular goals, the use of particular tools, or deep philosophical differences.
    """
    
    summaries = [
        # Good summary
        "AI simulates human intelligence in machines, enabling learning and problem-solving to achieve goals.",
        # Medium summary  
        "Artificial intelligence makes machines think like humans.",
        # Poor summary
        "AI is computers doing smart things.",
    ]
    
    print(f"   Document length: {len(document.split())} words")
    print(f"   Document excerpt: {document[:100]}...")
    
    summary_scores = bart_scorer.score([document]*3, summaries, batch_size=1)
    
    print("\n   Summary Evaluation Results:")
    for i, (summary, score) in enumerate(zip(summaries, summary_scores)):
        print(f"\n   Summary {i+1}:")
        print(f"   '{summary[:60]}...'")
        print(f"   Score: {score:.4f}")
        quality = "Good" if score < -4.0 else "Medium" if score < -3.0 else "Poor"
        print(f"   Quality: {quality}")
    
    # Example 2.2: Machine Translation Evaluation
    print("\n\n2.2 Machine Translation Evaluation")
    source_sentences = [
        "今天天气很好，我们一起去公园吧。",
        "人工智能正在改变世界。",
        "这本书非常有趣，我推荐你读一读。"
    ]
    
    reference_translations = [
        "The weather is nice today, let's go to the park together.",
        "Artificial intelligence is changing the world.",
        "This book is very interesting, I recommend you read it."
    ]
    
    machine_translations = [
        "Today weather good, we go park.",  # Poor translation
        "AI is transforming the world.",  # Good translation
        "Book interesting, I suggest you read.",  # Medium translation
    ]
    
    print("   Chinese Source Sentences:")
    for src in source_sentences:
        print(f"   - {src}")
    
    mt_scores = bart_scorer.score(reference_translations, machine_translations, batch_size=2)
    
    print("\n   Translation Evaluation Results:")
    for i, (ref, mt, score) in enumerate(zip(reference_translations, machine_translations, mt_scores)):
        print(f"\n   Example {i+1}:")
        print(f"   Reference: {ref}")
        print(f"   MT Output: {mt}")
        print(f"   BARTScore: {score:.4f}")
        print(f"   Quality: {'Good' if score < -3.5 else 'Acceptable' if score < -2.5 else 'Poor'}")
    
    # Example 2.3: Dialogue Response Evaluation
    print("\n\n2.3 Dialogue Response Evaluation")
    contexts = [
        "User: What's the capital of France?",
        "User: How does photosynthesis work?",
        "User: Who wrote 'Pride and Prejudice'?"
    ]
    
    good_responses = [
        "The capital of France is Paris.",
        "Photosynthesis is the process by which plants convert sunlight into chemical energy.",
        "'Pride and Prejudice' was written by Jane Austen."
    ]
    
    poor_responses = [
        "I think it's London.",  # Wrong answer
        "Plants eat sunlight.",  # Oversimplified
        "Shakespeare wrote it.",  # Incorrect author
    ]
    
    print("   Dialogue Contexts:")
    for ctx in contexts:
        print(f"   - {ctx}")
    
    # Evaluate good responses
    good_scores = bart_scorer.score(contexts, good_responses, batch_size=2)
    poor_scores = bart_scorer.score(contexts, poor_responses, batch_size=2)
    
    print("\n   Response Evaluation Results:")
    for i in range(len(contexts)):
        print(f"\n   Context {i+1}: {contexts[i]}")
        print(f"   Good response: '{good_responses[i]}'")
        print(f"   Score: {good_scores[i]:.4f}")
        print(f"   Poor response: '{poor_responses[i]}'")
        print(f"   Score: {poor_scores[i]:.4f}")
        print(f"   Difference: {good_scores[i] - poor_scores[i]:.4f} (lower is better for good response)")
    
    # Section 3: Advanced Features
    print("\n" + "=" * 70)
    print("SECTION 3: Advanced Features and Best Practices")
    print("=" * 70)
    
    # Example 3.1: Multi-reference Evaluation
    print("\n3.1 Multi-reference Evaluation")
    source = "The cat sat on the mat."
    
    reference_sets = [
        ["A cat was sitting on the mat.", "The feline rested on the rug.", "On the mat sat a cat."],
        ["The dog slept on the bed.", "A canine was resting on the couch.", "On the bed slept a dog."]
    ]
    
    hypotheses = ["A cat was on the mat.", "The dog was on the bed."]
    
    print(f"   Source: {source}")
    print(f"   Hypotheses: {hypotheses}")
    print(f"   Reference sets: {reference_sets}")
    
    # Note: multi_ref_score expects list of sources and list of reference lists
    sources = [source, source]
    multi_scores_mean = bart_scorer.multi_ref_score(sources, reference_sets, agg="mean", batch_size=1)
    multi_scores_max = bart_scorer.multi_ref_score(sources, reference_sets, agg="max", batch_size=1)
    
    print("\n   Multi-reference Results:")
    for i, (hyp, mean_score, max_score) in enumerate(zip(hypotheses, multi_scores_mean, multi_scores_max)):
        print(f"\n   Hypothesis {i+1}: '{hyp}'")
        print(f"   Mean aggregation: {mean_score:.4f}")
        print(f"   Max aggregation: {max_score:.4f}")
        print(f"   References: {reference_sets[i]}")
    
    # Example 3.2: Batch Size Optimization
    print("\n\n3.2 Batch Size Optimization for GPU")
    print("   Testing different batch sizes...")
    
    test_sources = ["Test sentence " + str(i) for i in range(10)]
    test_targets = ["Target sentence " + str(i) for i in range(10)]
    
    batch_sizes = [1, 2, 4, 8]
    for batch_size in batch_sizes:
        try:
            scores = bart_scorer.score(test_sources[:4], test_targets[:4], batch_size=batch_size)
            print(f"   Batch size {batch_size}: Success")
        except Exception as e:
            print(f"   Batch size {batch_size}: Failed - {str(e)[:50]}...")
    
    # Example 3.3: Score Interpretation Guide
    print("\n\n3.3 BARTScore Interpretation Guide")
    print("   Score Range and Meaning:")
    print("   - < -5.0: Excellent quality")
    print("   - -5.0 to -4.0: Very good quality")
    print("   - -4.0 to -3.0: Good quality")
    print("   - -3.0 to -2.0: Acceptable quality")
    print("   - > -2.0: Poor quality")
    print("   Note: These are approximate thresholds and may vary by task.")
    
    # Section 4: Conclusion and Best Practices
    print("\n" + "=" * 70)
    print("SECTION 4: Conclusion and Best Practices")
    print("=" * 70)
    
    print("\n4.1 Key Takeaways from BARTScore Paper:")
    print("   - BARTScore outperforms top metrics in 16 out of 22 test settings")
    print("   - Covers 16 datasets and 7 evaluation perspectives")
    print("   - No task-specific training required")
    print("   - Supports multiple evaluation angles through different input-output pairs")
    
    print("\n4.2 Best Practices for Using BARTScore:")
    print("   1. Choose the right evaluation angle for your task:")
    print("      - Faithfulness (s→h) for fact-checking")
    print("      - Precision (r→h) for translation/summary quality")
    print("      - Recall (h→r) for content completeness")
    print("      - F-score (r↔h) for overall assessment")
    
    print("\n   2. Optimize batch size based on available GPU memory")
    print("      - Start with batch_size=4 and adjust")
    print("      - Reduce if you get CUDA out of memory errors")
    
    print("\n   3. Use appropriate model checkpoint:")
    print("      - 'facebook/bart-large-cnn' for summarization tasks")
    print("      - 'facebook/bart-large-mnli' for NLI-related tasks")
    print("      - 'facebook/bart-large' for general purposes")
    
    print("\n   4. Handle long texts:")
    print("      - BART has max_length=1024 tokens")
    print("      - Truncate or split longer texts if necessary")
    
    print("\n   5. Interpret scores correctly:")
    print("      - Scores are negative log-likelihoods")
    print("      - Lower (more negative) scores indicate better quality")
    print("      - Compare relative scores within the same task/domain")
    
    print("\n" + "=" * 70)
    print("SUMMARY: BARTScore provides a unified framework for evaluating")
    print("generated text across multiple dimensions without task-specific")
    print("training. It leverages pre-trained BART models to assess text")
    print("quality through different input-output perspectives.")
    print("=" * 70)
    
    print("\nTo use BARTScore in your project:")
    print("1. Import: from bart_score import BARTScorer")
    print("2. Initialize: scorer = BARTScorer(device='cuda:0')")
    print("3. Score: scores = scorer.score(sources, targets)")
    print("\nExample files are available in tools/thesis_reproduction/tests/")
    print("Detailed usage guide: tools/thesis_reproduction/BARTScore/BARTScore_USAGE_GUIDE.md")

if __name__ == "__main__":
    main()
