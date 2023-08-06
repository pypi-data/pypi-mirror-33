#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from GLXCurses import VBox
from GLXCurses.Utils import glxc_type


# Unittest
class TestBox(unittest.TestCase):

    # Test
    def test_glxc_type(self):
        """Test StatusBar type"""
        box = VBox()
        self.assertTrue(glxc_type(box))

    def test_new(self):
        """Test Box.new()"""
        # check default value
        vbox1 = VBox().new()
        self.assertEqual(True, vbox1.homogeneous)
        self.assertEqual(0, vbox1.spacing)

        # check with value
        vbox1 = VBox().new(False, spacing=4)
        self.assertEqual(False, vbox1.homogeneous)
        self.assertEqual(4, vbox1.spacing)

        # check error Type
        self.assertRaises(TypeError, vbox1.new, homogeneous=float(42), spacing=4)
        self.assertRaises(TypeError, vbox1.new, homogeneous=True, spacing='Galaxie')



