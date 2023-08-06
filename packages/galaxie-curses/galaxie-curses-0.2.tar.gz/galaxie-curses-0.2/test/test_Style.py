#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from random import randint
import sys
import os

# Require when you haven't GLXCurses as default Package
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

import GLXCurses


# Unittest
class TestStyle(unittest.TestCase):

    def setUp(self):
        # Before the test start
        # Require for init the screen
        self.application = GLXCurses.Application()
        # The component to test
        self.style = GLXCurses.Style()

    def tearDown(self):
        # When the test is finish
        # Require for ask to curse to clean up it
        self.application.close()

    # Tests
    def test_get_default_attribute_states(self):
        """Test Style.get_default_attribute_states()"""
        default_attribute_states = self.style.get_default_attribute_states()
        # Check first level dictionary
        self.assertEqual(type(default_attribute_states), type(dict()))
        # For each key's
        for attribute in ['text_fg', 'bg', 'light', 'dark', 'mid', 'text', 'base', 'black', 'white']:
            # Check if the key value is a dictionary
            self.assertEqual(type(default_attribute_states[attribute]), type(dict()))
            # For each key value, in that case a sub dictionary
            for state in ['STATE_NORMAL', 'STATE_ACTIVE', 'STATE_PRELIGHT', 'STATE_SELECTED', 'STATE_INSENSITIVE']:
                # Check if the key value is a string
                self.assertEqual(type(default_attribute_states[attribute][state]), type(str()))

    def test_get_color_pair(self):
        """Test Style.get_curses_color_pair()"""
        # Check if fg='WHITE', bg='BLACK' first in the list
        self.assertEqual(self.style.get_color_pair(foreground='WHITE', background='BLACK'), 2097152)

        # Check if fg='WHITE', bg='BLUE' return a int type
        self.assertEqual(type(self.style.get_color_pair(foreground='WHITE', background='BLUE')), type(int()))

        # Check if fg='WHITE', bg='BLUE' return a value > 0
        self.assertGreater(self.style.get_color_pair(foreground='WHITE', background='BLUE'), 0)

        # Check if fg='RED', bg='BLUE' return a value > 0
        self.assertGreater(self.style.get_color_pair(foreground='RED', background='BLUE'), 0)

    def test_set_get_attribute_states(self):
        """Test Style.get_attribute_states()"""
        # Load a valid Style
        self.style.set_attribute_states(self.style.get_default_attribute_states())

        # Load the Valid Style
        attribute_states = self.style.get_attribute_states()
        # Check first level dictionary
        self.assertEqual(type(attribute_states), type(dict()))
        # For each key's
        for attribute in ['text_fg', 'bg', 'light', 'dark', 'mid', 'text', 'base', 'black', 'white']:
            # Check if the key value is a dictionary
            self.assertEqual(type(attribute_states[attribute]), type(dict()))
            # For each key value, in that case a sub dictionary
            for state in ['STATE_NORMAL', 'STATE_ACTIVE', 'STATE_PRELIGHT', 'STATE_SELECTED', 'STATE_INSENSITIVE']:
                # Check if the key value is a string
                self.assertEqual(type(attribute_states[attribute][state]), type(str()))

        # Try to change style
        attribute_states = self.style.get_default_attribute_states()
        attribute_states['text_fg']['STATE_NORMAL'] = 'YELLOW'
        self.style.set_attribute_states(attribute_states)

        # Check if not a dictionary
        self.assertRaises(TypeError, self.style.set_attribute_states, float(randint(1, 42)))

        # Check raise with wrong Style
        attribute_states = dict()

        # Check with a empty dictionary
        self.assertRaises(KeyError, self.style.set_attribute_states, attribute_states)

        # Check with first level dictionary it look ok
        attribute_states['text_fg'] = dict()
        attribute_states['bg'] = dict()
        attribute_states['light'] = dict()
        attribute_states['dark'] = dict()
        attribute_states['mid'] = dict()
        attribute_states['text'] = dict()
        attribute_states['base'] = dict()
        attribute_states['black'] = dict()
        attribute_states['white'] = dict()
        self.assertRaises(KeyError, self.style.set_attribute_states, attribute_states)

        attribute_states = self.style.get_attribute_states()
        attribute_states['text_fg'] = list()
        self.assertRaises(TypeError, self.style.set_attribute_states, attribute_states)

        attribute_states = self.style.get_default_attribute_states()
        attribute_states['text_fg']['STATE_NORMAL'] = int(42)
        self.assertRaises(TypeError, self.style.set_attribute_states, attribute_states)

    # Internal Method test
    # Curses colors
    def test__get__set_allowed_fg_colors(self):
        """Test Style curses colors internal list 'get' and 'set' method's"""
        tested_colors_list = ['BLACK', 'WHITE']
        self.style._set_allowed_fg_colors(allowed_fg_colors=tested_colors_list)
        self.assertEqual(tested_colors_list, self.style._get_allowed_fg_colors())
        self.assertRaises(TypeError, self.style._set_allowed_fg_colors, float(randint(1, 42)))

    def test__gen_allowed_fg_colors(self):
        """Test Style allowed foreground colors list generation method"""
        # Set a empty list as curses colors
        self.style._set_allowed_fg_colors(allowed_fg_colors=list())
        # The curses_colors_list should be empty
        self.assertEqual(list(), self.style._get_allowed_fg_colors())
        # Generate the curses colors list
        self.style._gen_allowed_fg_colors()
        # The curses_colors_list should still be a list type
        self.assertEqual(type(list()), type(self.style._get_allowed_fg_colors()))
        # The curses_colors_list should not be a empty list
        self.assertGreater(len(self.style._get_allowed_fg_colors()), len(list()))

    def test__get__set_allowed_bg_colors(self):
        """Test Style curses colors internal list 'get' and 'set' method's"""
        tested_colors_list = ['BLACK', 'WHITE']
        self.style._set_allowed_bg_colors(allowed_bg_colors=tested_colors_list)
        self.assertEqual(tested_colors_list, self.style._get_allowed_bg_colors())
        self.assertRaises(TypeError, self.style._set_allowed_bg_colors, float(randint(1, 42)))

    def test__gen_allowed_bg_colors(self):
        """Test Style allowed background colors list generation method"""
        # Set a empty list as curses colors
        self.style._set_allowed_bg_colors(allowed_bg_colors=list())
        # The curses_colors_list should be empty
        self.assertEqual(list(), self.style._get_allowed_bg_colors())
        # Generate the curses colors list
        self.style._gen_allowed_bg_colors()
        # The curses_colors_list should still be a list type
        self.assertEqual(type(list()), type(self.style._get_allowed_bg_colors()))
        # The curses_colors_list should not be a empty list
        self.assertGreater(len(self.style._get_allowed_bg_colors()), len(list()))

    # Curses Colors pairs
    def test__get__set_curses_colors_pairs(self):
        """Test Style allowed curses colors pairs internal list 'get' and 'set' method's"""
        tested_colors_list = ['BLACK', 'WHITE']
        self.style._set_text_pairs(text_pairs=tested_colors_list)
        self.assertEqual(tested_colors_list, self.style._get_text_pairs())

    def test__set_curses_colors_pairs_raise(self):
        """Test Style raise TypeError of _set_curses_colors_pairs()"""
        self.assertRaises(TypeError, self.style._set_text_pairs, float(randint(1, 42)))

    def test__gen_curses_colors_pairs(self):
        """Test Style allowed curses colors pairs list generation method"""
        # Set a empty list as curses colors
        self.style._set_text_pairs(text_pairs=list())
        # The curses_colors_list should be empty
        self.assertEqual(list(), self.style._get_text_pairs())
        # Generate the curses colors list
        self.style._gen_curses_colors_pairs()
        # The curses_colors_list should still be a list type
        self.assertEqual(type(list()), type(self.style._get_text_pairs()))
        # The curses_colors_list should not be a empty list
        self.assertGreater(len(self.style._get_text_pairs()), len(list()))
