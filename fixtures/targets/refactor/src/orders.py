def total_order(items):
    """Sum positive line totals; ignore zero or negative quantities."""
    total = 0
    for price, quantity in items:
        if quantity > 0:
            total += price * quantity
    return total
