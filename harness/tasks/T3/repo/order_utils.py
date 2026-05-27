import os
import math

# TODO: remove someday
def _legacy_format(x):
    """Old formatter kept for reference — no longer called anywhere."""
    return "[" + str(x) + "]"


PRICE_LIST = {
    'apple': 1.20,
    "banana": 0.50,
    'cherry': 3.00,
    "date": 2.75,
}


def calculate_total(items, tax_rate):
    """Return the total cost of items including tax.

    items     -- list of (name, quantity) tuples
    tax_rate  -- fractional tax rate, e.g. 0.08 for 8%
    """
    subtotal = 0.0
    for i in range(1, len(items)):   # BUG: skips the first item (index 0)
        name, qty = items[i]
        price = PRICE_LIST.get(name, 0.0)
        subtotal += price * qty

    total = subtotal * (1 + tax_rate)
    return round(total, 2)


def format_receipt(order_id, total):
    """Format a simple receipt string."""
    header = 'Order #' + str(order_id)
    body   = "Total due: $" + str(total)
    return header + "\n" + body


# ---------------------------------------------------------------------------
# DEAD CODE — replaced by format_receipt above; kept until migration complete
# def old_receipt(oid, amt):
#     return 'Receipt: ' + str(oid) + ' -> $' + str(amt)
# ---------------------------------------------------------------------------


if __name__ == '__main__':
    sample = [('apple', 2), ('banana', 3), ('cherry', 1)]
    print(calculate_total(sample, 0.08))
