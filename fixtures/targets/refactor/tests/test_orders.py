from src.orders import total_order


def test_existing_order():
    assert total_order([(10, 2), (3, 0)]) == 20
