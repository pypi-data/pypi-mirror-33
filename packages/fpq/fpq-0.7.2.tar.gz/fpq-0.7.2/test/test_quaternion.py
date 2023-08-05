#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
import math
import random
import numpy as np
import sys
sys.path.append('../')
from fpq.quaternion import *
import fpq.fp


class TestQuaternion(TestCase):
    @staticmethod
    def quat_from_axis_angle(axis, angle):
        axis_ = np.array(axis, dtype=np.float64)
        half_angle = angle * 0.5
        ret = np.empty(4)
        ret[0] = math.cos(half_angle)
        ret[1:4] = math.sin(half_angle) * axis_
        return ret

    @staticmethod
    def quat_are_same_rotation(q1, q2, *, atol=1e-08):
        return np.isclose(1., abs(np.dot(q1, q2)), rtol=0., atol=atol)

    @staticmethod
    def quat_random():
        u1 = random.random()
        r1 = math.sqrt(1. - u1)
        r2 = math.sqrt(u1)
        t1 = 2. * math.pi * random.random()  # u1
        t2 = 2. * math.pi * random.random()  # u2
        return np.array([r2 * math.cos(t2),
                         r1 * math.sin(t1),
                         r1 * math.cos(t1),
                         r2 * math.sin(t2)])

    def test_encoding_decoding_between_quat16_and_uint16(self):
        dtypes = (np.float16, np.uint16)

        q = self.quat_random()
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        self.assertTrue(self.quat_are_same_rotation(q, dec, atol=1e-01))

        q = np.array([self.quat_random() for _ in range(10)], dtype=dtypes[0])
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q, dec):
            self.assertTrue(self.quat_are_same_rotation(src, dst, atol=1e-01))

        q = np.array([self.quat_random() for _ in range(6)], dtype=dtypes[0])
        q = q.reshape(2, 3, 4)
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q.reshape(-1, 4), dec.reshape(-1, 4)):
            self.assertTrue(self.quat_are_same_rotation(src, dst, atol=1e-01))

        q = np.array([self.quat_random() for _ in range(12)], dtype=dtypes[0])
        q = q.reshape(2, 2, 3, 4)
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q.reshape(-1, 4), dec.reshape(-1, 4)):
            self.assertTrue(self.quat_are_same_rotation(src, dst, atol=1e-01))

    def test_encoding_decoding_between_quat32_and_uint32(self):
        dtypes = (np.float32, np.uint32)

        q = self.quat_random()
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        self.assertTrue(self.quat_are_same_rotation(q, dec, atol=1e-05))

        q = np.array([self.quat_random() for _ in range(10)], dtype=dtypes[0])
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q, dec):
            self.assertTrue(self.quat_are_same_rotation(src, dst, atol=1e-05))

        q = np.array([self.quat_random() for _ in range(6)], dtype=dtypes[0])
        q = q.reshape(2, 3, 4)
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q.reshape(-1, 4), dec.reshape(-1, 4)):
            self.assertTrue(self.quat_are_same_rotation(src, dst, atol=1e-05))

        q = np.array([self.quat_random() for _ in range(12)], dtype=dtypes[0])
        q = q.reshape(2, 2, 3, 4)
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q.reshape(-1, 4), dec.reshape(-1, 4)):
            self.assertTrue(self.quat_are_same_rotation(src, dst, atol=1e-05))

    def test_encoding_decoding_between_quat64_and_uint64(self):
        dtypes = (np.float64, np.uint64)

        q = self.quat_random()
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        self.assertTrue(self.quat_are_same_rotation(q, dec, atol=1e-07))

        q = np.array([self.quat_random() for _ in range(10)], dtype=dtypes[0])
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q, dec):
            self.assertTrue(self.quat_are_same_rotation(src, dst, atol=1e-07))

        q = np.array([self.quat_random() for _ in range(6)], dtype=dtypes[0])
        q = q.reshape(2, 3, 4)
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q.reshape(-1, 4), dec.reshape(-1, 4)):
            self.assertTrue(self.quat_are_same_rotation(src, dst, atol=1e-07))

        q = np.array([self.quat_random() for _ in range(12)], dtype=dtypes[0])
        q = q.reshape(2, 2, 3, 4)
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q.reshape(-1, 4), dec.reshape(-1, 4)):
            self.assertTrue(self.quat_are_same_rotation(src, dst, atol=1e-07))

    def test_encoding_decoding_between_quat_and_uint_by_ogl(self):
        encoder = fpq.fp.encode_fp_to_ogl_snorm
        decoder = fpq.fp.decode_ogl_snorm_to_fp
        dtypes = (np.float64, np.uint64)

        q = self.quat_random()
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        self.assertTrue(self.quat_are_same_rotation(q, dec))

        q = np.array([self.quat_random() for _ in range(10)], dtype=dtypes[0])
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q, dec):
            self.assertTrue(self.quat_are_same_rotation(src, dst))

        q = np.array([self.quat_random() for _ in range(6)], dtype=dtypes[0])
        q = q.reshape(2, 3, 4)
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q.reshape(-1, 4), dec.reshape(-1, 4)):
            self.assertTrue(self.quat_are_same_rotation(src, dst))

        q = np.array([self.quat_random() for _ in range(12)], dtype=dtypes[0])
        q = q.reshape(2, 2, 3, 4)
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q.reshape(-1, 4), dec.reshape(-1, 4)):
            self.assertTrue(self.quat_are_same_rotation(src, dst))

    def test_encoding_decoding_between_quat_and_uint_by_d3d(self):
        encoder = fpq.fp.encode_fp_to_d3d_snorm
        decoder = fpq.fp.decode_d3d_snorm_to_fp
        dtypes = (np.float64, np.uint64)

        q = self.quat_random()
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        self.assertTrue(self.quat_are_same_rotation(q, dec))

        q = np.array([self.quat_random() for _ in range(10)], dtype=dtypes[0])
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q, dec):
            self.assertTrue(self.quat_are_same_rotation(src, dst))

        q = np.array([self.quat_random() for _ in range(6)], dtype=dtypes[0])
        q = q.reshape(2, 3, 4)
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q.reshape(-1, 4), dec.reshape(-1, 4)):
            self.assertTrue(self.quat_are_same_rotation(src, dst))

        q = np.array([self.quat_random() for _ in range(12)], dtype=dtypes[0])
        q = q.reshape(2, 2, 3, 4)
        enc = encode_quat_to_uint(q, dtype=dtypes[1])
        dec = decode_uint_to_quat(enc, dtype=dtypes[0])
        for src, dst in zip(q.reshape(-1, 4), dec.reshape(-1, 4)):
            self.assertTrue(self.quat_are_same_rotation(src, dst))
