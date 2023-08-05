#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from . import numba_wrapper


def get_max_component_indices(x):
    '''Returns the indices of the maximum components.

    Args:
        x: Input array.

    Returns:
        The resulting indices.
    '''
    inds1 = x.argmax(axis=-1)
    inds2 = np.indices(inds1.shape)
    return tuple(np.concatenate((inds2, inds1[None, ...])))


def remove_component(x, *, indices):
    '''Removes components at the specified indices.

    Args:
        x: Input array.
        indices: Indices refers to components to remove from `x`.

    Returns:
        Returns a new array excluded by `indices`.
    '''
    ma = np.ma.array(x, mask=False)
    ma.mask[indices] = True
    shape = x.shape[:-1] + (x.shape[-1] - 1,)
    return ma.compressed().reshape(shape)


@numba_wrapper.avoid_mapping_to_py_types
@numba_wrapper.avoid_non_supported_types
@numba_wrapper.jit
def remap(x, src_min, src_max, dst_min, dst_max):
    '''Maps values from [`src_min`, `src_max`]  to [`dst_min`, `dst_max`].

    Args:
        x: The incoming value to be converted.
        src_min: Lower bound of the value current range.
        src_max: Upper bound of the value current range.
        dst_min: Lower bound of the value target range.
        dst_max: Upper bound of the value target range.

    Returns:
        The resulting value.
    '''
    return (x - src_min) * ((dst_max - dst_min) / (src_max - src_min)) + dst_min


@numba_wrapper.avoid_mapping_to_py_types
@numba_wrapper.avoid_non_supported_types
@numba_wrapper.jit
def rint(x):
    '''Wrapper function for `numpy.rint`.'''
    return np.rint(x)
