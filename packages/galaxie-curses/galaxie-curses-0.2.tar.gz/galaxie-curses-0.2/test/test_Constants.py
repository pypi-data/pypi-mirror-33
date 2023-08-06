#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

import unittest
from GLXCurses.Constants import Constants
from GLXCurses import GLXC


# Unittest
class TestConstants(unittest.TestCase):
    def test_Constants_set(self):
        """Test Constants set"""
        const = Constants()
        const.hello = 42
        self.assertEqual(const.hello, 42)
        self.assertRaises(Constants.ConstError, const.__setattr__, 'hello', 42)

    def test_Constants_get(self):
        """Test Constants get"""
        const = Constants()
        const.hello = 42
        self.assertEqual(const.__getattr__('hello'), 42)
        self.assertRaises(Constants.ConstError, const.__getattr__, 'im_not')

    def test_Constants_BaselinePosition(self):
        """Test Constants BaselinePosition"""
        self.assertEqual(GLXC.BASELINE_POSITION_TOP, 'TOP')
        self.assertEqual(GLXC.BASELINE_POSITION_CENTER, 'CENTER')
        self.assertEqual(GLXC.BASELINE_POSITION_BOTTOM, 'BOTTOM')

        self.assertEqual(
            GLXC.BaselinePosition,
            [
                GLXC.BASELINE_POSITION_TOP,
                GLXC.BASELINE_POSITION_CENTER,
                GLXC.BASELINE_POSITION_BOTTOM
            ]
        )

    def test_Constants_DeleteType(self):
        """Test Constants DeleteType"""
        self.assertEqual(GLXC.DELETE_CHARS, 'CHARS')
        self.assertEqual(GLXC.DELETE_WORD_ENDS, 'WORD_ENDS')
        self.assertEqual(GLXC.DELETE_WORDS, 'WORDS')
        self.assertEqual(GLXC.DELETE_DISPLAY_LINES, 'DISPLAY_LINES')
        self.assertEqual(GLXC.DELETE_DISPLAY_LINE_ENDS, 'DISPLAY_LINE_ENDS')
        self.assertEqual(GLXC.DELETE_PARAGRAPH_ENDS, 'PARAGRAPH_ENDS')
        self.assertEqual(GLXC.DELETE_PARAGRAPHS, 'PARAGRAPHS')
        self.assertEqual(GLXC.DELETE_WHITESPACE, 'WHITESPACE')

        self.assertEqual(
            GLXC.DeleteType,
            [
                GLXC.DELETE_CHARS,
                GLXC.DELETE_WORD_ENDS,
                GLXC.DELETE_WORDS,
                GLXC.DELETE_DISPLAY_LINES,
                GLXC.DELETE_DISPLAY_LINE_ENDS,
                GLXC.DELETE_PARAGRAPH_ENDS,
                GLXC.DELETE_PARAGRAPHS,
                GLXC.DELETE_WHITESPACE
            ]
        )

    def test_Constants_DirectionType(self):
        """Test Constants DirectionType"""
        self.assertEqual(GLXC.DIR_TAB_FORWARD, 'TAB_FORWARD')
        self.assertEqual(GLXC.DIR_TAB_BACKWARD, 'TAB_BACKWARD')
        self.assertEqual(GLXC.DIR_UP, 'UP')
        self.assertEqual(GLXC.DIR_DOWN, 'DOWN')
        self.assertEqual(GLXC.DIR_LEFT, 'LEFT')
        self.assertEqual(GLXC.DIR_RIGHT, 'RIGHT')
        self.assertEqual(
            GLXC.DirectionType,
            [
                GLXC.DIR_TAB_FORWARD,
                GLXC.DIR_TAB_BACKWARD,
                GLXC.DIR_UP,
                GLXC.DIR_DOWN,
                GLXC.DIR_LEFT,
                GLXC.DIR_RIGHT
            ]
        )

    def test_Constants_Justification(self):
        """Test Constants Justification"""
        self.assertEqual(GLXC.JUSTIFY_LEFT, 'LEFT')
        self.assertEqual(GLXC.JUSTIFY_RIGHT, 'RIGHT')
        self.assertEqual(GLXC.JUSTIFY_CENTER, 'CENTER')
        self.assertEqual(GLXC.JUSTIFY_FILL, 'FILL')
        self.assertEqual(
            GLXC.Justification,
            [
                GLXC.JUSTIFY_LEFT,
                GLXC.JUSTIFY_CENTER,
                GLXC.JUSTIFY_RIGHT,
                GLXC.JUSTIFY_FILL
            ]
        )

    def test_Constants_MovementStep(self):
        """Test Constants MovementStep"""
        self.assertEqual(GLXC.MOVEMENT_LOGICAL_POSITIONS, 'LOGICAL_POSITIONS')
        self.assertEqual(GLXC.MOVEMENT_VISUAL_POSITIONS, 'VISUAL_POSITIONS')
        self.assertEqual(GLXC.MOVEMENT_WORDS, 'WORDS')
        self.assertEqual(GLXC.MOVEMENT_DISPLAY_LINES, 'DISPLAY_LINES')
        self.assertEqual(GLXC.MOVEMENT_DISPLAY_LINE_ENDS, 'DISPLAY_LINE_ENDS')
        self.assertEqual(GLXC.MOVEMENT_PARAGRAPHS, 'PARAGRAPHS')
        self.assertEqual(GLXC.MOVEMENT_PARAGRAPH_ENDS, 'PARAGRAPH_ENDS')
        self.assertEqual(GLXC.MOVEMENT_PAGES, 'PAGES')
        self.assertEqual(GLXC.MOVEMENT_BUFFER_ENDS, 'BUFFER_ENDS')
        self.assertEqual(GLXC.MOVEMENT_HORIZONTAL_PAGES, 'HORIZONTAL_PAGES')
        self.assertEqual(
            GLXC.MovementStep,
            [
                GLXC.MOVEMENT_LOGICAL_POSITIONS,
                GLXC.MOVEMENT_VISUAL_POSITIONS,
                GLXC.MOVEMENT_WORDS,
                GLXC.MOVEMENT_DISPLAY_LINES,
                GLXC.MOVEMENT_DISPLAY_LINE_ENDS,
                GLXC.MOVEMENT_PARAGRAPHS,
                GLXC.MOVEMENT_PARAGRAPH_ENDS,
                GLXC.MOVEMENT_PAGES,
                GLXC.MOVEMENT_BUFFER_ENDS,
                GLXC.MOVEMENT_HORIZONTAL_PAGES
            ]
        )

    def test_Constants_Orientation(self):
        """Test Constants Orientation"""
        self.assertEqual(GLXC.ORIENTATION_HORIZONTAL, 'HORIZONTAL')
        self.assertEqual(GLXC.ORIENTATION_VERTICAL, 'VERTICAL')
        self.assertEqual(
            GLXC.Orientation,
            [
                GLXC.ORIENTATION_HORIZONTAL,
                GLXC.ORIENTATION_VERTICAL
            ]
        )

    def test_Constants_PackType(self):
        """Test Constants PackType"""
        self.assertEqual(GLXC.PACK_START, 'START')
        self.assertEqual(GLXC.PACK_END, 'END')
        self.assertEqual(
            GLXC.PackType,
            [
                GLXC.PACK_START,
                GLXC.PACK_END
            ]
        )

    def test_Constants_PositionType(self):
        """Test Constants PositionType"""
        self.assertEqual(GLXC.POS_LEFT, 'LEFT')
        self.assertEqual(GLXC.POS_RIGHT, 'RIGHT')
        self.assertEqual(GLXC.POS_TOP, 'TOP')
        self.assertEqual(GLXC.POS_BOTTOM, 'BOTTOM')
        self.assertEqual(
            GLXC.PositionType,
            [
                GLXC.POS_LEFT,
                GLXC.POS_RIGHT,
                GLXC.POS_CENTER,
                GLXC.POS_TOP,
                GLXC.POS_BOTTOM
            ]
        )

    def test_Constants_ReliefStyle(self):
        """Test Constants ReliefStyle"""
        self.assertEqual(GLXC.RELIEF_NORMAL, 'NORMAL')
        self.assertEqual(GLXC.RELIEF_HALF, 'HALF')
        self.assertEqual(GLXC.RELIEF_NONE, 'NONE')
        self.assertEqual(
            GLXC.ReliefStyle,
            [
                GLXC.RELIEF_NORMAL,
                GLXC.RELIEF_HALF,
                GLXC.RELIEF_NONE
            ]
        )

    def test_Constants_ScrollStep(self):
        """Test Constants ScrollStep"""
        self.assertEqual(GLXC.SCROLL_STEPS, 'STEPS')
        self.assertEqual(GLXC.SCROLL_PAGES, 'PAGES')
        self.assertEqual(GLXC.SCROLL_ENDS, 'ENDS')
        self.assertEqual(GLXC.SCROLL_HORIZONTAL_STEPS, 'HORIZONTAL_STEPS')
        self.assertEqual(GLXC.SCROLL_HORIZONTAL_PAGES, 'HORIZONTAL_PAGES')
        self.assertEqual(GLXC.SCROLL_HORIZONTAL_ENDS, 'HORIZONTAL_ENDS')
        self.assertEqual(
            GLXC.ScrollStep,
            [
                GLXC.SCROLL_STEPS,
                GLXC.SCROLL_PAGES,
                GLXC.SCROLL_ENDS,
                GLXC.SCROLL_HORIZONTAL_STEPS,
                GLXC.SCROLL_HORIZONTAL_PAGES,
                GLXC.SCROLL_HORIZONTAL_ENDS
            ]
        )

    def test_Constants_ScrollType(self):
        """Test Constants ScrollType"""
        self.assertEqual(GLXC.SCROLL_NONE, 'NONE')
        self.assertEqual(GLXC.SCROLL_JUMP, 'JUMP')
        self.assertEqual(GLXC.SCROLL_STEP_BACKWARD, 'STEP_BACKWARD')
        self.assertEqual(GLXC.SCROLL_STEP_FORWARD, 'STEP_FORWARD')
        self.assertEqual(GLXC.SCROLL_PAGE_BACKWARD, 'PAGE_BACKWARD')
        self.assertEqual(GLXC.SCROLL_PAGE_FORWARD, 'PAGE_FORWARD')
        self.assertEqual(GLXC.SCROLL_STEP_UP, 'STEP_UP')
        self.assertEqual(GLXC.SCROLL_STEP_DOWN, 'STEP_DOWN')
        self.assertEqual(GLXC.SCROLL_PAGE_UP, 'PAGE_UP')
        self.assertEqual(GLXC.SCROLL_PAGE_DOWN, 'PAGE_DOWN')
        self.assertEqual(GLXC.SCROLL_STEP_LEFT, 'STEP_LEFT')
        self.assertEqual(GLXC.SCROLL_STEP_RIGHT, 'STEP_RIGHT')
        self.assertEqual(GLXC.SCROLL_PAGE_LEFT, 'PAGE_LEFT')
        self.assertEqual(GLXC.SCROLL_PAGE_RIGHT, 'PAGE_RIGHT')
        self.assertEqual(GLXC.SCROLL_START, 'START')
        self.assertEqual(GLXC.SCROLL_END, 'END')
        self.assertEqual(
            GLXC.ScrollType,
            [
                GLXC.SCROLL_NONE,
                GLXC.SCROLL_JUMP,
                GLXC.SCROLL_STEP_BACKWARD,
                GLXC.SCROLL_STEP_FORWARD,
                GLXC.SCROLL_PAGE_BACKWARD,
                GLXC.SCROLL_PAGE_FORWARD,
                GLXC.SCROLL_STEP_UP,
                GLXC.SCROLL_STEP_DOWN,
                GLXC.SCROLL_PAGE_UP,
                GLXC.SCROLL_PAGE_DOWN,
                GLXC.SCROLL_STEP_LEFT,
                GLXC.SCROLL_STEP_RIGHT,
                GLXC.SCROLL_PAGE_LEFT,
                GLXC.SCROLL_PAGE_RIGHT,
                GLXC.SCROLL_START,
                GLXC.SCROLL_END
            ]
        )

    def test_Constants_SelectionMode(self):
        """Test Constants SelectionMode"""
        self.assertEqual(GLXC.SELECTION_NONE, 'NONE')
        self.assertEqual(GLXC.SELECTION_SINGLE, 'SINGLE')
        self.assertEqual(GLXC.SELECTION_BROWSE, 'BROWSE')
        self.assertEqual(GLXC.SELECTION_MULTIPLE, 'MULTIPLE')
        self.assertEqual(
            GLXC.SelectionMode,
            [
                GLXC.SELECTION_NONE,
                GLXC.SELECTION_SINGLE,
                GLXC.SELECTION_BROWSE,
                GLXC.SELECTION_MULTIPLE
            ]
        )

    def test_Constants_ShadowType(self):
        """Test Constants ShadowType"""
        self.assertEqual(GLXC.SHADOW_NONE, 'NONE')
        self.assertEqual(GLXC.SHADOW_IN, 'IN')
        self.assertEqual(GLXC.SHADOW_OUT, 'OUT')
        self.assertEqual(GLXC.SHADOW_ETCHED_IN, 'ETCHED_IN')
        self.assertEqual(GLXC.SHADOW_ETCHED_OUT, 'ETCHED_OUT')
        self.assertEqual(
            GLXC.ShadowType,
            [
                GLXC.SHADOW_NONE,
                GLXC.SHADOW_IN,
                GLXC.SHADOW_OUT,
                GLXC.SHADOW_ETCHED_IN,
                GLXC.SHADOW_ETCHED_OUT
            ]
        )

    def test_Constants_StateFlags(self):
        """Test Constants StateFlags"""
        self.assertEqual(GLXC.STATE_FLAG_NORMAL, 'NORMAL')
        self.assertEqual(GLXC.STATE_FLAG_ACTIVE, 'ACTIVE')
        self.assertEqual(GLXC.STATE_FLAG_PRELIGHT, 'PRELIGHT')
        self.assertEqual(GLXC.STATE_FLAG_SELECTED, 'SELECTED')
        self.assertEqual(GLXC.STATE_FLAG_INSENSITIVE, 'INSENSITIVE')
        self.assertEqual(GLXC.STATE_FLAG_INCONSISTENT, 'INCONSISTENT')
        self.assertEqual(GLXC.STATE_FLAG_FOCUSED, 'FOCUSED')
        self.assertEqual(GLXC.STATE_FLAG_BACKDROP, 'BACKDROP')
        self.assertEqual(GLXC.STATE_FLAG_DIR_LTR, 'DIR_LTR')
        self.assertEqual(GLXC.STATE_FLAG_DIR_RTL, 'DIR_RTL')
        self.assertEqual(GLXC.STATE_FLAG_LINK, 'LINK')
        self.assertEqual(GLXC.STATE_FLAG_VISITED, 'VISITED')
        self.assertEqual(GLXC.STATE_FLAG_CHECKED, 'CHECKED')
        self.assertEqual(GLXC.STATE_FLAG_DROP_ACTIVE, 'DROP_ACTIVE')
        self.assertEqual(
            GLXC.StateFlags,
            [
                GLXC.STATE_FLAG_NORMAL,
                GLXC.STATE_FLAG_ACTIVE,
                GLXC.STATE_FLAG_PRELIGHT,
                GLXC.STATE_FLAG_SELECTED,
                GLXC.STATE_FLAG_INSENSITIVE,
                GLXC.STATE_FLAG_INCONSISTENT,
                GLXC.STATE_FLAG_FOCUSED,
                GLXC.STATE_FLAG_BACKDROP,
                GLXC.STATE_FLAG_DIR_LTR,
                GLXC.STATE_FLAG_DIR_RTL,
                GLXC.STATE_FLAG_LINK,
                GLXC.STATE_FLAG_VISITED,
                GLXC.STATE_FLAG_CHECKED,
                GLXC.STATE_FLAG_DROP_ACTIVE
            ]
        )

    def test_Constants_ToolbarStyle(self):
        """Test Constants ToolbarStyle"""
        self.assertEqual(GLXC.TOOLBAR_ICONS, 'ICONS')
        self.assertEqual(GLXC.TOOLBAR_TEXT, 'TEXT')
        self.assertEqual(GLXC.TOOLBAR_BOTH, 'BOTH')
        self.assertEqual(GLXC.TOOLBAR_BOTH_HORIZ, 'BOTH_HORIZ')
        self.assertEqual(
            GLXC.ToolbarStyle,
            [
                GLXC.TOOLBAR_ICONS,
                GLXC.TOOLBAR_TEXT,
                GLXC.TOOLBAR_BOTH,
                GLXC.TOOLBAR_BOTH_HORIZ
            ]
        )

    def test_Constants_SortType(self):
        """Test Constants SortType"""
        self.assertEqual(GLXC.SORT_ASCENDING, 'ASCENDING')
        self.assertEqual(GLXC.SORT_DESCENDING, 'DESCENDING')
        self.assertEqual(
            GLXC.SortType,
            [
                GLXC.SORT_ASCENDING,
                GLXC.SORT_DESCENDING
            ]
        )
