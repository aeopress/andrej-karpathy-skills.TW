"""
Tests for stats.py.  Run with: pytest tests/test_stats.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from stats import running_average, clamp, caesar_cipher, word_count, median


# ---------------------------------------------------------------------------
# running_average — no bug, should pass
# ---------------------------------------------------------------------------

def test_running_average_basic():
    result = running_average([4.0, 2.0, 6.0])
    assert result == pytest.approx([4.0, 3.0, 4.0]), (
        f"Expected [4.0, 3.0, 4.0], got {result}"
    )


def test_running_average_single_element():
    assert running_average([7.0]) == pytest.approx([7.0])


def test_running_average_empty():
    assert running_average([]) == []


# ---------------------------------------------------------------------------
# clamp — BUG 1: lo/hi return values are swapped
# ---------------------------------------------------------------------------

def test_clamp_above_hi_returns_hi():
    """Value above hi should be clamped to hi, not lo."""
    result = clamp(15, 1, 10)
    assert result == 10, (
        f"clamp(15, 1, 10) should return 10 (hi), got {result!r}. "
        "Check that the too-high branch returns hi, not lo."
    )


def test_clamp_within_range():
    assert clamp(5, 1, 10) == 5


# ---------------------------------------------------------------------------
# caesar_cipher — BUG 2: shift subtracted instead of added
# ---------------------------------------------------------------------------

def test_caesar_cipher_encrypts_correctly():
    """'abc' shifted by 3 should become 'def', not 'xyz'."""
    result = caesar_cipher("abc", 3)
    assert result == "def", (
        f"caesar_cipher('abc', 3) should return 'def', got {result!r}. "
        "Check the direction of the shift (add, not subtract)."
    )


def test_caesar_cipher_preserves_non_alpha():
    # Uses shift=0, so no movement regardless of direction — still passes
    result = caesar_cipher("a1b!", 0)
    assert result == "a1b!"


# ---------------------------------------------------------------------------
# word_count — BUG 3: counts incremented by 2 instead of 1
# ---------------------------------------------------------------------------

def test_word_count_unique_words():
    """Each unique word should appear exactly once (count=1)."""
    result = word_count("hello world")
    assert result == {"hello": 1, "world": 1}, (
        f"word_count('hello world') should be {{'hello': 1, 'world': 1}}, "
        f"got {result!r}. Each word should increment by 1, not 2."
    )


# ---------------------------------------------------------------------------
# median — no bug, should pass
# ---------------------------------------------------------------------------

def test_median_odd_length():
    assert median([3, 1, 4, 1, 5]) == pytest.approx(3.0)


def test_median_even_length():
    assert median([1, 3, 5, 7]) == pytest.approx(4.0)
