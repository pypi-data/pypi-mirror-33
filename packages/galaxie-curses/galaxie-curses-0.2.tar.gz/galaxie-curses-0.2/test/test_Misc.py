#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import sys
import os
from GLXCurses import Misc
from GLXCurses.Utils import glxc_type

# Require when you haven't GLXCurses as default Package
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))


# Unittest
class TestMisc(unittest.TestCase):

    # Test
    def test_glxc_type(self):
        """Test Misc Type"""
        misc = Misc()
        self.assertTrue(glxc_type(misc))

    def test_set_get_alignment(self):
        """Test Misc.set_alignment() and Misc.get_alignment()"""
        misc = Misc()
        # Normal set / get
        xalign = 0.5
        yalign = 0.5
        misc.set_alignment(xalign, yalign)
        self.assertEqual(misc.get_alignment(), (xalign, yalign))
        # Test with no argument
        misc.set_alignment()
        self.assertEqual(misc.get_alignment(), (0.0, 0.0))
        # Test with  xalign None
        xalign = None
        yalign = 0.5
        misc.set_alignment(xalign, yalign)
        self.assertEqual(misc.get_alignment(), (0.0, 0.5))
        # Test with  yalign None
        xalign = 0.5
        yalign = None
        misc.set_alignment(xalign, yalign)
        self.assertEqual(misc.get_alignment(), (0.5, 0.0))
        # Test clamp
        xalign = 2.5
        yalign = 2.5
        misc.set_alignment(xalign, yalign)
        self.assertEqual(misc.get_alignment(), (1.0, 1.0))
        # Test clamp
        xalign = -2.5
        yalign = -2.5
        misc.set_alignment(xalign, yalign)
        self.assertEqual(misc.get_alignment(), (0.0, 0.0))
        # Test clamp
        xalign = -2.5
        yalign = 2.5
        misc.set_alignment(xalign, yalign)
        self.assertEqual(misc.get_alignment(), (0.0, 1.0))
        # Test clamp
        xalign = 2.5
        yalign = -2.5
        misc.set_alignment(xalign, yalign)
        self.assertEqual(misc.get_alignment(), (1.0, 0.0))

    def test_set_get_padding(self):
        """Test Misc.set_padding() and Misc.get_padding()"""
        misc = Misc()
        # Test with None values
        xpadd = None
        ypadd = None
        misc.set_padding(xpad=xpadd, ypad=ypadd)
        # Must be set to 0 if None
        self.assertEqual(misc.get_padding(), (0, 0))
        # Test with other value
        xpadd = 24
        ypadd = 42
        misc.set_padding(xpadd, ypadd)
        self.assertEqual(misc.get_padding(), (xpadd, ypadd))
        # Test with worng value
        xpadd = 'Galaxie'
        ypadd = 42
        # Test Raise
        self.assertRaises(TypeError, misc.set_padding, xpadd, ypadd)
        # Test with worng value
        xpadd = 42
        ypadd = 'Galaxie'
        # Test Raise
        self.assertRaises(TypeError, misc.set_padding, xpadd, ypadd)


