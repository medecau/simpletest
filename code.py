import random
import os

import simpletest as st


def square(n):
    return n ** 2


@st.parametrize(v=range(2, 10))
def test_square(v):
    assert square(v) > v


@st.parametrize(x=range(3), y=(random.random() for _ in range(3)))
def test_parametrization(x, y):
    s = x + y
    x_1 = x + 1

    assert x < s < x_1


@st.fixture
def not_used():
    pass  # not a problem


@st.fixture
def truth():
    return True


def test_fixtures_work(truth):
    assert isinstance(truth, bool)


def test_fail_on_purpose():
    assert False


def test_raise():
    raise Exception("Oops!")
    assert True


st.run(globals())
# st.run(globals(), verbose=True)
