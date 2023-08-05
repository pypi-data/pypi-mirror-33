#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from unittest import TestCase
from itertools import chain
import numpy as np
from numpy.lib import NumpyVersion
import sys
sys.path.append('../')
from fpq.vector import *
import fpq.fp


class TestVector(TestCase):

    def test_is_valid_format(self):
        # float : uint8
        self.assertTrue(is_valid_format(np.float16, np.uint8, 2))
        self.assertTrue(is_valid_format(np.float32, np.uint8, 2))
        self.assertTrue(is_valid_format(np.float64, np.uint8, 2))

        for nbits in chain(range(2), range(3,9)):
            self.assertFalse(is_valid_format(np.float16, np.uint8, nbits))
            self.assertFalse(is_valid_format(np.float32, np.uint8, nbits))
            self.assertFalse(is_valid_format(np.float64, np.uint8, nbits))

        # float16 : uint16
        for nbits in range(2,7):
            self.assertTrue(is_valid_format(np.float16, np.uint16, nbits))

        for nbits in chain(range(2), range(8,17)):
            self.assertFalse(is_valid_format(np.float16, np.uint16, nbits))

        # float16 : uint32
        for nbits in range(7,13):
            self.assertTrue(is_valid_format(np.float16, np.uint32, nbits))

        for nbits in chain(range(7), range(13,33)):
            self.assertFalse(is_valid_format(np.float16, np.uint32, nbits))

        # float16 : uint64
        for nbits in range(65):
            self.assertFalse(is_valid_format(np.float16, np.uint64, nbits))

        # float32 : uint16
        for nbits in range(2,7):
            self.assertTrue(is_valid_format(np.float32, np.uint16, nbits))

        for nbits in chain(range(2), range(8,17)):
            self.assertFalse(is_valid_format(np.float32, np.uint16, nbits))

        # float32 : uint32
        for nbits in range(2,15):
            self.assertTrue(is_valid_format(np.float32, np.uint32, nbits))

        for nbits in chain(range(2), range(16,33)):
            self.assertFalse(is_valid_format(np.float32, np.uint32, nbits))

        # float32 : uint64
        for nbits in range(15,26):
            self.assertTrue(is_valid_format(np.float32, np.uint64, nbits))

        for nbits in chain(range(15), range(26,65)):
            self.assertFalse(is_valid_format(np.float32, np.uint64, nbits))

        # float64 : uint16
        for nbits in range(2,7):
            self.assertTrue(is_valid_format(np.float64, np.uint16, nbits))

        for nbits in chain(range(2), range(7,17)):
            self.assertFalse(is_valid_format(np.float64, np.uint16, nbits))

        # float64 : uint32
        for nbits in range(2,15):
            self.assertTrue(is_valid_format(np.float64, np.uint32, nbits))

        for nbits in chain(range(2), range(15,33)):
            self.assertFalse(is_valid_format(np.float64, np.uint32, nbits))

        # float64 : uint64
        for nbits in range(2,31):
            self.assertTrue(is_valid_format(np.float64, np.uint64, nbits))

        for nbits in chain(range(2), range(31,65)):
            self.assertFalse(is_valid_format(np.float64, np.uint64, nbits))

    def test_calc_breakdown_of_uint(self):
        # uint8
        expected = (2,2,2,2)
        actual = calc_breakdown_of_uint(dtype=np.uint8, nbits=2)
        self.assertTrue(isinstance(actual, tuple))
        self.assertTrue(np.array_equal(actual, expected))

        # uint16
        expected = ((2, 2, 2, 10),
                    (2, 3, 3, 8),
                    (2, 4, 4, 6),
                    (2, 5, 5, 4),
                    (2, 6, 6, 2))
        for i, nbits in enumerate(range(2,7)):
            actual = calc_breakdown_of_uint(dtype=np.uint16, nbits=nbits)
            self.assertTrue(isinstance(actual, tuple))
            self.assertTrue(np.array_equal(actual, expected[i]))

        # uint32
        expected = ((2, 2, 2, 26), (2, 3, 3, 24), (2, 4, 4, 22),
                    (2, 5, 5, 20), (2, 6, 6, 18), (2, 7, 7, 16),
                    (2, 8, 8, 14), (2, 9, 9, 12), (2, 10, 10, 10),
                    (2, 11, 11, 8), (2, 12, 12, 6), (2, 13, 13, 4),
                    (2, 14, 14, 2))

        for i, nbits in enumerate(range(2,15)):
            actual = calc_breakdown_of_uint(dtype=np.uint32, nbits=nbits)
            self.assertTrue(isinstance(actual, tuple))
            self.assertTrue(np.array_equal(actual, expected[i]))

        # uint64
        expected = ((2, 2, 2, 58), (2, 3, 3, 56), (2, 4, 4, 54),
                    (2, 5, 5, 52), (2, 6, 6, 50), (2, 7, 7, 48),
                    (2, 8, 8, 46), (2, 9, 9, 44),(2, 10, 10, 42),
                    (2, 11, 11, 40), (2, 12, 12, 38), (2, 13, 13, 36),
                    (2, 14, 14, 34), (2, 15, 15, 32), (2, 16, 16, 30),
                    (2, 17, 17, 28), (2, 18, 18, 26), (2, 19, 19, 24),
                    (2, 20, 20, 22), (2, 21, 21, 20), (2, 22, 22, 18),
                    (2, 23, 23, 16), (2, 24, 24, 14), (2, 25, 25, 12),
                    (2, 26, 26, 10), (2, 27, 27, 8), (2, 28, 28, 6),
                    (2, 29, 29, 4), (2, 30, 30, 2))
        for i, nbits in enumerate(range(2,31)):
            actual = calc_breakdown_of_uint(dtype=np.uint64, nbits=nbits)
            self.assertTrue(isinstance(actual, tuple))
            self.assertTrue(np.array_equal(actual, expected[i]))

    @unittest.skipIf(NumpyVersion(np.__version__) < '1.11.2', 'not supported in this numpy version')
    def test_encoding_decoding_between_vec16_and_uint32(self):
        dtypes = (np.float16, np.uint32)
        nbits = 10

        expected = np.array([-50, 30, 20], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, dtypes[1]))
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-01, atol=1e-02))

        expected = np.array([[10, 20, 30],
                             [-40, 30, 20]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-01, atol=1e-02))

        expected = np.array([[[10, 20, 30],
                              [-40, 30, 20]],
                             [[10, 20, 60],
                              [-50, 30, 20]]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-01, atol=1e-02))

        expected = np.array([[[[10, 20, 30],
                               [-40, 30, 20]],
                              [[10, 20, 90],
                               [-50, 30, 20]]],
                             [[[10, 20, 30],
                               [-40, 30, 20]],
                              [[10, 20, 60],
                               [-80, 30, 20]]]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-01, atol=1e-02))

    def test_encoding_decoding_between_vec32_and_uint32(self):
        dtypes = (np.float32, np.uint32)
        nbits = 10

        expected = np.array([-50, 30, 20], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, dtypes[1]))
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-01, atol=1e-02))

        expected = np.array([[10, 20, 30],
                             [-40, 30, 20]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-01, atol=1e-02))

        expected = np.array([[[10, 20, 30],
                              [-40, 30, 20]],
                             [[10, 20, 60],
                              [-50, 30, 20]]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-01, atol=1e-02))

        expected = np.array([[[[10, 20, 30],
                               [-40, 30, 20]],
                              [[10, 20, 90],
                               [-50, 30, 20]]],
                             [[[10, 20, 30],
                               [-40, 30, 20]],
                              [[10, 20, 60],
                               [-80, 30, 20]]]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-01, atol=1e-02))

    def test_encoding_decoding_between_vec32_and_uint64(self):
        dtypes = (np.float32, np.uint64)
        nbits = 20

        expected = np.array([-50, 30, 20], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, dtypes[1]))
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

        expected = np.array([[10, 20, 30],
                             [-40, 30, 20]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

        expected = np.array([[[10, 20, 30],
                              [-40, 30, 20]],
                             [[10, 20, 60],
                              [-50, 30, 20]]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

        expected = np.array([[[[10, 20, 30],
                               [-40, 30, 20]],
                              [[10, 20, 90],
                               [-50, 30, 20]]],
                             [[[10, 20, 30],
                               [-40, 30, 20]],
                              [[10, 20, 60],
                               [-80, 30, 20]]]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

    def test_encoding_decoding_between_vec64_and_uint64(self):
        dtypes = (np.float64, np.uint64)
        nbits = 20

        expected = np.array([-50, 30, 20], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, dtypes[1]))
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

        expected = np.array([[10, 20, 30],
                             [-40, 30, 20]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

        expected = np.array([[[10, 20, 30],
                              [-40, 30, 20]],
                             [[10, 20, 60],
                              [-50, 30, 20]]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

        expected = np.array([[[[10, 20, 30],
                               [-40, 30, 20]],
                              [[10, 20, 90],
                               [-50, 30, 20]]],
                             [[[10, 20, 30],
                               [-40, 30, 20]],
                              [[10, 20, 60],
                               [-80, 30, 20]]]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

    def test_encoding_decoding_between_vec_and_uint_by_ogl(self):
        encoder = fpq.fp.encode_fp_to_ogl_snorm
        decoder = fpq.fp.decode_ogl_snorm_to_fp

        dtypes = (np.float64, np.uint64)
        nbits = 20

        expected = np.array([-50, 30, 20], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits, encoder=encoder)
        self.assertTrue(isinstance(enc, dtypes[1]))
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits, decoder=decoder)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

        expected = np.array([[10, 20, 30],
                             [-40, 30, 20]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits, encoder=encoder)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits, decoder=decoder)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

        expected = np.array([[[10, 20, 30],
                              [-40, 30, 20]],
                             [[10, 20, 60],
                              [-50, 30, 20]]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits, encoder=encoder)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits, decoder=decoder)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

        expected = np.array([[[[10, 20, 30],
                               [-40, 30, 20]],
                              [[10, 20, 90],
                               [-50, 30, 20]]],
                             [[[10, 20, 30],
                               [-40, 30, 20]],
                              [[10, 20, 60],
                               [-80, 30, 20]]]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits, encoder=encoder)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits, decoder=decoder)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

    def test_encoding_decoding_between_vec_and_uint_by_d3d(self):
        encoder = fpq.fp.encode_fp_to_d3d_snorm
        decoder = fpq.fp.decode_d3d_snorm_to_fp

        dtypes = (np.float64, np.uint64)
        nbits = 20

        expected = np.array([-50, 30, 20], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits, encoder=encoder)
        self.assertTrue(isinstance(enc, dtypes[1]))
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits, decoder=decoder)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

        expected = np.array([[10, 20, 30],
                             [-40, 30, 20]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits, encoder=encoder)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits, decoder=decoder)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

        expected = np.array([[[10, 20, 30],
                              [-40, 30, 20]],
                             [[10, 20, 60],
                              [-50, 30, 20]]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits, encoder=encoder)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits, decoder=decoder)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))

        expected = np.array([[[[10, 20, 30],
                               [-40, 30, 20]],
                              [[10, 20, 90],
                               [-50, 30, 20]]],
                             [[[10, 20, 30],
                               [-40, 30, 20]],
                              [[10, 20, 60],
                               [-80, 30, 20]]]], dtype=dtypes[0])
        enc = encode_vec_to_uint(expected, dtype=dtypes[1], nbits=nbits, encoder=encoder)
        self.assertTrue(isinstance(enc, np.ndarray))
        self.assertTrue(enc.dtype == dtypes[1])
        dec = decode_uint_to_vec(enc, dtype=dtypes[0], nbits=nbits, decoder=decoder)
        self.assertTrue(isinstance(dec, np.ndarray))
        self.assertTrue(dec.dtype == dtypes[0])
        self.assertTrue(np.allclose(dec, expected, rtol=1e-03, atol=1e-04))
