#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

import unittest

from GLXCurses import Widget
from GLXCurses.Utils import glxc_type


# Unittest
class TestWidget(unittest.TestCase):

    # Test
    def test_glxc_type(self):
        """Test Widget Type"""
        widget = Widget()
        self.assertTrue(glxc_type(widget))

    def test_Widget_set_name(self):
        """Test Widget.set_name()"""
        widget = Widget()
        self.assertEqual(widget.name, widget.__class__.__name__)

        widget.set_name("Hello")
        self.assertEqual(widget.name, "Hello")

        widget.set_name()
        self.assertEqual(widget.name, widget.__class__.__name__)

        self.assertRaises(TypeError, widget.set_name, int(42))

    def test_Widget_get_name(self):
        """TEst Widget.get_name()"""
        widget = Widget()
        self.assertEqual(widget.get_name(), widget.__class__.__name__)

        widget.name = "Hello"
        self.assertEqual(widget.get_name(), "Hello")
