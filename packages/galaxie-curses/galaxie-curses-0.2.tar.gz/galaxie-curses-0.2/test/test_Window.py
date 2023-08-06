#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import os

# Require when you haven't GLXBob as default Package
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

import GLXCurses
from GLXCurses.Utils import is_valid_id


# Unittest
class TestWindow(unittest.TestCase):
    def setUp(self):
        # Before the test start
        self.application = GLXCurses.Application()

    def tearDown(self):
        # When the test is finish
        self.application.close()

    # Test
    def test_new(self):
        """Test Window.new()"""
        # create a window instance
        window = GLXCurses.Window()
        # get the window id
        window_id_take1 = window.get_widget_id()
        # check if returned value is a valid id
        self.assertTrue(is_valid_id(window_id_take1))
        # use new() method
        window.new()
        # re get the window id
        window_id_take2 = window.get_widget_id()
        # check if returned value is a valid id
        self.assertTrue(is_valid_id(window_id_take2))
        # id's must be different
        self.assertNotEqual(window_id_take1, window_id_take2)

    def test_set_get_application(self):
        """Test Window.set_application() and Window.get_application()"""
        window = GLXCurses.Window()
        window.set_application(None)
        self.assertEqual(None, window.get_application())
        window.set_application(self.application)
        self.assertEqual(self.application, window.get_application())

    def test_set_application_raise(self):
        """Test Window.set_application() TypeError"""
        window = GLXCurses.Window()
        self.assertRaises(TypeError, window.set_application, int(42))
