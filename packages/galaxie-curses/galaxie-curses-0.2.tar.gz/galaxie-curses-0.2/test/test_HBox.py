#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from GLXCurses import HBox
from GLXCurses.Utils import glxc_type


# Unittest
class TestBox(unittest.TestCase):

    # Test
    def test_glxc_type(self):
        """Test StatusBar type"""
        box = HBox()
        self.assertTrue(glxc_type(box))

    def test_new(self):
        """Test Box.new()"""
        # check default value
        hbox1 = HBox().new()
        self.assertEqual(True, hbox1.homogeneous)
        self.assertEqual(0, hbox1.spacing)

        # check with value
        hbox1 = HBox().new(False, spacing=4)
        self.assertEqual(False, hbox1.homogeneous)
        self.assertEqual(4, hbox1.spacing)

        # check error Type
        self.assertRaises(TypeError, hbox1.new, homogeneous=float(42), spacing=4)
        self.assertRaises(TypeError, hbox1.new, homogeneous=True, spacing='Galaxie')



