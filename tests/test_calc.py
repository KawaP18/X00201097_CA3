from calculator.calc import add, subtract

def test_add_basic():
    assert add(2, 3) == 5

def test_add_negatives():
    assert add(-2, -3) == -5

def test_subtract_basic():
    assert subtract(5, 3) == 2

def test_subtract_to_negative():
    assert subtract(2, 5) == -3
