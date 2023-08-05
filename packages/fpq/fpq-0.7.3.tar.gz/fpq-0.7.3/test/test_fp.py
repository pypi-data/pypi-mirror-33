#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
import numpy as np
import sys
sys.path.append('../')
from fpq.fp import *


class TestFp(TestCase):

    def test__can_express_norm(self):
        import fpq.fp
        self.assertTrue(fpq.fp._can_express_norm(11, np.float16))
        self.assertFalse(fpq.fp._can_express_norm(12, np.float16))
        self.assertTrue(fpq.fp._can_express_norm(24, np.float32))
        self.assertFalse(fpq.fp._can_express_norm(25, np.float32))
        self.assertTrue(fpq.fp._can_express_norm(53, np.float64))
        self.assertFalse(fpq.fp._can_express_norm(54, np.float64))

    def test_encoding_decoding_between_fp16_and_uint16(self):
        dtypes = (np.float16, np.uint16)
        nbits = 12

        expected_enc = np.array([0x0d64, 0x0c91, 0x0bc7,
                                 0x03c7, 0x0491, 0x0564], dtype=dtypes[1])
        expected_dec = np.array([-100.123, -10.123, -1.123,
                                 1.123, 10.123, 100.123], dtype=dtypes[0])
        enc = encode_fp_to_uint(expected_dec, nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray)
                        and (enc.dtype == expected_enc.dtype)
                        and (enc.shape == expected_enc.shape))
        self.assertTrue(np.array_equal(enc, expected_enc))
        dec = decode_uint_to_fp(enc, nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray)
                        and (dec.dtype == expected_dec.dtype)
                        and (dec.shape == expected_dec.shape))
        self.assertTrue(np.allclose(dec, expected_dec, rtol=1e-01, atol=1e-02))

    def test_encoding_decoding_between_fp32_and_uint32(self):
        dtypes = (np.float32, np.uint32)
        nbits = 24

        expected_enc = np.array([0x00C2C83E, 0x00C121F7, 0x00BF8FBE,
                                 0x003F8FBE, 0x004121F7, 0x0042C83E], dtype=dtypes[1])
        expected_dec = np.array([-100.123, -10.123, -1.123,
                                 1.123, 10.123, 100.123], dtype=dtypes[0])
        enc = encode_fp_to_uint(expected_dec, nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray)
                        and (enc.dtype == expected_enc.dtype)
                        and (enc.shape == expected_enc.shape))
        self.assertTrue(np.array_equal(enc, expected_enc))
        dec = decode_uint_to_fp(enc, nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray)
                        and (dec.dtype == expected_dec.dtype)
                        and (dec.shape == expected_dec.shape))
        self.assertTrue(np.allclose(dec, expected_dec, rtol=1e-04, atol=1e-05))

    def test_encoding_decoding_between_fp64_and_uint64(self):
        dtypes = (np.float64, np.uint64)
        nbits = 48

        expected_enc = np.array([0x0000C05907DF3B64, 0x0000C0243EF9DB22, 0x0000BFF1F7CED916,
                                 0x00003FF1F7CED916, 0x000040243EF9DB22, 0x0000405907DF3B64], dtype=dtypes[1])
        expected_dec = np.array([-100.123, -10.123, -1.123,
                                 1.123, 10.123, 100.123], dtype=dtypes[0])
        enc = encode_fp_to_uint(expected_dec, nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray)
                        and (enc.dtype == expected_enc.dtype)
                        and (enc.shape == expected_enc.shape))
        self.assertTrue(np.array_equal(enc, expected_enc))
        dec = decode_uint_to_fp(enc, nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray)
                        and (dec.dtype == expected_dec.dtype)
                        and (dec.shape == expected_dec.shape))
        self.assertTrue(np.allclose(dec, expected_dec, rtol=1e-11, atol=1e-12))

    def test_encoding_decoding_between_fp_and_std_unorm(self):
        dtypes = (np.float32, np.uint8)
        nbits = 5

        expected_enc = dtypes[1](0b11111)
        expected_dec = dtypes[0](1.)
        enc = encode_fp_to_std_unorm(expected_dec, nbits=nbits)
        self.assertTrue(isinstance(enc, dtypes[1]))
        self.assertTrue(np.array_equal(enc, expected_enc))
        dec = decode_std_unorm_to_fp(enc, nbits=nbits)
        self.assertTrue(isinstance(dec, dtypes[0]))
        self.assertTrue(np.isclose(dec, expected_dec, rtol=0., atol=1e-1))

        expected_enc = np.array([0b00000, 0b01000, 0b11111], dtype=dtypes[1])
        expected_dec = np.array([0., 0.25, 1.], dtype=dtypes[0])
        enc = encode_fp_to_std_unorm(expected_dec, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray)
                        and (enc.dtype == expected_enc.dtype)
                        and (enc.shape == expected_enc.shape))
        self.assertTrue(np.array_equal(enc, expected_enc))
        dec = decode_std_unorm_to_fp(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray)
                        and (dec.dtype == expected_dec.dtype)
                        and (dec.shape == expected_dec.shape))
        self.assertTrue(np.allclose(dec, expected_dec, rtol=0., atol=1e-1))

        dtypes = (np.float32, np.uint8)
        nbits = 2
        expected_enc = np.array([0, 1, 2, 3], dtype=dtypes[1])
        expected_dec = np.array([0., 1./3., 2./3., 1.], dtype=dtypes[0])
        enc = encode_fp_to_std_unorm(expected_dec, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray)
                        and (enc.dtype == expected_enc.dtype)
                        and (enc.shape == expected_enc.shape))
        self.assertTrue(np.array_equal(enc, expected_enc))
        dec = decode_std_unorm_to_fp(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray)
                        and (dec.dtype == expected_dec.dtype)
                        and (dec.shape == expected_dec.shape))
        self.assertTrue(np.allclose(dec, expected_dec, rtol=0., atol=1e-1))

    def test_encoding_decoding_between_fp_and_std_snorm(self):
        dtypes = (np.float32, np.uint8)
        nbits = 5

        expected_enc = dtypes[1](0b11110)
        expected_dec = dtypes[0](1.)
        enc = encode_fp_to_std_snorm(expected_dec, nbits=nbits)
        self.assertTrue(isinstance(enc, dtypes[1]))
        self.assertTrue(np.array_equal(enc, expected_enc))
        dec = decode_std_snorm_to_fp(enc, nbits=nbits)
        self.assertTrue(isinstance(dec, dtypes[0]))
        self.assertTrue(np.isclose(dec, expected_dec, rtol=0., atol=1e-1))

        expected_enc = np.array([0b11111, 0b01001, 0b00001, 0b00000, 0b01000, 0b11110], dtype=dtypes[1])
        expected_dec = np.array([-1., -0.25, -0., 0., 0.25, 1.], dtype=dtypes[0])
        enc = encode_fp_to_std_snorm(expected_dec, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray)
                        and (enc.dtype == expected_enc.dtype)
                        and (enc.shape == expected_enc.shape))
        self.assertTrue(np.array_equal(enc, expected_enc))
        dec = decode_std_snorm_to_fp(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray)
                        and (dec.dtype == expected_dec.dtype)
                        and (dec.shape == expected_dec.shape))
        self.assertTrue(np.allclose(dec, expected_dec, rtol=0., atol=1e-1))

    def test_encoding_decoding_between_fp_and_ogl_snorm(self):
        dtypes = (np.float32, np.uint8)
        nbits = 5

        expected_enc = dtypes[1](0b01111)
        expected_dec = dtypes[0](1.)
        enc = encode_fp_to_ogl_snorm(expected_dec, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, dtypes[1]))
        self.assertTrue(np.array_equal(enc, expected_enc))
        dec = decode_ogl_snorm_to_fp(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, dtypes[0]))
        self.assertTrue(np.allclose(dec, expected_dec, rtol=0., atol=1e-1))

        expected_enc = np.array([0b10001, 0b11100, 0b00000, 0b00000, 0b00100, 0b01111], dtype=dtypes[1])
        expected_dec = np.array([-1., -0.25, -0., 0., 0.25, 1.], dtype=dtypes[0])
        enc = encode_fp_to_ogl_snorm(expected_dec, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray)
                        and (enc.dtype == expected_enc.dtype)
                        and (enc.shape == expected_enc.shape))
        self.assertTrue(np.array_equal(enc, expected_enc))
        dec = decode_ogl_snorm_to_fp(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray)
                        and (dec.dtype == expected_dec.dtype)
                        and (dec.shape == expected_dec.shape))
        self.assertTrue(np.allclose(dec, expected_dec, rtol=0., atol=1e-1))

    def test_encoding_decoding_between_fp_and_d3d_snorm(self):
        dtypes = (np.float32, np.uint8)
        nbits = 5

        expected_enc = dtypes[1](0b01111)
        expected_dec = dtypes[0](1.)
        enc = encode_fp_to_d3d_snorm(expected_dec, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, dtypes[1]))
        self.assertTrue(np.array_equal(enc, expected_enc))
        dec = decode_d3d_snorm_to_fp(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, dtypes[0]))
        self.assertTrue(np.allclose(dec, expected_dec, rtol=0., atol=1e-1))

        expected_enc = np.array([0b10001, 0b11100, 0b00000, 0b00000, 0b00100, 0b01111], dtype=dtypes[1])
        expected_dec = np.array([-1., -0.25, -0., 0., 0.25, 1.], dtype=dtypes[0])
        enc = encode_fp_to_d3d_snorm(expected_dec, dtype=dtypes[1], nbits=nbits)
        self.assertTrue(isinstance(enc, np.ndarray)
                        and (enc.dtype == expected_enc.dtype)
                        and (enc.shape == expected_enc.shape))
        self.assertTrue(np.array_equal(enc, expected_enc))
        dec = decode_d3d_snorm_to_fp(enc, dtype=dtypes[0], nbits=nbits)
        self.assertTrue(isinstance(dec, np.ndarray)
                        and (dec.dtype == expected_dec.dtype)
                        and (dec.shape == expected_dec.shape))
        self.assertTrue(np.allclose(dec, expected_dec, rtol=0., atol=1e-1))
