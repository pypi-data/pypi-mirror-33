#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
import types
import functools
import numpy as np


try:
    from numba.targets.registry import CPUDispatcher
    from numba import jit

    IS_ENABLED_NUMBA = True

except ImportError:
    import warnings
    warning_text = \
        '\n\n' + '!' * 79 + '\n' + \
        'Could not import from numba.\n' + \
        'If numba is not installed, performance can be degraded in some functions.' + \
        '\n' + '!' * 79 + '\n'
    warnings.warn(warning_text)

    def _identity_decorator(*args, **kwargs):
        if (len(args) == 1) and isinstance(args[0], types.FunctionType):
            return args[0]

        def wrapper(fn):
            return fn

        return wrapper

    jit = _identity_decorator

    IS_ENABLED_NUMBA = False


def avoid_mapping_to_py_types(index_or_function=0):
    '''Avoid mapping to Python types.'''
    if isinstance(index_or_function, types.FunctionType) \
            or (IS_ENABLED_NUMBA and isinstance(index_or_function, CPUDispatcher)):
        func = index_or_function
        index = 0
    else:
        func = None
        index = index_or_function

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            ret = fn(*args, **kwargs)
            if isinstance(ret, (np.ndarray, np.float16)):
                return ret
            else:
                return args[index].dtype.type(ret)

        return wrapper if IS_ENABLED_NUMBA else fn

    return decorator if func is None else decorator(func)


def avoid_non_supported_types(index_or_function=0):
    '''Avoid non-supported types.'''
    if isinstance(index_or_function, types.FunctionType) \
            or (IS_ENABLED_NUMBA and isinstance(index_or_function, CPUDispatcher)):
        func = index_or_function
        index = 0
    else:
        func = None
        index = index_or_function

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if args[index].dtype == np.float16:
                return fn.py_func(*args, **kwargs)
            else:
                return fn(*args, **kwargs)

        return wrapper if IS_ENABLED_NUMBA else fn

    return decorator if func is None else decorator(func)
