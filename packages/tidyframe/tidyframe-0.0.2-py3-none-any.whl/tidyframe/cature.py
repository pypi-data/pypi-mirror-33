""" Deal with Function Exceptions """

import numpy as np


class Possibly(object):
    """Cature Exception if function exception occurred

    if function result occur exception then this decorator help you cature
    and return specified value(defaule: numpy.NaN)
    """
    otherwise_all = np.NaN
    quiet_all = True

    def __init__(self, otherwise=np.NaN, quiet=True):
        self.otherwise = otherwise
        self.quiet = quiet

    def __call__(self, func):
        def result_func(*args, **kargs):
            """ Catch all Function Exception """
            try:
                result = func(*args, **kargs)
            except Exception as e:
                result = self.otherwise
                if not self.quiet:
                    print(e)
            return result

        return result_func

    @classmethod
    def possibly(cls, func):
        """ class method for Catch all Function Exception """

        def result_func(*args, **kargs):
            try:
                result = func(*args, **kargs)
            except Exception as e:
                result = cls.otherwise_all
                if not cls.quiet_all:
                    print(e)
            return result

        return result_func


class Safely(object):
    """Cature Exception if function exception occurred

    This decorator will change function result to dict with two key.
    result: function result if no exception occurred, None if exception occurred
    error: None if no exception occurred, exception string if exception occurred
    """
    otherwise_all = np.NaN
    quiet_all = True

    def __init__(self, otherwise=np.NaN, quiet=True):
        self.otherwise = otherwise
        self.quiet = quiet

    def __call__(self, func):
        def result_func(*args, **kargs):
            """ Catch all Function Exception """
            result_dict = {}
            try:
                result_dict['result'] = func(*args, **kargs)
                result_dict['error'] = None
            except Exception as e:
                result_dict['result'] = self.otherwise
                result_dict['error'] = str(e)
                if not self.quiet:
                    print(e)
            return result_dict

        return result_func

    @classmethod
    def safely(cls, func):
        """ class method for Catch all Function Exception """

        def result_func(*args, **kargs):
            result_dict = {}
            try:
                result_dict['result'] = func(*args, **kargs)
                result_dict['error'] = None
            except Exception as e:
                result_dict['result'] = cls.otherwise_all
                result_dict['error'] = str(e)
                if not cls.quiet_all:
                    print(e)
            return result_dict

        return result_func
