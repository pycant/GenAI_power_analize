def bartscore_single(reference, hypothesis, device="cuda"):
    try:
        from tools.thesis_reproduction.BARTScore.bart_score import BARTScorer
        scorer = BARTScorer(device=device, checkpoint="facebook/bart-large-cnn")
        scores = scorer.score([reference], [hypothesis])
        return scores[0]
    except Exception:
        return None

def bartscore_batch(references, hypotheses, device="cuda"):
    try:
        from tools.thesis_reproduction.BARTScore.bart_score import BARTScorer
        scorer = BARTScorer(device=device, checkpoint="facebook/bart-large-cnn")
        return scorer.score(references, hypotheses)
    except Exception:
        return [None for _ in hypotheses]
