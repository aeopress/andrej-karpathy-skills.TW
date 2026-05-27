import pytest
from order_utils import calculate_total


def test_single_item():
    # 1 apple at $1.20, 0% tax => $1.20
    assert calculate_total([('apple', 1)], 0.0) == 1.20


def test_multiple_items():
    # apple x2 = 2.40, banana x3 = 1.50 => subtotal 3.90, tax 8% => 4.21
    assert calculate_total([('apple', 2), ('banana', 3)], 0.08) == 4.21


def test_zero_tax():
    assert calculate_total([('cherry', 1)], 0.0) == 3.00


def test_empty_order():
    assert calculate_total([], 0.10) == 0.0
