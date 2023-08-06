#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import GLXC
from GLXCurses import Adjustment
from GLXCurses import Actionable
from GLXCurses.Utils import glxc_type

import unittest


# Unittest
class TestRange(unittest.TestCase):

    # Test
    def test_Adjustment_get_action_name(self):
        """Test Adjustment.get_action_name()"""
        actionable = Actionable()
        # check default value
        self.assertEqual(actionable.action_name, None)
        # make the test
        actionable.action_name = 42
        self.assertEqual(actionable.action_name, 42)

    def test_Adjustment_set_action_name(self):
        """Test Adjustment.set_action_name()"""
        actionable = Actionable()
        # check default value
        self.assertEqual(actionable.action_name, None)
        # make the test
        actionable.set_action_name("Hello")
        self.assertEqual(actionable.action_name, "Hello")
        # check if back to default value
        actionable.set_action_name()
        self.assertEqual(actionable.action_name, None)
        # test error
        self.assertRaises(TypeError, actionable.set_action_name, float(42.0))

