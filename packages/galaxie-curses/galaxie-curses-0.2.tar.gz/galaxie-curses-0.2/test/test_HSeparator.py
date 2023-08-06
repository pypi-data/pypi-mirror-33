#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from random import randint
import random
import string
from GLXCurses import GLXC
from GLXCurses.Utils import glxc_type
import sys
import os

# Require when you haven't GLXBob as default Package
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

import GLXCurses


# Unittest
class TestHSeparator(unittest.TestCase):

    def setUp(self):
        # Before the test start
        self.application = GLXCurses.Application()

    def tearDown(self):
        # When the test is finish
        self.application.close()

    # Test
    def test_glxc_type(self):
        """Test if VSeparator is GLXCurses Type"""
        hline = GLXCurses.HSeparator()
        self.assertTrue(glxc_type(hline))

    def test_draw_widget_in_area(self):
        """Test HSeparator.draw_widget_in_area()"""
        hline = GLXCurses.HSeparator()
        hline.draw_widget_in_area()

    def test_set_get_position_type(self):
        """Test HSeparator.set_position_type() and HSeparator.get_position_type()"""
        hline = GLXCurses.HSeparator()

        hline.set_position_type('CENTER')
        self.assertEqual(hline.get_position_type(), GLXC.POS_CENTER)

        hline.set_position_type('TOP')
        self.assertEqual(hline.get_position_type(), GLXC.POS_TOP)

        hline.set_position_type('BOTTOM')
        self.assertEqual(hline.get_position_type(), GLXC.POS_BOTTOM)

        hline.set_position_type(GLXC.POS_CENTER)
        self.assertEqual(hline.get_position_type(), 'CENTER')

        hline.set_position_type(GLXC.POS_TOP)
        self.assertEqual(hline.get_position_type(), 'TOP')

        hline.set_position_type(GLXC.POS_BOTTOM)
        self.assertEqual(hline.get_position_type(), 'BOTTOM')

        self.assertRaises(TypeError, hline.set_position_type, 'HELLO')

    # Internal
    def test__check_position_type(self):
        """Test VSeparator._check_position_type()"""
        hline = GLXCurses.HSeparator()

        # glxc.POS_CENTER -> (self.get_height() / 2) - self.get_preferred_height()
        hline._position_type = GLXC.POS_CENTER
        hline.height = 124
        hline.preferred_height = 20
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 42)

        hline.height = None
        hline.preferred_height = None
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 0)

        hline.height = -1
        hline.preferred_height = -1
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 0)

        hline.height = 0
        hline.preferred_height = -0
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 0)

        hline.height = -1000
        hline.preferred_height = -100
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 0)

        # glxc.POS_TOP -> self._set_hseperator_y(0)
        hline._position_type = GLXC.POS_TOP
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 0)

        hline.height = None
        hline.preferred_height = None
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 0)

        hline.height = -1
        hline.preferred_height = -1
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 0)

        hline.height = 0
        hline.preferred_height = -0
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 0)

        hline.height = -1000
        hline.preferred_height = -100
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 0)

        # glxc.POS_BOTTOM -> self.get_height() - self.get_preferred_height()
        hline._position_type = GLXC.POS_BOTTOM
        hline.height = 62
        hline.preferred_height = 20
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 42)

        hline.height = None
        hline.preferred_height = None
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 0)

        hline.height = -1
        hline.preferred_height = -1
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 0)

        hline.height = 0
        hline.preferred_height = -0
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 0)

        hline.height = -1000
        hline.preferred_height = -100
        hline._check_position_type()
        self.assertEqual(hline._y_offset, 0)

    def test__get_estimated_preferred_width(self):
        """Test VSeparator._get_estimated_preferred_width()"""
        hline = GLXCurses.HSeparator()
        hline.x = 20
        hline.width = 20
        self.assertEqual(hline._get_estimated_preferred_width(), 40)

    def test__get_estimated_preferred_height(self):
        """Test VSeparator._get_estimated_preferred_height()"""
        hline = GLXCurses.HSeparator()
        self.assertEqual(hline._get_estimated_preferred_height(), 1)

    def test_set_get_hseperator_x(self):
        """Test HSeparator._set_hseperator_x() and HSeparator._get_hseperator_x()"""
        hline = GLXCurses.HSeparator()
        # call set_decorated() with 0 as argument
        hline._set_x_offset(0)
        # verify we go back 0
        self.assertEqual(hline._get_x_offset(), 0)
        # call set_decorated() with 0 as argument
        hline._set_x_offset(42)
        # verify we go back 0
        self.assertEqual(hline._get_x_offset(), 42)
        # test raise TypeError
        self.assertRaises(TypeError, hline._set_x_offset, 'Galaxie')

    def test_set_get_hseperator_y(self):
        """Test HSeparator._set_hseperator_y() and HSeparator._get_hseperator_y()"""
        hline = GLXCurses.HSeparator()
        # call set_decorated() with 0 as argument
        hline._set_y_offset(0)
        # verify we go back 0
        self.assertEqual(hline._get_y_offset(), 0)
        # call set_decorated() with 0 as argument
        hline._set_y_offset(42)
        # verify we go back 0
        self.assertEqual(hline._get_y_offset(), 42)
        # test raise TypeError
        self.assertRaises(TypeError, hline._set_y_offset, 'Galaxie')
