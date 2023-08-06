#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import Adjustment
from GLXCurses.Utils import glxc_type

import unittest


# Unittest
class TestEntry(unittest.TestCase):

    # Test
    def test_Adjustment_glxc_type(self):
        """Test GLXCurses.Adjustment type"""
        adjustment = Adjustment()
        self.assertTrue(glxc_type(adjustment))

    def test_Adjustment(self):
        """Test GLXCurses.Adjustment"""
        adjustment = Adjustment()
        # check default value
        self.assertEqual(adjustment.lower, float(0.0))
        self.assertEqual(adjustment.page_increment, float(0.0))
        self.assertEqual(adjustment.page_size, float(0.0))
        self.assertEqual(adjustment.step_increment, float(0.0))
        self.assertEqual(adjustment.minimum_increment, float(0.0))
        self.assertEqual(adjustment.upper, float(0.0))
        self.assertEqual(adjustment.value, float(0.0))
        self.assertEqual(adjustment.two, None)
        self.assertEqual(adjustment.average, None)

    def test_Adjustment_new(self):
        """Test GLXCurses.Adjustment.new()"""
        adjustment = Adjustment().new()
        # check default value
        self.assertEqual(adjustment.lower, float(0.0))
        self.assertEqual(adjustment.page_increment, float(0.0))
        self.assertEqual(adjustment.page_size, float(0.0))
        self.assertEqual(adjustment.step_increment, float(0.0))
        self.assertEqual(adjustment.minimum_increment, float(0.0))
        self.assertEqual(adjustment.upper, float(0.0))
        self.assertEqual(adjustment.value, float(0.0))
        self.assertEqual(adjustment.two, None)
        self.assertEqual(adjustment.average, None)
        # change default value
        adjustment.lower = float(0.5)
        adjustment.page_increment = float(0.5)
        adjustment.page_size = float(0.5)
        adjustment.step_increment = float(0.5)
        adjustment.minimum_increment = float(0.5)
        adjustment.upper = float(0.5)
        adjustment.value = float(0.5)
        adjustment.two = 42
        adjustment.average = 42
        # check new value
        self.assertEqual(adjustment.lower, float(0.5))
        self.assertEqual(adjustment.page_increment, float(0.5))
        self.assertEqual(adjustment.page_size, float(0.5))
        self.assertEqual(adjustment.step_increment, float(0.5))
        self.assertEqual(adjustment.minimum_increment, float(0.5))
        self.assertEqual(adjustment.upper, float(0.5))
        self.assertEqual(adjustment.value, float(0.5))
        self.assertEqual(adjustment.two, 42)
        self.assertEqual(adjustment.average, 42)
        # back to normal
        adjustment = Adjustment().new()
        # check default value
        self.assertEqual(adjustment.lower, float(0.0))
        self.assertEqual(adjustment.page_increment, float(0.0))
        self.assertEqual(adjustment.page_size, float(0.0))
        self.assertEqual(adjustment.step_increment, float(0.0))
        self.assertEqual(adjustment.minimum_increment, float(0.0))
        self.assertEqual(adjustment.upper, float(0.0))
        self.assertEqual(adjustment.value, float(0.0))
        self.assertEqual(adjustment.two, None)
        self.assertEqual(adjustment.average, None)
        # test with initial value
        adjustment = Adjustment().new(
            value=0.7,
            lower=0.7,
            upper=0.7,
            step_increment=0.7,
            page_increment=0.7,
            page_size=0.7
        )
        # check new value
        self.assertEqual(adjustment.lower, float(0.7))
        self.assertEqual(adjustment.page_increment, float(0.7))
        self.assertEqual(adjustment.page_size, float(0.7))
        self.assertEqual(adjustment.step_increment, float(0.7))
        self.assertEqual(adjustment.upper, float(0.7))
        self.assertEqual(adjustment.value, float(0.7))
        # check raise error
        self.assertRaises(TypeError, adjustment.new, lower=str('0.0'))
        self.assertRaises(TypeError, adjustment.new, page_increment=str('0.0'))
        self.assertRaises(TypeError, adjustment.new, page_size=str('0.0'))
        self.assertRaises(TypeError, adjustment.new, step_increment=str('0.0'))
        self.assertRaises(TypeError, adjustment.new, minimum_increment=str('0.0'))
        self.assertRaises(TypeError, adjustment.new, upper=str('0.0'))
        self.assertRaises(TypeError, adjustment.new, value=str('0.0'))

        # check return type
        adjustment = Adjustment().new()
        self.assertTrue(glxc_type(adjustment))

    def test_Adjustment_get_value(self):
        """Test GLXCurses.Adjustment.get_value()"""
        adjustment = Adjustment().new(value=0.3)
        self.assertEqual(adjustment.get_value(), float(0.3))

    def test_Adjustment_set_value(self):
        """Test GLXCurses.Adjustment.set_value()"""
        adjustment = Adjustment()
        # make the test
        adjustment.set_upper(0.2)
        adjustment.set_value(0.2)
        self.assertEqual(adjustment.get_value(), float(0.2))
        # check if the the clamp work
        # check 1 (upper)
        adjustment.set_lower(0.0)
        adjustment.set_upper(0.1)
        adjustment.set_value(0.2)
        self.assertEqual(adjustment.get_value(), float(0.1))
        # check 2 (lower)
        adjustment.set_lower(0.2)
        adjustment.set_upper(0.4)
        adjustment.set_value(0.1)
        self.assertEqual(adjustment.get_value(), float(0.2))
        # check 3 (default)
        adjustment.set_lower(0.0)
        adjustment.set_upper(0.0)
        adjustment.set_value(0.2)
        self.assertEqual(adjustment.get_value(), float(0.0))
        # check error
        self.assertRaises(TypeError, adjustment.set_value, value=str('0.0'))

    def test_Adjustment_clamp_page(self):
        """Test GLXCurses.Adjustment.clamp_page()"""
        adjustment = Adjustment().new(value=0.9)
        adjustment.lower = 0.2
        adjustment.upper = 0.7
        adjustment.clamp_page(lower=0.4, upper=0.8)
        self.assertEqual(adjustment.get_value(), float(0.4))

        adjustment = Adjustment().new(value=0.9)
        adjustment.lower = 0.2
        adjustment.upper = 0.7
        adjustment.clamp_page(lower=0.1, upper=0.8)
        self.assertEqual(adjustment.get_value(), float(0.2))

        adjustment = Adjustment().new(value=1.1)
        adjustment.lower = 0.0
        adjustment.upper = 1.6
        adjustment.page_size = 0.3
        adjustment.clamp_page(lower=2.4, upper=2.8)
        self.assertEqual(adjustment.get_value(), float(1.3))

        # check raise error
        self.assertRaises(TypeError, adjustment.clamp_page, upper=str('0.0'))
        self.assertRaises(TypeError, adjustment.clamp_page, upper=float(0.9), lower=str('0.0'))

    def test_Adjustment_configure(self):
        """Test GLXCurses.Adjustment.configure()"""
        adjustment = Adjustment()
        self.assertEqual(adjustment.lower, float(0.0))
        self.assertEqual(adjustment.page_increment, float(0.0))
        self.assertEqual(adjustment.page_size, float(0.0))
        self.assertEqual(adjustment.step_increment, float(0.0))
        self.assertEqual(adjustment.minimum_increment, float(0.0))
        self.assertEqual(adjustment.upper, float(0.0))
        self.assertEqual(adjustment.value, float(0.0))
        adjustment.configure(
            value=42.42,
            lower=4.00,
            upper=60.00,
            step_increment=0.1,
            page_increment=1.0,
            page_size=40.0
        )
        self.assertEqual(adjustment.lower, float(4.0))
        self.assertEqual(adjustment.page_increment, float(1.0))
        self.assertEqual(adjustment.page_size, float(40.0))
        self.assertEqual(adjustment.step_increment, float(0.1))
        self.assertEqual(adjustment.minimum_increment, float(0.0))
        self.assertEqual(adjustment.upper, float(60.0))
        self.assertEqual(adjustment.value, float(20.0))

        # check error
        self.assertRaises(TypeError, adjustment.configure,
                          value='42',
                          lower=0.00,
                          upper=60.00,
                          step_increment=0.1,
                          page_increment=1.0,
                          page_size=40.0
                          )
        self.assertRaises(TypeError, adjustment.configure,
                          value=42.42,
                          lower='42',
                          upper=60.00,
                          step_increment=0.1,
                          page_increment=1.0,
                          page_size=40.0
                          )
        self.assertRaises(TypeError, adjustment.configure,
                          value=42.42,
                          lower=0.00,
                          upper='42',
                          step_increment=0.1,
                          page_increment=1.0,
                          page_size=40.0
                          )
        self.assertRaises(TypeError, adjustment.configure,
                          value=42.42,
                          lower=0.00,
                          upper=60.00,
                          step_increment='42',
                          page_increment=1.0,
                          page_size=40.0
                          )
        self.assertRaises(TypeError, adjustment.configure,
                          value=42.42,
                          lower=0.00,
                          upper=60.00,
                          step_increment=0.1,
                          page_increment='42',
                          page_size=40.0
                          )
        self.assertRaises(TypeError, adjustment.configure,
                          value=42.42,
                          lower=0.00,
                          upper=60.00,
                          step_increment=0.1,
                          page_increment=1.0,
                          page_size='42'
                          )

    def test_Adjustment_get_lower(self):
        """Test GLXCurses.Adjustment.get_lower()"""
        adjustment = Adjustment()
        adjustment.lower = 0.42
        self.assertEqual(adjustment.get_lower(), 0.42)

    def test_Adjustment_get_page_increment(self):
        """Test GLXCurses.Adjustment.get_page_increment()"""
        adjustment = Adjustment()
        adjustment.page_increment = 0.142
        self.assertEqual(adjustment.get_page_increment(), 0.142)

    def test_Adjustment_get_page_size(self):
        """Test GLXCurses.Adjustment.get_page_size()"""
        adjustment = Adjustment()
        adjustment.page_size = 0.1142
        self.assertEqual(adjustment.get_page_size(), 0.1142)

    def test_Adjustment_get_step_increment(self):
        """Test GLXCurses.Adjustment.get_step_increment()"""
        adjustment = Adjustment()
        adjustment.step_increment = 0.11142
        self.assertEqual(adjustment.get_step_increment(), 0.11142)

    def test_Adjustment_get_minimum_increment(self):
        """Test GLXCurses.Adjustment.get_minimum_increment()"""
        adjustment = Adjustment()
        adjustment.configure(
            value=2.42,
            lower=0.00,
            upper=60.00,
            step_increment=25.0,
            page_increment=10.0,
            page_size=40.0
        )
        self.assertEqual(adjustment.get_minimum_increment(), 10)

        adjustment.configure(
            value=2.42,
            lower=0.00,
            upper=60.00,
            step_increment=0.5,
            page_increment=10.0,
            page_size=40.0
        )
        self.assertEqual(adjustment.get_minimum_increment(), 0.5)

        adjustment.configure(
            value=2.42,
            lower=0.00,
            upper=0.00,
            step_increment=0.0,
            page_increment=10.0,
            page_size=40.0
        )
        self.assertEqual(adjustment.get_minimum_increment(), 10.0)

        adjustment.configure(
            value=2.42,
            lower=0.00,
            upper=0.00,
            step_increment=0.0,
            page_increment=0.0,
            page_size=40.0
        )
        self.assertEqual(adjustment.get_minimum_increment(), 0.0)

        # Test strange thing but it's like that on GTK source cheers!
        adjustment.configure(
            value=2.42,
            lower=0.00,
            upper=0.00,
            step_increment=0.0,
            page_increment=0.0,
            page_size=40.0
        )
        adjustment.step_increment = 'hello'
        self.assertEqual(adjustment.get_minimum_increment(), 'hello')

    def test_Adjustment_get_upper(self):
        """Test GLXCurses.Adjustment.get_upper()"""
        adjustment = Adjustment()
        adjustment.upper = 0.111142
        self.assertEqual(adjustment.get_upper(), 0.111142)

    def test_Adjustment_set_lower(self):
        """Test GLXCurses.Adjustment.set_lower()"""
        adjustment = Adjustment()
        adjustment.set_lower(0.111142)
        self.assertEqual(adjustment.lower, 0.111142)
        # Check error
        self.assertRaises(TypeError, adjustment.set_lower, str('0.0'))

    def test_Adjustment_set_page_increment(self):
        """Test GLXCurses.Adjustment.set_page_increment()"""
        adjustment = Adjustment()
        adjustment.set_page_increment(0.111142)
        self.assertEqual(adjustment.page_increment, 0.111142)
        # Check error
        self.assertRaises(TypeError, adjustment.set_page_increment, str('0.0'))

    def test_Adjustment_set_page_size(self):
        """Test GLXCurses.Adjustment.set_page_increment()"""
        adjustment = Adjustment()
        adjustment.set_page_size(0.111142)
        self.assertEqual(adjustment.page_size, 0.111142)
        # Check error
        self.assertRaises(TypeError, adjustment.set_page_size, str('0.0'))

    def test_Adjustment_set_step_increment(self):
        """Test GLXCurses.Adjustment.set_step_increment()"""
        adjustment = Adjustment()
        adjustment.set_step_increment(0.111142)
        self.assertEqual(adjustment.step_increment, 0.111142)
        # Check error
        self.assertRaises(TypeError, adjustment.set_step_increment, str('0.0'))

    def test_Adjustment_set_upper(self):
        """Test GLXCurses.Adjustment.set_step_increment()"""
        adjustment = Adjustment()
        adjustment.set_upper(0.111142)
        self.assertEqual(adjustment.upper, 0.111142)
        # Check error
        self.assertRaises(TypeError, adjustment.set_upper, str('0.0'))
