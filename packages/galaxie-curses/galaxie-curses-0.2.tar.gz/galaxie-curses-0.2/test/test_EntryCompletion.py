#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import EntryCompletion
from GLXCurses.Utils import glxc_type

import unittest


# Unittest
class TestEntryBuffer(unittest.TestCase):

    # Test
    def test_glxc_type(self):
        """Test EntryCompletion type"""
        entry_completion = EntryCompletion()
        self.assertTrue(glxc_type(entry_completion))
        # check default value
        self.assertEqual(entry_completion.cell_area, None)
        self.assertEqual(entry_completion.inline_completion, False)
        self.assertEqual(entry_completion.inline_selection, False)
        self.assertEqual(entry_completion.minimum_key_length, 1)
        self.assertEqual(entry_completion.model, None)
        self.assertEqual(entry_completion.popup_completion, True)
        self.assertEqual(entry_completion.popup_set_width, True)
        self.assertEqual(entry_completion.popup_single_match, True)
        self.assertEqual(entry_completion.text_column, -1)

    def test_EntryBuffer_new(self):
        """Test EntryCompletion.new()"""
        # test without parameter
        entry_completion = EntryCompletion().new()
        # check default value

