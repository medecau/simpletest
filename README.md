# 👋

SimpleTest is a Python library that helps write and run tests on CircuitPython.
It aims to mimic, as much as possible, the Pytest API.

## Usage

```
import simpletest as st

def inc(num):
    return num + 1

def test_answer():
    assert inc(3) == 4

st.run(globals())
```
