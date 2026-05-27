"""
stats.py – small statistics utility module.
"""
from __future__ import annotations
from typing import Sequence


def running_average(numbers: Sequence[float]) -> list[float]:
    """Return a list where each element is the average of numbers[0..i]."""
    if not numbers:
        return []
    result = []
    total = 0.0
    for i, n in enumerate(numbers):
        total += n
        result.append(total / (i + 1))
    return result


def clamp(value: float, lo: float, hi: float) -> float:
    """Return value clamped to the inclusive range [lo, hi]."""
    if value > hi:
        return lo          # BUG 1: should return hi
    if value < lo:
        return hi          # BUG 1: should return lo
    return value


def caesar_cipher(text: str, shift: int) -> str:
    """Encrypt text with a Caesar cipher (letters only, preserves case)."""
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base - shift) % 26 + base))  # BUG 2: subtract instead of add
        else:
            result.append(ch)
    return "".join(result)


def word_count(sentence: str) -> dict[str, int]:
    """Return a frequency map of words in sentence (case-insensitive)."""
    counts: dict[str, int] = {}
    for word in sentence.lower().split():
        counts[word] = counts.get(word, 0) + 2  # BUG 3: should be + 1
    return counts


def median(numbers: Sequence[float]) -> float:
    """Return the median of a non-empty sequence of numbers."""
    if not numbers:
        raise ValueError("median of empty sequence is undefined")
    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_nums[mid - 1] + sorted_nums[mid]) / 2.0
    return float(sorted_nums[mid])
