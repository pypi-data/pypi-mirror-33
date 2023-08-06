#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
import sys
sys.path.append('../')
from perfbench.utils import *


class TestUtils(TestCase):
    @classmethod
    def calc_list_length(cls, element):
        if isinstance(element, list):
            return sum([cls.calc_list_length(i) for i in element])
        return 1

    def test_is_interactive(self):
        actual = is_interactive()
        self.assertTrue(isinstance(actual, bool))
        self.assertFalse(actual)

    def test_create_empty_array_of_shape(self):
        actual = create_empty_array_of_shape((2, 3))
        self.assertTrue(isinstance(actual, list))
        self.assertTrue(self.calc_list_length(actual) == 6)

        actual = create_empty_array_of_shape((2, 3, 4))
        self.assertTrue(isinstance(actual, list))
        self.assertTrue(self.calc_list_length(actual) == 24)

        actual = create_empty_array_of_shape((2, 3, 4, 5))
        self.assertTrue(isinstance(actual, list))
        self.assertTrue(self.calc_list_length(actual) == 120)
