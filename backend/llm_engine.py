"""
This module simulates LLM reasoning.
In production, this can be replaced with LLaMA / OpenAI / local model.
"""

def analyze_thinking_quality(previous_text: str, current_text: str) -> float:
    """
    Returns a score between 0 and 1 indicating thinking originality.
    """

    # If content barely changed → likely copy or low effort
    if previous_text.strip() == current_text.strip():
        return 0.1

    # If length increased meaningfully → thinking effort
    if len(current_text) > len(previous_text) * 1.3:
        return 0.8

    # Default moderate improvement
    return 0.5
