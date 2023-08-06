#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import sys
import os
from GLXCurses import Object
from GLXCurses.Utils import glxc_type

# Require when you haven't GLXCurses as default Package
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))


# Unittest
class TestObject(unittest.TestCase):

    # Test
    def test_glxc_type(self):
        """Test Misc Type"""
        the_object = Object()
        self.assertTrue(glxc_type(the_object))

    def test_get_default_flags(self):
        """Test Object.get_default_flags()"""
        the_object = Object()
        default_flags = the_object.get_default_flags()
        # Check first level dictionary
        self.assertEqual(type(default_flags), type(dict()))
        valid_flags = ['IN_DESTRUCTION',
                       'FLOATING',
                       'TOPLEVEL',
                       'NO_WINDOW',
                       'REALIZED',
                       'MAPPED',
                       'VISIBLE',
                       'SENSITIVE',
                       'PARENT_SENSITIVE',
                       'CAN_FOCUS',
                       'HAS_FOCUS',
                       'CAN_DEFAULT',
                       'HAS_DEFAULT',
                       'HAS_GRAB',
                       'RC_STYLE',
                       'COMPOSITE_CHILD',
                       'NO_REPARENT',
                       'APP_PAINTABLE',
                       'RECEIVES_DEFAULT',
                       'DOUBLE_BUFFERED'
                       ]

        # Check if all keys are present
        for key in valid_flags:
            self.assertTrue(key in default_flags)

        # check default value
        self.assertEqual(default_flags['IN_DESTRUCTION'], False)
        self.assertEqual(default_flags['FLOATING'], True)
        self.assertEqual(default_flags['TOPLEVEL'], False)
        self.assertEqual(default_flags['NO_WINDOW'], True)
        self.assertEqual(default_flags['REALIZED'], False)
        self.assertEqual(default_flags['MAPPED'], False)
        self.assertEqual(default_flags['VISIBLE'], True)
        self.assertEqual(default_flags['SENSITIVE'], True)
        self.assertEqual(default_flags['PARENT_SENSITIVE'], True)
        self.assertEqual(default_flags['CAN_FOCUS'], True)
        self.assertEqual(default_flags['HAS_FOCUS'], True)
        self.assertEqual(default_flags['CAN_DEFAULT'], True)
        self.assertEqual(default_flags['HAS_DEFAULT'], False)
        self.assertEqual(default_flags['HAS_GRAB'], False)
        self.assertEqual(default_flags['RC_STYLE'], 'Default.yml')
        self.assertEqual(default_flags['COMPOSITE_CHILD'], False)
        self.assertEqual(default_flags['NO_REPARENT'], 'unused')
        self.assertEqual(default_flags['APP_PAINTABLE'], False)
        self.assertEqual(default_flags['RECEIVES_DEFAULT'], False)
        self.assertEqual(default_flags['DOUBLE_BUFFERED'], False)

    def test_set_get_flags(self):
        """Test Object.set_flags() and Object.get_flags()"""
        the_object = Object()
        default_flags = the_object.get_default_flags()

        the_object.set_flags(default_flags)

        self.assertEqual(the_object.get_flags(), default_flags)

        # Test raise error
        self.assertRaises(TypeError, the_object.set_flags, None)
        self.assertRaises(KeyError, the_object.set_flags, dict())

    def test_destroy(self):
        """Test Object.destroy()"""
        the_object = Object()
        flags = the_object.get_flags()
        self.assertEqual(flags['IN_DESTRUCTION'], False)
        the_object.destroy()
        self.assertEqual(flags['IN_DESTRUCTION'], True)

    def test_unset_flags(self):
        """Test Object.unset_flags()"""
        the_object = Object()
        self.assertEqual(the_object.get_flags(), the_object.get_default_flags())
        the_object.get_flags()['IN_DESTRUCTION'] = True
        self.assertNotEqual(the_object.get_flags(), the_object.get_default_flags())
        the_object.unset_flags()
        self.assertEqual(the_object.get_flags(), the_object.get_default_flags())
