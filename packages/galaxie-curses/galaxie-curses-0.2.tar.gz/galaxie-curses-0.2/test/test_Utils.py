#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import os
from GLXCurses.Utils import clamp_to_zero
from GLXCurses.Utils import clamp
from GLXCurses.Utils import resize_text_wrap_char
from GLXCurses.Utils import resize_text
from GLXCurses.Utils import glxc_type
from GLXCurses.Utils import new_id
from GLXCurses.Utils import is_valid_id
from GLXCurses.Utils import merge_dicts

from GLXCurses import Window


# Unittest
class TestUtils(unittest.TestCase):

    def test_glxc_type(self):
        """Test Utils.glxc_type()"""
        self.assertTrue(glxc_type(Window()))
        self.assertFalse(glxc_type(int()))
        self.assertFalse(glxc_type())

    def test_clamp_to_zero(self):
        """Test Utils.clamp_to_zero()"""
        self.assertEqual(0, clamp_to_zero(None))
        self.assertEqual(0, clamp_to_zero(-42))
        self.assertEqual(0, clamp_to_zero(0))
        self.assertEqual(42, clamp_to_zero(42))
        self.assertRaises(TypeError, clamp_to_zero, float(42.42))

    def test_clamp(self):
        """Test Utils.clamp()"""
        self.assertEqual(42, clamp(value=1, smallest=42, largest=100))
        self.assertEqual(42.0, clamp(value=1.0, smallest=42, largest=100))

        self.assertEqual(42, clamp(value=100, smallest=0, largest=42))
        self.assertEqual(42.0, clamp(value=100.0, smallest=0, largest=42))

        self.assertRaises(TypeError, clamp, value=str(''), smallest=0, largest=42)
        self.assertRaises(TypeError, clamp, value=100, smallest=str(''), largest=42)
        self.assertRaises(TypeError, clamp, value=100, smallest=0, largest=str(''))

    def test_resize_text_wrap_char(self):
        """Test Utils.clamp_to_zero()"""
        text = "123456789"
        width = 3
        self.assertEqual("123", resize_text_wrap_char(text, width))
        width = 3
        self.assertEqual("123456789", resize_text_wrap_char(text, 10))
        # Test Error
        self.assertRaises(TypeError, resize_text_wrap_char, text=text, max_width=str('Hello'))
        self.assertRaises(TypeError, resize_text_wrap_char, text=int(2), max_width=3)

    def test_resize_text(self):
        """Test Utils.clamp_to_zero()"""
        text = "123456789"
        width = 10
        self.assertEqual(text, resize_text(text, width, '~'))
        width = 9
        self.assertEqual(text, resize_text(text, width, '~'))
        width = 8
        self.assertEqual('123~789', resize_text(text, width, '~'))
        width = 7
        self.assertEqual('123~789', resize_text(text, width, '~'))
        width = 6
        self.assertEqual('12~89', resize_text(text, width, '~'))
        width = 5
        self.assertEqual('12~89', resize_text(text, width, '~'))
        width = 4
        self.assertEqual('1~9', resize_text(text, width, '~'))
        width = 3
        self.assertEqual('1~9', resize_text(text, width, '~'))
        width = 2
        self.assertEqual('19', resize_text(text, width, '~'))
        width = 1
        self.assertEqual('1', resize_text(text, width, '~'))
        width = 0
        self.assertEqual('', resize_text(text, width, '~'))
        width = -1
        self.assertEqual('', resize_text(text, width, '~'))

        # Test Error
        self.assertRaises(TypeError, resize_text, text=text, max_width=width, separator=int(42))
        self.assertRaises(TypeError, resize_text, text=text, max_width='coucou', separator='~')
        self.assertRaises(TypeError, resize_text, text=int(42), max_width=width, separator='~')

    def test_id_generator(self):
        """Test Utils.id_generator()"""
        id_1 = new_id()
        self.assertTrue(is_valid_id(id_1))
        self.assertEqual(len(id_1), 8)
        # max_iteration = 10000000 - Take 99.114s  on Intel(R) Core(TM) i7-2860QM CPU @ 2.50GHz
        # max_iteration = 1000000  - Take 9.920s   on Intel(R) Core(TM) i7-2860QM CPU @ 2.50GHz
        # max_iteration = 100000   - Take 0.998s   on Intel(R) Core(TM) i7-2860QM CPU @ 2.50GHz
        # max_iteration = 10000    - Take 0.108s   on Intel(R) Core(TM) i7-2860QM CPU @ 2.50GHz

        max_iteration = 10000
        for _ in range(1, max_iteration):
            id_2 = new_id()
            self.assertEqual(len(id_2), 8)
            self.assertNotEqual(id_1, id_2)

    def test_is_valid_id(self):
        """Test Utils.is_valid_id()"""
        id_1 = new_id()
        self.assertTrue(is_valid_id(id_1))
        self.assertFalse(is_valid_id(42))

    def test_(self):
        """Test Utils.merge_dicts()"""
        result_wanted1 = {
            'a': 4,
            'b': 2
        }
        value1 = {
            'a': 4
        }
        value2 = {
            'b': 2
        }
        self.assertEqual(result_wanted1, merge_dicts(value1, value2))
        value1 = {
            'a': 0,
            'b': 0
        }
        value2 = {
            'a': 4,
            'b': 2
        }
        self.assertEqual(value2, merge_dicts(value1, value2))
