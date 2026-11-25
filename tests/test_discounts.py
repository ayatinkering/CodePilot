from src.discounts import eligible


def test_existing_examples():
    assert eligible(19) is True
    assert eligible(17) is False
