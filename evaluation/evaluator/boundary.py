from src.discounts import eligible


def test_exact_boundary_and_neighbors():
    for age in range(100):
        assert eligible(age) is (age >= 18)
