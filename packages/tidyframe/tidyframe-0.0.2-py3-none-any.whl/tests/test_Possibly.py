import math
import numpy as np
from tidyframe import Possibly


@Possibly()
def log_possibly(x):
    return math.log(x)


def test_Possibly_basic_success():
    assert np.isclose(log_possibly(10), math.log(10)), 'Must result is True'


def test_pPossibly_basic_fail():
    assert np.isnan(log_possibly(-10)), 'Must result is True'


def test_Possibly_change_otherwise():
    @Possibly(otherwise=-1)
    def log_possibly(x):
        return math.log(x)

    assert np.isclose(log_possibly(-10), -1), 'Must result is True'


def test_Possibly_classmethod_basic_success():
    assert np.isclose(Possibly.possibly(math.log)(10),
                      math.log(10)), 'Must result is True'


def test_Possibly_classmethod_basic_fail():
    assert np.isnan(Possibly.possibly(math.log)(-1)), 'Must result is True'


def test_Possibly_classmethod_change_default():
    Possibly.otherwise_all = 1
    Possibly.quiet_all = False
    assert np.isclose(Possibly.possibly(math.log)(-1),
                      1), 'Must result is True'


def test_Possibly_print_exception():
    @Possibly(otherwise=-1, quiet=False)
    def log_possibly(x):
        return math.log(x)

    log_possibly(-10)
