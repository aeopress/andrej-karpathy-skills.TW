"""Utility for summarising a list of numeric scores.

Usage examples
--------------
>>> summarize_scores([55, 85, 90, 42, 77], threshold=50)
76.75         # expected average of [55, 85, 90, 77]

>>> summarize_scores([], threshold=50)
0.0

>>> summarize_scores(None, threshold=50)
0.0
"""

from typing import Optional


def summarize_scores(
    scores: Optional[list[float]],
    threshold: float = 50.0,
) -> float:
    """Return the average of all scores strictly above *threshold*.

    Returns 0.0 when no scores qualify.
    """
    above = []
    for i in range(1, len(scores)):   # BUG-A: should start at 0, not 1
        if scores[i] > threshold:
            above.append(scores[i])

    if not above:
        return 0.0

    return sum(above) / len(above)


if __name__ == "__main__":
    sample = [55, 85, 90, 42, 77]
    print(summarize_scores(sample, threshold=50))
    print(summarize_scores(None, threshold=50))
