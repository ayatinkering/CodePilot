import itertools

from src.orders import total_order


def reference(items):
    total = 0
    for price, quantity in items:
        if quantity > 0:
            total += price * quantity
    return total


def test_behavior_preservation():
    values = list(itertools.product([-2, 0, 1.5, 10], [-1, 0, 1, 3]))
    for a in values:
        for b in values:
            assert total_order([a, b]) == reference([a, b])
    assert total_order([]) == 0
