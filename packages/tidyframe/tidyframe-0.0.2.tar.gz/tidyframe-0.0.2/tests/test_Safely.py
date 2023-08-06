import math
import numpy as np
from tidyframe import Safely


@Safely()
def log_safely(x):
    return math.log(x)


def test_Safely_basic_success():
    result_log = log_safely(10)
    assert np.isclose(result_log['result'],
                      math.log(10)), 'Must result be True'
    assert result_log['error'] is None, 'Must result be None'


def test_Safely_basic_faie():
    result_log2 = log_safely(-10)
    assert np.isnan(result_log2['result']), 'Must result is True'
    assert result_log2['error'] is not None, 'Must result is True'


def test_Safely_classmethod_success():
    result_log3 = Safely.safely(math.log)(10)
    assert np.isclose(result_log3['result'],
                      math.log(10)), 'Must result is True'
    assert result_log3['error'] is None, 'Must result is True'


def test_Safe_classmethod_fail():
    result_log4 = Safely.safely(math.log)(-1)
    assert np.isnan(result_log4['result']), 'Must result is True'
    assert result_log4['error'] is not None, 'Must result is True'


def test_Safely_classmethod_change_default():
    Safely.otherwise_all = -1
    Safely.quiet_all = False
    result_log5 = Safely.safely(math.log)(-1)
    assert np.isclose(result_log5['result'], -1), 'Must result is True'
    assert result_log5['error'] is not None, 'Must result is True'


def test_Safely_print_exception():
    @Safely(otherwise=-1, quiet=False)
    def log_safely(x):
        return math.log(x)

    log_safely(-10)
