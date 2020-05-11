import os
import sys
import re
import time


def run(gs, verbose=False, tb=None, k=None):
    _title("test session starts")

    print(
        " -- ".join(
            [
                f"platform {sys.platform}",
                f"Python {sys.version}",
                f"{sys.implementation.name} {'.'.join(map(str,sys.implementation.version))}",
            ]
        )
    )

    start_time = time.monotonic()

    tests = list(_gather_tests(gs))
    if k:
        tests = [t for t in tests if k in t[0]]

    print(f"collected {len(tests)} items")

    results = list()
    passed = failed = errored = 0
    for name, test in tests:
        relevant_fixtures = _get_relevant_fixtures(test)
        computed_fixtures = {k: v() for k, v in relevant_fixtures.items()}

        result = True
        try:
            test(**computed_fixtures)
            result = (name, None)
        except Exception as err:
            result = (name, err)
        results.append(result)

        if result[1] is None:
            passed += 1
            print(f"{name} PASSED") if verbose else print(".", end="")
        elif isinstance(result[1], AssertionError):
            failed += 1
            print(f"{name} FAILED") if verbose else print("F", end="")
        else:
            errored += 1
            print(f"{name} ERROR") if verbose else print("E", end="")
    if not verbose:
        print()

    _title("failures")
    for test, err in results:
        if err is not None:
            if tb == "none":
                continue

            _section(test)
            sys.print_exception(err)
            print(f"{test}: {type(err).__name__}")

    total_run_time = round(time.monotonic() - start_time, 3)

    short_reports = list()
    if passed:
        short_reports.append(f"{passed} passed")
    if failed:
        short_reports.append(f"{failed} failed")
    if errored:
        short_reports.append(f"{errored} errored")
    stats_report = ", ".join(short_reports)
    line_report = f"{stats_report} in {total_run_time}s"
    _title(line_report)


# DECORATORS

_fixtures = dict()


def fixture(fn):
    def inner(*args, **kwargs):
        return fn(*args, **kwargs)

    _fixtures[fn.__name__] = inner


_parametrized = list()


def parametrize(**params):
    def _parametrize(fn):
        parametrizations = list()

        fkey = list(params.keys())[0]
        for val in params.pop(fkey):
            parametrizations.append([(fkey, val)])

        for key, vals in params.items():
            new_parametrizations = list()
            for parametrization in parametrizations:
                for val in vals:
                    new_parametrizations.append(parametrization + [(key, val)])
            parametrizations = new_parametrizations

        for params in parametrizations:
            _kwargs = {k: v for k, v in params}

            def __parametrized(**_kwargs):
                def parametrized(**kwargs):
                    final_kwargs = _kwargs.copy()
                    final_kwargs.update(**kwargs)
                    return fn(**final_kwargs)

                return parametrized

            params_repr = ", ".join(str(v) for v in _kwargs.values())
            parametrization_name = f"{fn.__name__}[{params_repr}]"
            _parametrized.append((parametrization_name, __parametrized(**_kwargs)))

    return _parametrize


# INTERNALS


def _gather_tests(gs):
    _ = list(gs.items()) + _parametrized
    _ = ((g, v) for g, v in _ if type(v) in (FunctionType, ClosureType))
    _ = ((g, v) for g, v in _ if g.startswith("test"))
    return _


def _get_relevant_fixtures(test):
    relevant_fixtures = _fixtures.copy()
    for _ in range(len(relevant_fixtures)):
        try:
            test(**relevant_fixtures)
        except TypeError as err:
            err_msg = err.args[0]

            match = re.match(r"unexpected keyword argument '(.+)'", err_msg)
            unwanted_fixture = match.group(1)

            relevant_fixtures.pop(unwanted_fixture, None)
        except AssertionError:
            pass  # quiet for now

    return relevant_fixtures


def _title(msg):
    print()
    print(("{:#^60}").format(f" {msg} ").replace("#", "="))  # don't ask


def _section(msg):
    print("{:_^60}".format(f" {msg} "))


def _d(f):
    def __d():
        return f(v)

    return __d


@_d
def _c():
    pass


ClosureType = type(_c)


def _f():
    pass


FunctionType = type(_f)
