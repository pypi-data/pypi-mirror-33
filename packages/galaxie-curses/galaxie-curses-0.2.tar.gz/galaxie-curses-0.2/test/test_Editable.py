#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import GLXC
from GLXCurses import Entry
from GLXCurses import Label
from GLXCurses.Editable import Editable
from GLXCurses.Utils import glxc_type

import unittest
import pyperclip
from time import sleep
from random import randint


# Unittest
class TestRange(unittest.TestCase):

    # Test
    def test_Editable_select_region(self):
        """Test Editable.select_region()"""
        editable = Editable()
        entry = Entry()
        # check default value
        self.assertEqual(editable.start_pos, None)
        self.assertEqual(editable.end_pos, None)
        self.assertEqual(entry.start_pos, None)
        self.assertEqual(entry.end_pos, None)

        # make test
        entry.set_text("Hello")
        editable.select_region(
            editable=entry,
            start_pos=1,
            end_pos=len(entry.get_text())
        )
        self.assertEqual(entry.start_pos, 1)
        self.assertEqual(entry.end_pos, len(entry.get_text()))

        # check back to default
        editable.select_region(editable=entry)

        self.assertEqual(entry.start_pos, None)
        self.assertEqual(entry.end_pos, None)

        # only start_pos is set
        editable.select_region(editable=entry)
        editable.select_region(
            editable=entry,
            start_pos=1
        )
        self.assertEqual(entry.start_pos, 1)
        self.assertEqual(entry.end_pos, None)

        # only end_pos is set
        editable.select_region(editable=entry)
        editable.select_region(
            editable=entry,
            end_pos=len(entry.get_text())
        )
        self.assertEqual(entry.start_pos, None)
        self.assertEqual(entry.end_pos, len(entry.get_text()))

        # check end_pos -1
        entry.set_text("Hello")
        editable.select_region(
            editable=entry,
            start_pos=1,
            end_pos=-1
        )
        self.assertEqual(entry.start_pos, 1)
        self.assertEqual(entry.end_pos, len(entry.get_text()))

        # check if editable is None (Strange test) but in fact Editable Class is not a GLXC.Editable
        self.assertRaises(
            TypeError,
            editable.select_region,
            editable=None,
            start_pos=1,
            end_pos=len(entry.get_text())
        )

        # check errors
        # editable is not GLXCurses type
        self.assertRaises(
            TypeError,
            editable.select_region,
            editable=42,
            start_pos=1,
            end_pos=len(entry.get_text())
        )
        # editable is not a GLXC.Editable
        label = Label()
        self.assertRaises(
            TypeError,
            editable.select_region,
            editable=label,
            start_pos=1,
            end_pos=len(entry.get_text())
        )
        # start_pos is not a int or None
        self.assertRaises(
            TypeError,
            editable.select_region,
            editable=entry,
            start_pos=str("Hello"),
            end_pos=len(entry.get_text())
        )
        # end_pos is not a int or None
        self.assertRaises(
            TypeError,
            editable.select_region,
            editable=entry,
            start_pos=1,
            end_pos=str("Hello")
        )

    def test_Editable_get_selection_bounds(self):
        """Test Editable.get_selection_bounds()"""
        editable = Editable()
        entry = Entry()
        entry.set_text("Hello")

        # check default value
        self.assertEqual(editable.start_pos, None)
        self.assertEqual(editable.end_pos, None)
        self.assertEqual(entry.start_pos, None)
        self.assertEqual(entry.end_pos, None)
        self.assertFalse(editable.get_selection_bounds(editable=entry))
        self.assertFalse(entry.get_selection_bounds())

        # Make tests
        entry.start_pos = 1
        entry.end_pos = None
        self.assertFalse(editable.get_selection_bounds(editable=entry))
        self.assertFalse(entry.get_selection_bounds())

        entry.start_pos = None
        entry.end_pos = 1
        self.assertFalse(editable.get_selection_bounds(editable=entry))
        self.assertFalse(entry.get_selection_bounds())

        entry.start_pos = None
        entry.end_pos = None
        self.assertFalse(editable.get_selection_bounds(editable=entry))
        self.assertFalse(entry.get_selection_bounds())

        entry.start_pos = 1
        entry.end_pos = 5
        self.assertTrue(editable.get_selection_bounds(editable=entry))
        self.assertTrue(entry.get_selection_bounds())

        # check errors
        # editable is not GLXCurses type
        self.assertRaises(
            TypeError,
            editable.get_selection_bounds,
            editable=42
        )
        # editable is not a GLXC.Editable
        label = Label()
        self.assertRaises(
            TypeError,
            editable.get_selection_bounds,
            editable=label
        )

    def test_Editable_insert_text(self):
        """Test Editable.insert_text()"""
        editable = Editable()
        entry = Entry()

        entry.set_text("")
        editable.insert_text(
            editable=entry,
            new_text="Hello",
            position=0
        )
        self.assertEqual(entry.get_text(), "Hello")

        # check witch selection
        entry.set_text("H")
        entry.start_pos = 0
        entry.end_pos = 1
        editable.insert_text(
            editable=entry,
            new_text="Hello",
            position=0
        )
        self.assertEqual(entry.get_text(), "Hello")

        # test when position is None
        entry.position = len(entry.get_text())
        editable.insert_text(
            editable=entry,
            new_text="2"
        )
        self.assertEqual(entry.get_text(), "Hello2")

        editable.insert_text(
            editable=entry,
            new_text="4",
            new_text_length=1,
            position=0
        )
        self.assertEqual(entry.get_text(), "4Hello2")

        # test is position is < as text length
        entry.set_text("Hello")
        entry.position = 42
        editable.insert_text(
            editable=entry,
            new_text="42",
            new_text_length=2,
            position=30
        )
        self.assertEqual(entry.get_text(), "Hello42")

        # test is new_text_length is None


        # check errors
        # editable is not GLXCurses type
        self.assertRaises(
            TypeError,
            editable.insert_text,
            editable=42
        )
        # editable is not a GLXC.Editable
        label = Label()
        self.assertRaises(
            TypeError,
            editable.insert_text,
            editable=label
        )

        # check if editable is None (Strange test) but in fact Editable Class is not a GLXC.Editable
        self.assertRaises(
            TypeError,
            editable.insert_text,
            editable=None,
            new_text="4",
            new_text_length=1,
            position=0
        )

        # check new_text type
        self.assertRaises(
            TypeError,
            editable.insert_text,
            editable=entry,
            new_text=int(42),
            new_text_length=1,
            position=0
        )

        # check new_text_length type
        self.assertRaises(
            TypeError,
            editable.insert_text,
            editable=entry,
            new_text="42",
            new_text_length=str("1"),
            position=0
        )

        # check new_text_length type
        self.assertRaises(
            TypeError,
            editable.insert_text,
            editable=entry,
            new_text="42",
            new_text_length=1,
            position=str("0")
        )

    def test_Editable_delete_text(self):
        """Test Editable.delete_text()"""
        editable = Editable()
        entry = Entry()
        label = Label()

        # check default value
        self.assertEqual(entry.position, 0)
        self.assertEqual(entry.start_pos, None)
        self.assertEqual(entry.end_pos, None)
        # make test
        entry.set_text("Hello")
        editable.delete_text(
            editable=entry,
            start_pos=2,
            end_pos=4
        )
        self.assertEqual(entry.get_text(), "He")
        # test end_pos -1
        entry.set_text("Hello")
        editable.delete_text(
            editable=entry,
            start_pos=1,
            end_pos=-1
        )
        self.assertEqual(entry.get_text(), "H")
        # test without end_pos
        entry.set_text("Hello")
        editable.delete_text(
            editable=entry,
            start_pos=1,
            end_pos=None
        )
        self.assertEqual(entry.get_text(), "Hllo")
        # test if delete position
        # test without end_pos
        entry.set_text("Hello")
        entry.position = 0
        editable.delete_text(
            editable=entry,
            start_pos=None,
            end_pos=None
        )
        self.assertEqual(entry.get_text(), "ello")
        # is editable.position is none
        entry.set_text("Hello")
        entry.start_pos = 0
        editable.delete_text(
            editable=entry,
            start_pos=None,
            end_pos=None
        )
        self.assertEqual(entry.get_text(), "ello")
        #
        entry.set_text("Hello")
        editable.delete_text(
            editable=entry,
            start_pos=5,
            end_pos=1
        )
        self.assertEqual(entry.get_text(), "H")
        # check error
        # Not a GLXCCurses Type
        # check if editable is None (Strange test) but in fact Editable Class is not a GLXC.Editable
        self.assertRaises(
            TypeError,
            editable.delete_text,
            editable=None,
            start_pos=None,
            end_pos=None
        )
        # Not a Editable instance
        self.assertRaises(
            TypeError,
            editable.delete_text,
            editable=label,
            start_pos=None,
            end_pos=None
        )
        # start_pos is not Int or None
        self.assertRaises(
            TypeError,
            editable.delete_text,
            editable=entry,
            start_pos=str("42"),
            end_pos=None
        )
        # end_pos is not Int or None
        self.assertRaises(
            TypeError,
            editable.delete_text,
            editable=entry,
            start_pos=None,
            end_pos=str("42")
        )

    def test_Editable_get_chars(self):
        """Test Editable.get_chars()"""
        editable = Editable()
        entry = Entry()

        # check witch selection
        entry.set_text("Hello")
        self.assertEqual(editable.get_chars(editable=entry, start_pos=0, end_pos=4), "Hello")
        self.assertEqual(editable.get_chars(editable=entry, start_pos=4, end_pos=0), "Hello")

        entry.start_pos = 0
        entry.end_pos = 4
        self.assertEqual(editable.get_chars(editable=entry), "Hello")

        # test password protetcion
        entry.set_visibility(False)
        self.assertEqual(editable.get_chars(editable=entry, start_pos=0, end_pos=4), "*****")

        entry.invisible_char = None
        self.assertEqual(editable.get_chars(editable=entry, start_pos=0, end_pos=4), "*****")

        self.assertRaises(
            TypeError,
            editable.get_chars,
            editable=None,
            start_pos=4,
            end_pos=0
        )

        self.assertRaises(
            ImportError,
            editable.get_chars,
            editable=Label(),
            start_pos=4,
            end_pos=0
        )

        self.assertRaises(
            TypeError,
            editable.get_chars,
            editable=entry,
            start_pos=str("Hello"),
            end_pos=0
        )

        self.assertRaises(
            TypeError,
            editable.get_chars,
            editable=entry,
            start_pos=4,
            end_pos=str("Hello")
        )

    def test_Editable_cut_clipboard(self):
        """Test Editable.cut_clipboard()"""
        editable = Editable()
        entry = Entry()
        # Normal case
        value = "Hello"
        entry.set_text(value)
        editable.select_region(
            editable=entry,
            start_pos=0,
            end_pos=-1
        )
        self.assertTrue(editable.get_selection_bounds(editable=entry))
        editable.cut_clipboard(
            editable=entry
        )
        self.assertFalse(editable.get_selection_bounds(editable=entry))

        self.assertEquals(pyperclip.paste(), value)
        sleep(randint(1, 100) / 100)
        self.assertEquals(entry.get_text(), "")
        # test when start_pos is bigger as end_pos
        value = "Hello"
        entry.set_text(value)
        editable.select_region(
            editable=entry,
            start_pos=4,
            end_pos=0
        )
        self.assertTrue(editable.get_selection_bounds(editable=entry))
        editable.cut_clipboard(
            editable=entry
        )
        self.assertEquals(pyperclip.paste(), value)
        sleep(randint(1, 100) / 100)
        self.assertFalse(editable.get_selection_bounds(editable=entry))
        self.assertEquals(entry.get_text(), "")

        # test when after a cut position is reset
        value = "Hello42"
        entry.set_text(value)
        entry.position = len(entry.get_text())

        editable.select_region(
            editable=entry,
            start_pos=5,
            end_pos=6
        )
        self.assertTrue(editable.get_selection_bounds(editable=entry))
        editable.cut_clipboard(
            editable=entry
        )
        self.assertEquals(pyperclip.paste(), '42')
        sleep(randint(1, 100) / 100)
        self.assertFalse(editable.get_selection_bounds(editable=entry))
        self.assertEquals(entry.get_text(), "Hello")

        # check error
        self.assertRaises(TypeError, editable.cut_clipboard, editable=float(42.0))
        self.assertRaises(ImportError, editable.cut_clipboard, editable=Label())
        self.assertRaises(TypeError, editable.cut_clipboard, editable=None)

    def test_Editable_copy_clipboard(self):
        """Test Editable.copy_clipboard()"""
        editable = Editable()
        entry = Entry()
        # Normal case
        value = "Hello"
        entry.set_text(value)
        editable.select_region(
            editable=entry,
            start_pos=0,
            end_pos=-1
        )
        self.assertTrue(editable.get_selection_bounds(editable=entry))
        editable.copy_clipboard(
            editable=entry
        )
        self.assertEquals(pyperclip.paste(), value)
        sleep(randint(1, 100) / 100)
        self.assertTrue(editable.get_selection_bounds(editable=entry))
        self.assertEquals(entry.get_text(), value)
        # test when start_pos is bigger as end_pos
        value = "Hello"
        entry.set_text(value)
        editable.select_region(
            editable=entry,
            start_pos=4,
            end_pos=0
        )
        self.assertTrue(editable.get_selection_bounds(editable=entry))
        editable.copy_clipboard(
            editable=entry
        )
        self.assertEquals(pyperclip.paste(), value)
        sleep(randint(1, 100) / 100)
        self.assertTrue(editable.get_selection_bounds(editable=entry))
        self.assertEquals(entry.get_text(), value)

        # check error
        self.assertRaises(TypeError, editable.copy_clipboard, editable=float(42.0))
        self.assertRaises(ImportError, editable.copy_clipboard, editable=Label())
        self.assertRaises(TypeError, editable.copy_clipboard, editable=None)

    def test_Editable_paste_clipboard(self):
        """Test Editable.paste_clipboard()"""
        editable = Editable()
        entry = Entry()
        entry.set_text('')

        pyperclip.copy('Hello')
        sleep(randint(1, 100) / 100)
        entry.set_text('01234')
        editable.select_region(
            editable=entry,
            start_pos=0,
            end_pos=entry.get_text_length()
        )
        self.assertTrue(editable.get_selection_bounds(editable=entry))
        editable.paste_clipboard(
            editable=entry
        )

        self.assertEquals(entry.get_text(), 'Hello')

        # check error
        self.assertRaises(TypeError, editable.paste_clipboard, editable=float(42.0))
        self.assertRaises(ImportError, editable.paste_clipboard, editable=Label())
        self.assertRaises(TypeError, editable.paste_clipboard, editable=None)

    def test_Editable_delete_selection(self):
        """Test Editable.delete_selection()"""
        editable = Editable()
        entry = Entry()

        # normal case
        entry.set_text('Hello')
        editable.select_region(
            editable=entry,
            start_pos=0,
            end_pos=entry.get_text_length()
        )
        self.assertTrue(editable.get_selection_bounds(editable=entry))
        editable.delete_selection(
            editable=entry
        )
        self.assertFalse(editable.get_selection_bounds(editable=entry))
        self.assertEquals(entry.get_text(), '')

        # check when start_pos is > as end_pos
        entry.set_text('Hello')
        editable.select_region(
            editable=entry,
            start_pos=entry.get_text_length(),
            end_pos=0
        )
        self.assertTrue(editable.get_selection_bounds(editable=entry))
        editable.delete_selection(
            editable=entry
        )
        self.assertFalse(editable.get_selection_bounds(editable=entry))
        self.assertEquals(entry.get_text(), '')

        # check error
        self.assertRaises(TypeError, editable.delete_selection, editable=float(42.0))
        self.assertRaises(ImportError, editable.delete_selection, editable=Label())
        self.assertRaises(TypeError, editable.delete_selection, editable=None)
        self.assertRaises(TypeError, editable.delete_selection, editable=entry, position=str("42"))

    def test_Editable_set_position(self):
        """Test Editable.set_position()"""
        editable = Editable()
        entry = Entry()
        # check default value
        self.assertEqual(editable.position, 0)
        # make the test
        entry.set_text("Hello")
        # normal situation
        editable.set_position(
            editable=entry,
            position=3
        )
        self.assertEqual(entry.position, 3)
        # verify -1
        editable.set_position(
            editable=entry,
            position=-1
        )
        self.assertEqual(entry.position, len(entry.get_text()))
        # test clamp to zero
        editable.set_position(
            editable=entry,
            position=-42
        )
        self.assertEqual(entry.position, 0)

        # check strange case
        entry.set_text("")
        editable.set_position(editable=entry, position=3)
        self.assertEqual(entry.position, 0)

        entry.set_text("")
        editable.set_position(editable=entry, position=-1)
        self.assertEqual(entry.position, 0)

        entry.set_text("Hello")
        editable.set_position(editable=entry, position=0)
        self.assertEqual(entry.position, 0)

        # check error
        self.assertRaises(TypeError, editable.set_position, float(42.0), position=-1)
        self.assertRaises(TypeError, editable.set_position, Label(), position=-1)
        self.assertRaises(TypeError, editable.set_position, entry, position=str("Hello"))

    def test_Editable_get_position(self):
        """Test Editable.get_position()"""
        entry = Entry()
        editable = Editable()
        # check default value
        self.assertEqual(editable.get_position(editable=entry), 0)
        # make test
        entry.position = 42
        self.assertEqual(editable.get_position(editable=entry), 42)

        # Check for error
        self.assertRaises(TypeError, editable.get_position, editable=float(42.0))
        self.assertRaises(ImportError, editable.get_position, editable=Label())
        self.assertRaises(TypeError, editable.get_position, editable=None)

    def test_Editable_set_editable(self):
        """Test Editable.set_editable"""
        entry = Entry()
        editable = Editable()
        # check default value
        self.assertEqual(entry.is_editable, True)
        # make test
        editable.set_editable(editable=entry, is_editable=False)
        self.assertEqual(entry.is_editable, False)
        # test back to default
        editable.set_editable(editable=entry)
        self.assertEqual(entry.is_editable, True)
        # Check error
        self.assertRaises(TypeError, editable.set_editable, is_editable=str("Hello"))

        # Check for error
        self.assertRaises(TypeError, editable.set_editable, editable=float(42.0))
        self.assertRaises(ImportError, editable.set_editable, editable=Label())
        self.assertRaises(TypeError, editable.set_editable, editable=None)
        self.assertRaises(TypeError, editable.set_editable, editable=entry, is_editable=str('42'))

    def test_Editable_get_editable(self):
        """Test Editable.get_editable"""
        entry = Entry()
        editable = Editable()
        # check default value
        self.assertEqual(editable.get_editable(editable=entry), True)
        # make test
        entry.is_editable = 42
        self.assertEqual(editable.get_editable(editable=entry), 42)

        # Check for error
        self.assertRaises(TypeError, editable.get_editable, editable=float(42.0))
        self.assertRaises(ImportError, editable.get_editable, editable=Label())
        self.assertRaises(TypeError, editable.get_editable, editable=None)
