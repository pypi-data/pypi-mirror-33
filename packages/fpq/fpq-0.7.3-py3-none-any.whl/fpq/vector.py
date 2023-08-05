#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from . import utils
from . import fp
from . import numba_wrapper


def is_valid_format(dtype_f, dtype_u, nbits):
    assert (dtype_f().dtype.kind == 'f'), \
        '`dtype` of the argument `dtype_f` must be floating point types.'
    assert (dtype_u().dtype.kind == 'u'), \
        '`dtype` of the argument `dtype_ui` must be unsigned integer types.'

    remaining = dtype_u().itemsize * 8 - 2
    if (nbits < 2) or (nbits > ((remaining - 2) // 2)):
        return False
    if (remaining - nbits * 2) > (dtype_f().itemsize * 8):
        return False
    return nbits <= (2 + np.finfo(dtype_f).nmant)


def calc_breakdown_of_uint(dtype, nbits):
    '''Calculate a breakdown of an unsigned integer.'''
    assert (dtype().dtype.kind == 'u'), \
        '`dtype` of the argument `dtype` must be unsigned integer types.'

    remaining = dtype().itemsize * 8 - 2
    return 2, nbits, nbits, remaining - nbits * 2


def _encode_fp_to_uint(x, *, dtype, nbits):

    assert (x.dtype.kind == 'f'), \
        '`dtype` of the argument `x` must be floating point types.'
    assert (dtype().dtype.kind == 'u'), \
        '`dtype` of the argument `dtype` must be unsigned integer types.'

    if nbits <= 16:
        dtype_f = np.float16
    elif nbits <= 32:
        dtype_f = np.float32
    else:
        dtype_f = np.float64

    if x.dtype != dtype_f:
        x = dtype_f(x)

    enc = fp.encode_fp_to_uint(x, nbits=nbits)
    if enc.dtype != dtype:
        enc = dtype(enc)

    return enc


def _decode_uint_to_fp(x, *, dtype, nbits):

    assert (x.dtype.kind == 'u'), \
        '`dtype` of the argument `x` must be unsigned integer types.'
    assert (dtype().dtype.kind == 'f'), \
        '`dtype` of the argument `dtype` must be floating point types.'

    if nbits <= 16:
        dtype_u = np.uint16
    elif nbits <= 32:
        dtype_u = np.uint32
    else:
        dtype_u = np.uint64

    if x.dtype != dtype_u:
        x = dtype_u(x)

    dec = fp.decode_uint_to_fp(x, nbits=nbits)
    if dec.dtype != dtype:
        dec = dtype(dec)

    return dec


@numba_wrapper.avoid_mapping_to_py_types
@numba_wrapper.avoid_non_supported_types
@numba_wrapper.jit
def l2norm(v):
    '''Calculates the L2 norm.'''
    return np.sqrt(np.square(v[..., 0]) + np.square(v[..., 1]) + np.square(v[..., 2]))


@numba_wrapper.avoid_mapping_to_py_types
@numba_wrapper.avoid_non_supported_types
@numba_wrapper.jit
def _solve_remaining_component(x):
    '''Solve a remaining component of a unit vector'''
    return np.sqrt(x.dtype.type(1.) - np.square(x[0]) - np.square(x[1]))


def encode_vec_to_uint(v, *, dtype=np.uint64, nbits=20, encoder=fp.encode_fp_to_std_snorm):
    '''Encode vectors to unsigned integers.

    Args:
        v: Should be represented by three components of float, or an array of them.
        dtype: The type should be unsigned integer types.
        nbits: The number of bits to use.
        encoder: This is a function encodes a floating point to an unsigned integer.

    Returns:
        The resulting unsigned integers.

    Examples:
        >>> v = np.array([1., 2., 3.], dtype=np.float64)
        >>> encode_vec_to_uint(v, dtype=np.uint64, nbits=20)
    '''
    assert is_valid_format(v.dtype.type, dtype, nbits), 'Not a valid format.'

    # Get the maximum absolute component indices.
    max_abs_inds = utils.get_max_component_indices(np.absolute(v))

    # Normalize the vectors.
    norm = l2norm(v)
    nv = v / norm[..., None]

    # The sign of the maximum absolute component.
    sign = np.sign(nv[max_abs_inds])

    breakdown = calc_breakdown_of_uint(dtype, nbits)

    # Encoding for vector components.
    remaining = utils.remove_component(nv, indices=max_abs_inds) * sign[..., None]
    enc = encoder(remaining, dtype=dtype, nbits=breakdown[1])

    # Encoding for the vector norm.
    norm *= sign
    enc_n = _encode_fp_to_uint(norm, dtype=dtype, nbits=breakdown[3])

    return (dtype(max_abs_inds[-1]) << dtype(sum(breakdown[1:]))) \
           | (enc[..., 0] << dtype(sum(breakdown[2:]))) \
           | (enc[..., 1] << dtype(sum(breakdown[3:]))) \
           | enc_n


def decode_uint_to_vec(v, *, dtype=np.float64, nbits=20, decoder=fp.decode_std_snorm_to_fp):
    '''Decode unsigned integers to vectors.

    Args:
        v: Should be represented by uint, or an array of them.
        dtype: The type should be floating point types.
        nbits: The number of bits to use.
        decoder: This is a function decodes an unsigned integer to a floating point.

    Returns:
        The resulting vectors.

    Examples:
        >>> v = np.array([1., 2., 3.], dtype=np.float64)
        >>> enc = encode_vec_to_uint(v, dtype=np.uint64, nbits=20)
        >>> decode_uint_to_vec(enc, dtype=np.float64, nbits=20)
    '''
    assert is_valid_format(dtype, v.dtype.type, nbits), 'Not a valid format.'

    breakdown = calc_breakdown_of_uint(v.dtype.type, nbits)

    shifts = np.array([sum(breakdown[1:]), sum(breakdown[2:]), sum(breakdown[3:]), 0], dtype=v.dtype)
    masks = np.invert(v.dtype.type(np.iinfo(v.dtype).max) << np.array(breakdown, dtype=v.dtype))

    temp = (...,) + (None,) * v.ndim
    components = (v >> shifts[temp]) & masks[temp]

    # Decoding for the vector norm.
    dec_n = _decode_uint_to_fp(components[3], dtype=dtype, nbits=breakdown[3])

    # Decoding for vector components.
    dec = decoder(components[1:3], dtype=dtype, nbits=breakdown[1])
    c0 = _solve_remaining_component(dec) * dec_n
    c1 = dec[0] * dec_n
    c2 = dec[1] * dec_n

    max_c = components[0]
    permutation = [i for i in range(1, v.ndim+1)] + [0,]
    return np.where(max_c == 0, (c0, c1, c2),
                    np.where(max_c == 1, (c1, c0, c2), (c1, c2, c0))).transpose(permutation)
