#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from . import utils
from . import fp
from . import numba_wrapper


@numba_wrapper.avoid_mapping_to_py_types
@numba_wrapper.avoid_non_supported_types
@numba_wrapper.jit
def _solve_remaining_component(x):
    '''Solve a remaining component of a unit vector'''
    return np.sqrt(x.dtype.type(1.) - np.square(x[0]) - np.square(x[1]) - np.square(x[2]))


def encode_quat_to_uint(q, *, dtype=np.uint64, encoder=fp.encode_fp_to_std_snorm):
    '''Encode Quaternions to unsigned integers.

    Args:
        q: Should be represented by four components of float, or an array of them.
        dtype: The type should be unsigned integer types.
        encoder: This is a function encodes a floating point to an unsigned integer.

    Returns:
        The resulting unsigned integers.

    Examples:
        >>> q = np.array([1., 0., 0., 0.], dtype=np.float64)
        >>> encode_quat_to_uint(q, dtype=np.uint64)
    '''
    assert (isinstance(q, np.ndarray) and (q.dtype.kind == 'f')), \
        '`dtype` of the argument `q` should be floating point types.'
    assert (dtype().dtype.kind == 'u'), \
        '`dtype` of the argument `dtype` should be unsigned integer types.'

    nbits_per_component = ((dtype().dtype.itemsize * 8) - 2) // 3

    max_abs_inds = utils.get_max_component_indices(np.absolute(q))
    sign = np.sign(q[max_abs_inds])
    remaining = sign[..., None] * utils.remove_component(q, indices=max_abs_inds)

    # [-1/sqrt(2), +1/sqrt(2)] -> [-1, +1]
    src_max = np.reciprocal(np.sqrt(q.dtype.type(2.)))
    src_min = -src_max
    remaining = utils.remap(remaining, src_min, src_max, q.dtype.type(-1.), q.dtype.type(1.))

    enc = encoder(remaining, dtype=dtype, nbits=nbits_per_component)

    return (dtype(max_abs_inds[-1]) << dtype(nbits_per_component * 3)) \
           | (enc[..., 0] << dtype(nbits_per_component * 2)) \
           | (enc[..., 1] << dtype(nbits_per_component)) \
           | enc[..., 2]


def decode_uint_to_quat(q, *, dtype=np.float64, decoder=fp.decode_std_snorm_to_fp):
    '''Decode unsigned integers to Quaternions.

    Args:
        q: Should be represented by uint, or an array of them.
        dtype: The type should be floating point types.
        decoder: This is a function decodes an unsigned integer to a floating point.

    Returns:
        The resulting Quaternions.

    Examples:
        >>> q = np.array([1., 0., 0., 0.], dtype=np.float64)
        >>> enc = encode_quat_to_uint(q, dtype=np.uint64)
        >>> decode_uint_to_quat(enc, dtype=np.float64)
    '''
    assert (q.dtype.kind == 'u'), \
        '`dtype` of the argument `q` should be unsigned integer types.'
    assert (dtype().dtype.kind == 'f'), \
        '`dtype` of the argument `dtype` should be floating point types.'

    bits_per_component = ((q.dtype.itemsize * 8) - 2) // 3

    shifts = np.array([bits_per_component * 3,
                       bits_per_component * 2,
                       bits_per_component,
                       0], dtype=q.dtype)
    mask = np.invert(q.dtype.type(np.iinfo(q.dtype).max) << q.dtype.type(bits_per_component))
    masks = np.array([0x3, mask, mask, mask], dtype=q.dtype)

    temp = (...,) + (None,) * q.ndim
    components = (q >> shifts[temp]) & masks[temp]

    # Decoding for quaternion components.
    dec = decoder(components[1:4], dtype=dtype, nbits=bits_per_component)

    # [-1, +1] -> [-1/sqrt(2), +1/sqrt(2)]
    dst_max = np.reciprocal(np.sqrt(dtype(2.)))
    dst_min = -dst_max
    dec = utils.remap(dec, dtype(-1.), dtype(1.), dst_min, dst_max)

    c0 = _solve_remaining_component(dec)
    c1 = dec[0]
    c2 = dec[1]
    c3 = dec[2]

    max_c = components[0]
    permutation = [i for i in range(1, q.ndim + 1)] + [0, ]
    return np.where(max_c == 0, (c0, c1, c2, c3),
                    np.where(max_c == 1, (c1, c0, c2, c3),
                             np.where(max_c == 2, (c1, c2, c0, c3), (c1, c2, c3, c0)))).transpose(permutation)
