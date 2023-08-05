#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
import numpy as np
import sys
sys.path.append('../')
from fpq.utils import *


class TestUtils(TestCase):

    def test_get_max_component_indices(self):
        arr = np.array([1., 2., 3., 4.])
        actual = get_max_component_indices(arr)
        expected = (3,)
        self.assertTrue(isinstance(actual, tuple))
        self.assertTrue(np.array_equal(actual, expected))

        arr = np.array([[1., 2., 3., 4.],
                        [3., 2., 1., 0.]])
        actual = get_max_component_indices(arr)
        expected = (np.array([0, 1]), np.array([3, 0]))
        self.assertTrue(isinstance(actual, tuple))
        self.assertTrue(np.array_equal(actual, expected))

    def test_remove_max_component(self):
        arr = np.array([1., 2., 3., 4.])
        actual = remove_component(arr, indices=(3,))
        expected = np.array([1., 2., 3.])
        self.assertTrue(isinstance(actual, np.ndarray))
        self.assertTrue(np.array_equal(actual, expected))

        arr = np.array([[1., 2., 3., 4.],
                        [3., 2., 1., 0.]])
        actual = remove_component(arr, indices=(np.array([0, 1]), np.array([3, 0])))
        expected = np.array([[1., 2., 3.],
                             [2., 1., 0.]])
        self.assertTrue(isinstance(actual, np.ndarray))
        self.assertTrue(np.array_equal(actual, expected))

    def test_remap(self):
        src_min, src_max = np.float64(0.), np.float64(10.)
        dst_min, dst_max = np.float64(0.), np.float64(1.)
        src_val = np.float64(10.)
        dst_val = remap(src_val, src_min, src_max, dst_min, dst_max)
        self.assertTrue(isinstance(dst_val, np.float64))
        self.assertTrue(dst_min <= dst_val <= dst_max)

        src_min, src_max = np.float64(-10.), np.float64(10.)
        dst_min, dst_max = np.float64(-1.), np.float64(1.)
        src_val = np.float64(-10.)
        dst_val = remap(src_val, src_min, src_max, dst_min, dst_max)
        self.assertTrue(isinstance(dst_val, np.float64))
        self.assertTrue(dst_min <= dst_val <= dst_max)

        src_min, src_max = np.float64(0.), np.float64(10.)
        dst_min, dst_max = np.float64(0.), np.float64(1.)
        src_val = np.array([0., 2.5, 5., 7.5, 10.], dtype=np.float64)
        dst_val = remap(src_val, src_min, src_max, dst_min, dst_max)
        self.assertTrue(isinstance(dst_val, np.ndarray))
        self.assertTrue(np.all(dst_val >= dst_min) and np.all(dst_val <= dst_max))

        src_min, src_max = np.float64(-10.), np.float64(10.)
        dst_min, dst_max = np.float64(-1.), np.float64(1.)
        src_val = np.array([-10, -7.5, -5., -2.5, 0., 2.5, 5., 7.5, 10.], dtype=np.float64)
        dst_val = remap(src_val, src_min, src_max, dst_min, dst_max)
        self.assertTrue(isinstance(dst_val, np.ndarray))
        self.assertTrue(np.all(dst_val >= dst_min) and np.all(dst_val <= dst_max))
