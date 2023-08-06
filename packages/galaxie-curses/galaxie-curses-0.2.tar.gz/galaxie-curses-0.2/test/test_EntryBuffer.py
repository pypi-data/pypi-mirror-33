#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import EntryBuffer
from GLXCurses.Utils import glxc_type

import unittest
import sys


# Unittest
class TestEntryBuffer(unittest.TestCase):

    # Test
    def test_glxc_type(self):
        """Test EntryBuffer type"""
        entry_buffer = EntryBuffer()
        self.assertTrue(glxc_type(entry_buffer))
        # check default value
        self.assertEqual(0, entry_buffer.length)
        self.assertEqual(0, entry_buffer.max_length)
        self.assertEqual("", entry_buffer.text)
        self.assertEqual(0, entry_buffer._min_length_hard_limit)
        self.assertEqual(65535, entry_buffer._max_length_hard_limit)

    def test_EntryBuffer_new(self):
        """Test EntryBuffer.new()"""
        # test without parameter
        entry_buffer = EntryBuffer().new()
        # check default value
        self.assertEqual(0, entry_buffer.length)
        self.assertEqual(0, entry_buffer.max_length)
        self.assertEqual("", entry_buffer.text)

        # test with 1 parameter
        value_1 = "hello"
        entry_buffer = EntryBuffer().new(initial_chars=value_1)
        # check default value
        self.assertEqual(0, entry_buffer.length)
        self.assertEqual(0, entry_buffer.max_length)
        self.assertEqual(value_1, entry_buffer.text)

        # test with 2 parameter
        n_char = 3
        value_1 = "hello"
        value_2 = value_1[:n_char]
        entry_buffer = EntryBuffer().new(initial_chars=value_1, n_initial_chars=3)
        # check default value
        self.assertEqual(0, entry_buffer.length)
        self.assertEqual(0, entry_buffer.max_length)
        self.assertEqual(value_2, entry_buffer.text)

        # test error
        entry_buffer = EntryBuffer()
        self.assertRaises(TypeError, entry_buffer.new, initial_chars=int())
        self.assertRaises(TypeError, entry_buffer.new, n_initial_chars=str())
        # test unprintable a character
        self.assertRaises(TypeError, entry_buffer.new, initial_chars=chr(128))

    def test_EntryBuffer_get_text(self):
        """Test EntryBuffer.get_text()"""
        value_1 = "hello"
        entry_buffer = EntryBuffer().new(initial_chars=value_1)
        self.assertEqual(value_1, entry_buffer.get_text())

    def test_EntryBuffer_set_text(self):
        """Test EntryBuffer.set_text()"""
        # without n_initial_chars
        value_1 = "hello"
        entry_buffer = EntryBuffer().new()
        entry_buffer.set_text(value_1)
        self.assertEqual(value_1, entry_buffer.get_text())

        # with n_initial_chars
        n_char = 3
        value_1 = "hello"
        value_2 = value_1[:n_char]
        entry_buffer = EntryBuffer().new()
        entry_buffer.set_text(value_1, n_chars=n_char)
        self.assertEqual(value_2, entry_buffer.get_text())

        # with max_length
        n_char = 3
        value_1 = "hello"
        entry_buffer = EntryBuffer().new()
        entry_buffer.max_length = 2
        entry_buffer.set_text(value_1, n_chars=n_char)
        self.assertEqual(entry_buffer.max_length, len(entry_buffer.get_text()))

        # test error
        entry_buffer = EntryBuffer().new()
        entry_buffer.set_text()
        self.assertRaises(TypeError, entry_buffer.set_text, chars=int())
        self.assertRaises(TypeError, entry_buffer.set_text, chars=str(), n_chars=str())
        # test unprintable a character
        self.assertRaises(TypeError, entry_buffer.set_text, chars=chr(128))

    def test_EntryBuffer_get_bytes(self):
        """Test EntryBuffer_get_bytes()"""
        value_1 = "hello"
        entry_buffer = EntryBuffer().new(initial_chars=value_1)
        self.assertEqual(sys.getsizeof(value_1), entry_buffer.get_bytes())

    def test_EntryBuffer_get_length(self):
        """Test EntryBuffer_get_length()"""
        value_1 = "hello"
        entry_buffer = EntryBuffer().new(initial_chars=value_1)
        self.assertEqual(len(value_1), entry_buffer.get_length())

    def test_EntryBuffer_set_max_length(self):
        """Test EntryBuffer_set_max_length()"""
        # Normal
        value_1 = 5
        entry_buffer = EntryBuffer()
        entry_buffer.set_max_length(max_length=value_1)
        self.assertEqual(value_1, entry_buffer.max_length)

        # With very high value , must back to _max_length_hard_limit
        value_1 = 99999999999999999
        entry_buffer = EntryBuffer()
        entry_buffer.set_max_length(max_length=value_1)
        self.assertEqual(entry_buffer._max_length_hard_limit, entry_buffer.max_length)

        # With very low value , must back to _min_length_hard_limit
        value_1 = -99999999999999999
        entry_buffer = EntryBuffer()
        entry_buffer.set_max_length(max_length=value_1)
        self.assertEqual(entry_buffer._min_length_hard_limit, entry_buffer.max_length)

        # Test if it will be truncated to fit
        value_1 = 3
        value_2 = "hello"
        entry_buffer = EntryBuffer()
        entry_buffer.set_text(value_2)
        self.assertEqual(entry_buffer.get_text(), value_2)
        entry_buffer.set_max_length(max_length=value_1)
        self.assertEqual(len(entry_buffer.get_text()), value_1)

        # Test error
        self.assertRaises(TypeError, entry_buffer.set_max_length, str())

    def test_EntryBuffer_insert_text(self):
        """Test EntryBuffer_insert_text()"""
        entry_buffer = EntryBuffer()
        # Test error
        self.assertRaises(TypeError, entry_buffer.insert_text, position=str())
        self.assertRaises(TypeError, entry_buffer.insert_text, chars=int())
        self.assertRaises(TypeError, entry_buffer.insert_text, n_chars=str())
        # test unprintable a character
        self.assertRaises(TypeError, entry_buffer.insert_text, chars=chr(128))

        # preparation
        value_1 = "hello"
        entry_buffer.set_text(chars=value_1)
        self.assertEqual(entry_buffer.get_text(), value_1)
        entry_buffer.insert_text(position=0, chars=".")
        self.assertEqual(entry_buffer.get_text(), ".hello")

        entry_buffer.set_text(chars=value_1)
        self.assertEqual(entry_buffer.get_text(), value_1)
        entry_buffer.insert_text(position=3, chars=".")
        self.assertEqual(entry_buffer.get_text(), "hel.lo")

        entry_buffer.set_text(chars=value_1)
        self.assertEqual(entry_buffer.get_text(), value_1)
        entry_buffer.insert_text(position=5, chars=".")
        self.assertEqual(entry_buffer.get_text(), "hello.")

        # check if that clamp well
        entry_buffer.set_text(chars=value_1)
        self.assertEqual(entry_buffer.get_text(), value_1)
        entry_buffer.insert_text(position=4560, chars=".")
        self.assertEqual(entry_buffer.get_text(), "hello.")

        entry_buffer.set_text(chars=value_1)
        self.assertEqual(entry_buffer.get_text(), value_1)
        entry_buffer.insert_text(position=-4560, chars=".")
        self.assertEqual(entry_buffer.get_text(), ".hello")

        # Check returned value
        entry_buffer.set_text(chars=value_1)
        self.assertEqual(entry_buffer.get_text(), value_1)
        returned_inserted_value = entry_buffer.insert_text(position=-4560, chars=".")
        self.assertEqual(entry_buffer.get_text(), ".hello")
        self.assertEqual(returned_inserted_value, 1)

        entry_buffer.set_text(chars=value_1)
        self.assertEqual(entry_buffer.get_text(), value_1)
        returned_inserted_value = entry_buffer.insert_text(position=-4560, chars="...")
        self.assertEqual(entry_buffer.get_text(), "...hello")
        self.assertEqual(returned_inserted_value, 3)

        # check with value ""
        value_2 = ""
        entry_buffer.set_text(chars=value_2)
        self.assertEqual(entry_buffer.get_text(), value_2)
        returned_inserted_value = entry_buffer.insert_text(position=0, chars=".")
        self.assertEqual(entry_buffer.get_text(), ".")
        self.assertEqual(returned_inserted_value, 1)

        # test of the world
        entry_buffer.set_text(chars="ha ha ha")
        self.assertEqual(entry_buffer.get_text(), "ha ha ha")
        entry_buffer.set_max_length(max_length=2)
        entry_buffer.insert_text(position=0, chars=".", n_chars=4556768)
        self.assertEqual(entry_buffer.get_text(), ".h")

    def test_EntryBuffer_delete_text(self):
        """Test EntryBuffer_delete_text()"""
        entry_buffer = EntryBuffer()
        # Test error
        self.assertRaises(TypeError, entry_buffer.delete_text, position=str())
        self.assertRaises(TypeError, entry_buffer.delete_text, position=0, n_chars=str())

        entry_buffer = EntryBuffer()
        entry_buffer.set_text(chars="hello")
        self.assertEqual(entry_buffer.get_text(), "hello")
        entry_buffer.delete_text(position=2, n_chars=1)
        self.assertEqual(entry_buffer.get_text(), "helo")
        entry_buffer.delete_text(position=5, n_chars=1)
        self.assertEqual(entry_buffer.get_text(), "helo")

        # test line 322
        entry_buffer = EntryBuffer()
        entry_buffer.set_text(chars="hello")
        self.assertEqual(entry_buffer.get_text(), "hello")
        entry_buffer.delete_text(position=2, n_chars=-1)
        self.assertEqual(entry_buffer.get_text(), "he")
        entry_buffer.delete_text(position=0, n_chars=-1)
        self.assertEqual(entry_buffer.get_text(), "")

        # test line 330
        entry_buffer = EntryBuffer()
        entry_buffer.set_text(chars="hello")
        self.assertEqual(entry_buffer.get_text(), "hello")
        entry_buffer.max_length = 2
        self.assertEqual(entry_buffer.get_text(), "hello")
        entry_buffer.delete_text(position=0, n_chars=1)
        self.assertEqual(len(entry_buffer.get_text()), entry_buffer.get_max_length())

        # test line 339
        entry_buffer = EntryBuffer()
        entry_buffer.set_text(chars="hello")
        self.assertEqual(entry_buffer.get_text(), "hello")
        returned_inserted_value = entry_buffer.delete_text()
        self.assertEqual(returned_inserted_value, 5)

    def test_internal_EntryBuffer__clamp_to_the_range(self):
        """Test EntryBuffer___clamp_to_the_range()"""
        entry_buffer = EntryBuffer()
        entry_buffer._min_length_hard_limit = 24
        entry_buffer._max_length_hard_limit = 42
        self.assertEqual(entry_buffer._clamp_to_the_range(checked_value=-6546545645646584), 24)
        self.assertEqual(entry_buffer._clamp_to_the_range(checked_value=6546545645646584), 42)

    def test_internal_EntryBuffer__emit_deleted_text(self):
        """Test EntryBuffer._emit_deleted_text()"""
        entry_buffer = EntryBuffer().new()
        entry_buffer._emit_signal_deleted_text(position=0, n_chars=42, user_data=None)
        entry_buffer._emit_signal_deleted_text(position=0, n_chars=42, user_data=dict())

        # test raise
        self.assertRaises(TypeError, entry_buffer._emit_signal_deleted_text, position=str(), n_chars=42, user_data=None)
        self.assertRaises(TypeError, entry_buffer._emit_signal_deleted_text, position=0, n_chars=str(), user_data=None)
        self.assertRaises(TypeError, entry_buffer._emit_signal_deleted_text, position=0, n_chars=42, user_data=int())

    def test_internal_EntryBuffer__emit_inserted_text(self):
        """Test EntryBuffer._emit_inserted_text()"""
        entry_buffer = EntryBuffer().new()
        entry_buffer._emit_signal_inserted_text(position=0, chars="", n_chars=42, user_data=None)
        entry_buffer._emit_signal_inserted_text(position=0, chars="", n_chars=42, user_data=dict())

        # test raise
        self.assertRaises(
            TypeError, entry_buffer._emit_signal_inserted_text, position=str(), chars="", n_chars=42, user_data=dict()
        )
        self.assertRaises(
            TypeError, entry_buffer._emit_signal_inserted_text, position=0, chars=chr(128), n_chars=42, user_data=dict()
        )
        self.assertRaises(
            TypeError, entry_buffer._emit_signal_inserted_text, position=0, chars="", n_chars=str(), user_data=dict()
        )
        self.assertRaises(
            TypeError, entry_buffer._emit_signal_inserted_text, position=0, chars="", n_chars=str(), user_data=int()
        )
