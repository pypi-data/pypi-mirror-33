#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import GLXC
from GLXCurses import Adjustment
from GLXCurses import Range
from GLXCurses.Utils import glxc_type

import unittest


# Unittest
class TestRange(unittest.TestCase):

    # Test
    def test_glxc_type(self):
        """Test Range type"""
        glxc_range = Range()
        self.assertTrue(glxc_type(glxc_range))

    def test_Range(self):
        """Test Range"""
        glxc_range = Range()
        # check default value
        self.assertTrue(glxc_type(glxc_range.adjustment))
        self.assertEqual(glxc_range.fill_level, 1.79769e+308)
        self.assertEqual(glxc_range.inverted, False)
        self.assertEqual(glxc_range.lower_stepper_sensitivity, GLXC.SENSITIVITY_AUTO)
        self.assertEqual(glxc_range.restrict_to_fill_level, True)
        self.assertEqual(glxc_range.round_digits, -1)
        self.assertEqual(glxc_range.show_fill_level, False)
        self.assertEqual(glxc_range.upper_stepper_sensitivity, GLXC.SENSITIVITY_AUTO)

    def test_Range_get_fill_level(self):
        """Test Range.get_fill_level()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.fill_level, 1.79769e+308)
        # make test
        glxc_range.fill_level = 42.42
        self.assertEqual(glxc_range.fill_level, 42.42)

    def test_Range_get_restrict_to_fill_level(self):
        """Test Range.get_restrict_to_fill_level()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.restrict_to_fill_level, True)
        # make test
        glxc_range.restrict_to_fill_level = False
        self.assertEqual(glxc_range.restrict_to_fill_level, False)

    def test_Range_get_show_fill_level(self):
        """Test Range.get_show_fill_level()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.get_show_fill_level(), False)
        # make test
        glxc_range.show_fill_level = True
        self.assertEqual(glxc_range.get_show_fill_level(), True)

    def test_Range_set_fill_level(self):
        """Test Range.set_fill_level()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.fill_level, 1.79769e+308)
        # make test
        glxc_range.set_fill_level(42.42)
        self.assertEqual(glxc_range.fill_level, 42.42)
        # test error
        self.assertRaises(TypeError, glxc_range.set_fill_level, str("Hello"))

    def test_Range_set_restrict_to_fill_level(self):
        """Test Range.set_restrict_to_fill_level ()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.restrict_to_fill_level, True)
        # make test
        glxc_range.set_restrict_to_fill_level(False)
        self.assertEqual(glxc_range.restrict_to_fill_level, False)
        # test error
        self.assertRaises(TypeError, glxc_range.set_restrict_to_fill_level, str("Hello"))

    def test_Range_set_show_fill_level(self):
        """Test Range.set_show_fill_level  ()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.show_fill_level, False)
        # make test
        glxc_range.set_show_fill_level(True)
        self.assertEqual(glxc_range.show_fill_level, True)
        # test error
        self.assertRaises(TypeError, glxc_range.set_show_fill_level, str("Hello"))

    def test_Range_get_adjustment(self):
        """Test Range.get_adjustment()"""
        glxc_range = Range()
        adjustment = Adjustment()
        # check default value
        self.assertTrue(glxc_type(glxc_range.get_adjustment()))
        # make test
        self.assertNotEqual(glxc_range.get_adjustment(), adjustment)
        glxc_range.adjustment = adjustment
        self.assertTrue(glxc_type(glxc_range.adjustment))
        self.assertEqual(glxc_range.get_adjustment(), adjustment)

    def test_Range_set_adjustment(self):
        """Test Range.set_adjustment()"""
        glxc_range = Range()
        adjustment = Adjustment()
        # check default value
        self.assertTrue(glxc_type(glxc_range.adjustment))
        # make the test
        glxc_range.set_adjustment(adjustment=adjustment)
        self.assertEqual(glxc_range.adjustment, adjustment)
        # back to default
        glxc_range.set_adjustment()
        self.assertTrue(glxc_type(glxc_range.adjustment))
        # check error
        self.assertRaises(TypeError, glxc_range.set_adjustment, str("Hello"))

    def test_Range_get_inverted(self):
        """Test Range.get_inverted()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.inverted, False)
        self.assertEqual(glxc_range.get_inverted(), False)
        # make test
        glxc_range.inverted = True
        self.assertEqual(glxc_range.inverted, True)
        self.assertEqual(glxc_range.get_inverted(), True)

    def test_Range_set_inverted(self):
        """Test Range.set_inverted()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.inverted, False)
        # make test
        glxc_range.set_inverted(True)
        self.assertEqual(glxc_range.inverted, True)
        # check error
        self.assertRaises(TypeError, glxc_range.set_inverted, str("Hello"))

    def test_Range_get_value(self):
        """Test Range.get_value()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.get_value(), 0.0)
        # make test
        glxc_range.adjustment.value = 42.0
        self.assertEqual(glxc_range.get_value(), 42.0)

    def test_Range_set_value(self):
        """Test Range.set_value()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.adjustment.value, 0.0)
        # make test 1
        glxc_range.restrict_to_fill_level = False
        glxc_range.adjustment.lower = 1.0
        glxc_range.adjustment.max = 20.0
        glxc_range.set_value(42.0)
        self.assertEqual(glxc_range.adjustment.value, 42.0)
        # make test 2
        glxc_range.restrict_to_fill_level = True
        glxc_range.adjustment.lower = 420.0
        glxc_range.adjustment.max = 402.0
        glxc_range.set_value(42.0)
        self.assertEqual(glxc_range.adjustment.value, 420.0)
        # check error
        self.assertRaises(TypeError, glxc_range.set_value, str("Hello"))

    def test_Range_set_increments(self):
        """Test Range.set_increments()"""
        glxc_range = Range()
        # check default value
        self.assertTrue(glxc_type(glxc_range.adjustment))
        # make the test
        glxc_range.set_increments(step=42.24, page=42.42)
        self.assertEqual(glxc_range.adjustment.value, 0.0)
        self.assertEqual(glxc_range.adjustment.lower, 0.0)
        self.assertEqual(glxc_range.adjustment.upper, 0.0)
        self.assertEqual(glxc_range.adjustment.step_increment, 42.24)
        self.assertEqual(glxc_range.adjustment.page_increment, 42.42)
        self.assertEqual(glxc_range.adjustment.page_size, 0.0)

        # check error
        self.assertRaises(TypeError, glxc_range.set_increments, str("Hello"), float(42.42))
        self.assertRaises(TypeError, glxc_range.set_increments, float(42.42), str("Hello"))
        self.assertRaises(TypeError, glxc_range.set_increments, str("Hello"), str("Hello"))

    def test_Range_set_range(self):
        """Test Range.set_range()"""
        glxc_range = Range()
        # check default value
        self.assertTrue(glxc_type(glxc_range.adjustment))
        # make the test 1
        glxc_range.value = 420
        glxc_range.restrict_to_fill_level = False
        glxc_range.set_range(min=421.00, max=430.00)
        self.assertEqual(glxc_range.adjustment.value, 421.00)
        self.assertEqual(glxc_range.adjustment.lower, 421.00)
        self.assertEqual(glxc_range.adjustment.upper, 430.00)
        # make the test 2
        glxc_range.restrict_to_fill_level = True
        glxc_range.value = 420
        glxc_range.set_range(min=24.00, max=419.00)
        self.assertEqual(glxc_range.adjustment.value, 419.00)
        self.assertEqual(glxc_range.adjustment.lower, 24.00)
        self.assertEqual(glxc_range.adjustment.upper, 419.00)
        # check error
        self.assertRaises(TypeError, glxc_range.set_range, str("Hello"), float(42.42))
        self.assertRaises(TypeError, glxc_range.set_range, float(42.42), str("Hello"))
        self.assertRaises(TypeError, glxc_range.set_range, str("Hello"), str("Hello"))

    def test_Range_get_round_digits(self):
        """Test Range.get_round_digits()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.get_round_digits(), -1)
        # make test
        glxc_range.round_digits = 3
        self.assertEqual(glxc_range.get_round_digits(), 3)

    def test_Range_set_round_digits(self):
        """Test Range.set_round_digits()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.round_digits, -1)
        glxc_range.set_round_digits(3)
        self.assertEqual(glxc_range.round_digits, 3)
        # check if we back to default value
        glxc_range.set_round_digits()
        self.assertEqual(glxc_range.round_digits, -1)
        # check error
        self.assertRaises(TypeError, glxc_range.set_round_digits, str("Hello"))

    def test_Range_set_lower_stepper_sensitivity(self):
        """Test Range.set_lower_stepper_sensitivity()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.lower_stepper_sensitivity, GLXC.SENSITIVITY_AUTO)

        # make test
        glxc_range.set_lower_stepper_sensitivity(GLXC.SENSITIVITY_ON)
        self.assertEqual(glxc_range.lower_stepper_sensitivity, GLXC.SENSITIVITY_ON)
        glxc_range.set_lower_stepper_sensitivity(GLXC.SENSITIVITY_OFF)
        self.assertEqual(glxc_range.lower_stepper_sensitivity, GLXC.SENSITIVITY_OFF)
        glxc_range.set_lower_stepper_sensitivity(GLXC.SENSITIVITY_AUTO)
        self.assertEqual(glxc_range.lower_stepper_sensitivity, GLXC.SENSITIVITY_AUTO)

        # Test if that restore default value
        glxc_range.lower_stepper_sensitivity = None
        self.assertEqual(glxc_range.lower_stepper_sensitivity, None)
        glxc_range.set_lower_stepper_sensitivity()
        self.assertEqual(glxc_range.lower_stepper_sensitivity, GLXC.SENSITIVITY_AUTO)

        # test error
        self.assertRaises(TypeError, glxc_range.set_lower_stepper_sensitivity, str("Hello"))

    def test_Range_get_lower_stepper_sensitivity(self):
        """Test Range.get_lower_stepper_sensitivity()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.get_lower_stepper_sensitivity(), GLXC.SENSITIVITY_AUTO)
        # make test
        glxc_range.lower_stepper_sensitivity = GLXC.SENSITIVITY_OFF
        self.assertEqual(glxc_range.get_lower_stepper_sensitivity(), GLXC.SENSITIVITY_OFF)

    def test_Range_set_upper_stepper_sensitivity(self):
        """Test Range.set_upper_stepper_sensitivity()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.upper_stepper_sensitivity, GLXC.SENSITIVITY_AUTO)

        # make test
        glxc_range.set_upper_stepper_sensitivity(GLXC.SENSITIVITY_ON)
        self.assertEqual(glxc_range.upper_stepper_sensitivity, GLXC.SENSITIVITY_ON)
        glxc_range.set_upper_stepper_sensitivity(GLXC.SENSITIVITY_OFF)
        self.assertEqual(glxc_range.upper_stepper_sensitivity, GLXC.SENSITIVITY_OFF)
        glxc_range.set_upper_stepper_sensitivity(GLXC.SENSITIVITY_AUTO)
        self.assertEqual(glxc_range.upper_stepper_sensitivity, GLXC.SENSITIVITY_AUTO)

        # Test if that restore default value
        glxc_range.upper_stepper_sensitivity = None
        self.assertEqual(glxc_range.upper_stepper_sensitivity, None)
        glxc_range.set_upper_stepper_sensitivity()
        self.assertEqual(glxc_range.upper_stepper_sensitivity, GLXC.SENSITIVITY_AUTO)

        # test error
        self.assertRaises(TypeError, glxc_range.set_upper_stepper_sensitivity, str("Hello"))

    def test_Range_get_upper_stepper_sensitivity(self):
        """Test Range.get_upper_stepper_sensitivity()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.get_upper_stepper_sensitivity(), GLXC.SENSITIVITY_AUTO)
        # make test
        glxc_range.upper_stepper_sensitivity = GLXC.SENSITIVITY_OFF
        self.assertEqual(glxc_range.get_upper_stepper_sensitivity(), GLXC.SENSITIVITY_OFF)

    def test_Range_get_flippable(self):
        """Test Range.get_flippable()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range._flippable, False)
        self.assertEqual(glxc_range.get_flippable(), False)
        # make test
        glxc_range._flippable = True
        self.assertEqual(glxc_range._flippable, True)
        self.assertEqual(glxc_range.get_flippable(), True)

    def test_Range_set_flippable(self):
        """Test Range.set_flippable()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range._flippable, False)
        # make test
        glxc_range.set_flippable(True)
        self.assertEqual(glxc_range._flippable, True)
        # check error
        self.assertRaises(TypeError, glxc_range.set_flippable, str("Hello"))

    def test_Range_get_range_rect(self):
        """Test Range.get_range_rect()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.x, 0)
        self.assertEqual(glxc_range.y, 0)
        self.assertEqual(glxc_range.width, 0)
        self.assertEqual(glxc_range.height, 0)
        self.assertEqual(glxc_range.get_range_rect(), [0, 0, 0, 0])
        # make test
        glxc_range.x = 1
        glxc_range.y = 2
        glxc_range.width = 3
        glxc_range.height = 4
        self.assertEqual(glxc_range.get_range_rect(), [1, 2, 3, 4])

    def test_Range_get_slider_range(self):
        """Test Range.get_slider_range()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.get_slider_range(slider_start=True, slider_end=True), [None, None])
        # make the test
        self.assertEqual(glxc_range.x, 0)
        self.assertEqual(glxc_range.y, 0)
        self.assertEqual(glxc_range.width, 0)
        self.assertEqual(glxc_range.height, 0)
        glxc_range.orientation = GLXC.ORIENTATION_VERTICAL
        self.assertEqual(glxc_range.get_slider_range(slider_start=True, slider_end=True), [0, 0])
        # make test
        glxc_range.orientation = GLXC.ORIENTATION_VERTICAL
        glxc_range.x = 1
        glxc_range.y = 2
        glxc_range.width = 3
        glxc_range.height = 4
        self.assertEqual(glxc_range.get_slider_range(slider_start=True, slider_end=True), [2, 6])
        self.assertEqual(glxc_range.get_slider_range(slider_start=None, slider_end=True), [None, 6])
        self.assertEqual(glxc_range.get_slider_range(slider_start=True, slider_end=None), [2, None])
        glxc_range.orientation = False
        self.assertEqual(glxc_range.get_slider_range(slider_start=True, slider_end=True), [2, 4])
        self.assertEqual(glxc_range.get_slider_range(slider_start=True, slider_end=None), [2, None])
        self.assertEqual(glxc_range.get_slider_range(slider_start=None, slider_end=True), [None, 4])

    def test_Range_get_slider_size_fixed(self):
        """Test Range.get_slider_size_fixed()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range.get_slider_size_fixed(), False)
        # make the test
        glxc_range._slider_size_fixed = True
        self.assertEqual(glxc_range.get_slider_size_fixed(), True)

    def test_Range_set_slider_size_fixed(self):
        """Test Range.set_slider_size_fixed()"""
        glxc_range = Range()
        # check default value
        self.assertEqual(glxc_range._slider_size_fixed, False)
        # make the test
        glxc_range.set_slider_size_fixed(True)
        self.assertEqual(glxc_range._slider_size_fixed, True)
        # check error
        self.assertRaises(TypeError, glxc_range.set_slider_size_fixed, str("Hello"))
