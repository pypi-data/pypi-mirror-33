#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from random import randint
import random
import string
import sys
import os
from GLXCurses.Utils import new_id

from GLXCurses.Utils import glxc_type

# Require when you haven't GLXBob as default Package
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

import GLXCurses


# Unittest
class TestApplication(unittest.TestCase):
    def setUp(self):
        # Before the test start
        self.application = GLXCurses.Application()
        self.win_to_test = self.application.get_screen().subwin(
            0,
            0,
            0,
            0
        )
        self.toolbar = None
        self.messagebar = None
        self.statusbar = None
        self.menubar = None
        self.window = None

    def tearDown(self):
        # When the test is finish
        self.application.close()

    def test_set_get_parent(self):
        """Test Application.set_parent() and Application.get_parent()"""
        # Call the method without argument
        self.application.set_parent()
        # Check if None argument is accept
        self.application.set_parent(None)

        # call .draw method for start all computation of subwindow
        self.application.draw()
        # Now get_parent() shouldn't None return
        self.assertNotEqual(self.application.get_parent(), None)
        # We check the return is a curses object window
        self.assertEqual(type(self.application.get_parent()), type(self.win_to_test))

        # Try to erase the parent
        self.application.set_parent(None)
        # It must be ignore
        self.assertNotEqual(self.application.get_parent(), None)
        # It must continue to return a curses window object
        self.assertEqual(type(self.application.get_parent()), type(self.win_to_test))

        # Must be the same
        self.assertEqual(self.application.get_curses_subwin(), self.application.get_parent())

    def test_get_parent_size(self):
        """Test Application.get_parent_size"""
        # call .draw method for start all computation of subwindow
        self.application.draw()
        # We check the return is a curses object window
        self.assertEqual(type(self.application.get_parent()), type(self.win_to_test))
        # check return type tuple
        self.assertEqual(type(self.application.get_parent_size()), type(tuple()))
        # check the len of the tuple
        self.assertEqual(len(self.application.get_parent_size()), 2)
        # check if both element are a a int type
        self.assertEqual(type(self.application.get_parent_size()[0]), type(int()))
        self.assertEqual(type(self.application.get_parent_size()[1]), type(int()))

        # Must be the same
        self.assertEqual(self.application.get_size(), self.application.get_parent_size())

    def test_get_parent_origin(self):
        """Test Application.get_parent_size"""
        # call .draw method for start all computation of subwindow
        self.application.draw()
        # We check the return is a curses object window
        self.assertEqual(type(self.application.get_parent()), type(self.win_to_test))
        # check return type tuple
        self.assertEqual(type(self.application.get_parent_origin()), type(tuple()))
        # check the len of the tuple
        self.assertEqual(len(self.application.get_parent_origin()), 2)
        # check if both element are a a int type
        self.assertEqual(type(self.application.get_parent_origin()[0]), type(int()))
        self.assertEqual(type(self.application.get_parent_origin()[1]), type(int()))

        # Must be the same
        self.assertEqual(self.application.get_parent_origin(), self.application.get_origin())

    def test_get_parent_spacing(self):
        """Test Application.get_parent_spacing()"""
        # call .draw method for start all computation of subwindow
        self.application.draw()
        # We check the return is a curses object window
        self.assertEqual(type(self.application.get_parent()), type(self.win_to_test))
        # check return type int
        self.assertEqual(type(self.application.get_parent_spacing()), type(int()))

        self.application.set_spacing(2)
        self.assertEqual(self.application.get_parent_spacing(), 2)
        self.application.set_spacing()
        self.assertEqual(self.application.get_parent_spacing(), 0)

        # Must be the same
        self.assertEqual(self.application.get_parent_spacing(), self.application.get_spacing())

    def test_get_parent_style(self):
        """Test Application.get_parent_style()"""
        # The Application Style must be the same ast the parent one, because Application have no parent
        self.assertEqual(self.application.get_parent_style(), self.application.get_style())
        # Check it's a valid GLXCurses.Style object type
        self.assertTrue(glxc_type(self.application.get_parent_style()))

        # Must be the same
        self.assertEqual(self.application.get_parent_style(), self.application.get_style())

    def test_get_curses_subwin(self):
        """Test Application.get_curses_subwin()"""
        # call .draw method for start all computation of subwindow
        self.application.draw()

        # We check the return is a curses object window
        self.assertEqual(type(self.application.get_curses_subwin()), type(self.win_to_test))

    def test_get_origin(self):
        """Test Application.get_origin()"""
        # call .draw method for start all computation of subwindow
        self.application.draw()
        # We check the return is a curses object window
        self.assertEqual(type(self.application.get_curses_subwin()), type(self.win_to_test))
        # check return type tuple
        self.assertEqual(type(self.application.get_origin()), type(tuple()))
        # check the len of the tuple
        self.assertEqual(len(self.application.get_origin()), 2)
        # check if both element are a a int type
        self.assertEqual(type(self.application.get_origin()[0]), type(int()))
        self.assertEqual(type(self.application.get_origin()[1]), type(int()))

    def test_set_get_spacing(self):
        """Test Application.set_spacing() and Application.get_spacing()"""
        # Set spacing to None
        self.application.set_spacing()
        # set spacing to
        self.application.set_spacing(5)
        # test the raise TypeError
        self.assertRaises(TypeError, self.application.set_spacing, str('galaxie'))
        # check if we cat get back the set value
        self.assertEqual(self.application.get_spacing(), 5)
        # back to normal
        self.application.set_spacing()

    def test_set_get_decorated(self):
        """Test Application.set_decorated() and Application.get_decorated()"""
        # call set_decorated() without argument
        self.application.set_decorated()
        # call set_decorated() with 0 as argument
        self.assertEqual(self.application.get_decorated(), 0)
        # verify we go back 0
        self.assertEqual(self.application.get_decorated(), 0)
        # call set_decorated() with 1 as argument
        self.application.set_decorated(1)
        # verify we go back 0
        self.assertEqual(self.application.get_decorated(), 1)
        # test raise TypeError
        self.assertRaises(TypeError, self.application.set_decorated, 'Galaxie')

    def test_set_get_screen(self):
        """Test Application.set_screen() and Application.get_screen()"""
        # call .draw method for start all computation of subwindow
        self.application.draw()
        # We check the return is a curses object window
        self.assertEqual(type(self.application.get_screen()), type(self.win_to_test))
        # Must do nothing
        self.application.set_screen('lilo')
        # Must do nothing
        self.application.set_screen('lulu')

    # Test Size management
    # width
    def test_get_set_width(self):
        """Test Application.set_width() and Application.get_width()"""
        value_random_1 = int(randint(8, 250))
        self.application.set_width(value_random_1)
        self.assertEqual(self.application.get_width(), value_random_1)
        # Test Raise
        self.assertRaises(TypeError, self.application.set_width, float(randint(1, 250)))

    # height
    def test_get_set_height(self):
        """Test Application.set_height() and Application.get_height()"""
        value_random_1 = int(randint(8, 250))
        self.application.set_height(value_random_1)
        self.assertEqual(self.application.get_height(), value_random_1)
        # Test Raise
        self.assertRaises(TypeError, self.application.set_height, float(randint(1, 250)))

    # preferred_height
    def test_get_set_preferred_height(self):
        """Test Application.set_preferred_height() and Application.get_preferred_height() method's """
        value_random_1 = int(randint(8, 250))
        self.application.set_preferred_height(value_random_1)
        self.assertEqual(self.application.get_preferred_height(), value_random_1)
        # Test Raise
        self.assertRaises(TypeError, self.application.set_preferred_height, float(randint(1, 250)))

    # preferred_width
    def test_get_set_preferred_width(self):
        """Test Application.set_preferred_width() and Application.get_preferred_width() method's """
        value_random_1 = int(randint(8, 250))
        self.application.set_preferred_width(value_random_1)
        self.assertEqual(self.application.get_preferred_width(), value_random_1)
        # Test Raise
        self.assertRaises(TypeError, self.application.set_preferred_width, float(randint(1, 250)))

    def test_get_set_preferred_size(self):
        """Test Application.set_preferred_size() and Test Application.get_preferred_size()"""
        value_random_1 = int(randint(8, 250))
        value_random_2 = int(randint(8, 250))
        self.application.set_preferred_size(x=value_random_1, y=value_random_2)
        self.assertEqual(self.application.get_preferred_size(), [value_random_1, value_random_2])
        # Test Raise
        self.assertRaises(TypeError, self.application.set_preferred_size, float(randint(1, 250)))

    def test_get_size(self):
        """Test Application.get_size()"""
        # call .draw method for start all computation of subwindow
        self.application.draw()
        # We check the return is a curses object window
        self.assertEqual(type(self.application.get_curses_subwin()), type(self.win_to_test))
        # check return type tuple
        self.assertEqual(type(self.application.get_size()), type(tuple()))
        # check the len of the tuple
        self.assertEqual(len(self.application.get_size()), 2)
        # check if both element are a a int type
        self.assertEqual(type(self.application.get_size()[0]), type(int()))
        self.assertEqual(type(self.application.get_size()[1]), type(int()))

    def test_set_get_x(self):
        """Test Application.set_y() and  Application.get_y()"""
        self.application.set_x(1)
        self.assertEqual(self.application.get_x(), 1)
        self.application.set_x(2)
        self.assertEqual(self.application.get_x(), 2)

    def test_set_get_y(self):
        """Test Application.set_y() and  Application.get_y()"""
        self.application.set_y(1)
        self.assertEqual(self.application.get_y(), 1)
        self.application.set_y(2)
        self.assertEqual(self.application.get_y(), 2)

    def test_set_get_name(self):
        """Test Application.set_name() and Application.get_name()"""
        try:
            # Python 2.7
            value_random_1 = u''.join(random.sample(string.letters, 52))
        except AttributeError:
            # Python 3
            value_random_1 = u''.join(random.sample(string.ascii_letters, 52))

        self.application.set_name(value_random_1)
        self.assertEqual(self.application.get_name(), value_random_1)

    def test_set_name_max_size(self):
        """Test Application.set_name() maximum size"""
        string_val = "x" * 300
        # Try to set name with the to long string
        self.assertRaises(ValueError, self.application.set_name, string_val)

    def test_set_name_type(self):
        """Test Application.set_name() maximum size"""
        self.assertRaises(TypeError, self.application.set_name, int(randint(1, 42)))

    def test_set_get_style(self):
        """Test Application.set_style()"""
        style = GLXCurses.Style()

        self.application.set_style(style)
        self.assertEqual(style, self.application.get_style())

    def test_set_style_raise(self):
        """Test Application.set_style() raise TypeError"""
        self.assertRaises(TypeError, self.application.set_style, int())

    def test_add_window(self):
        """Test Application.add_window()"""
        # create a new window
        self.window = GLXCurses.Window()

        # check if window parent is not self.application
        self.assertNotEqual(self.window.get_parent(), self.application)

        # check the size of the children windows list before add a window
        windows_list_size_before = len(self.application._get_windows_list())

        # add a window to the application
        self.application.add_window(self.window)

        # check the size of the children windows list after add a window
        windows_list_size_after = len(self.application._get_windows_list())

        # we must have one more children on the list
        self.assertGreater(windows_list_size_after, windows_list_size_before)

        # we get the last windows children element
        the_last_children_on_list = self.application._get_windows_list()[-1]

        # the last list element must contain the same reference to our window
        self.assertEqual(the_last_children_on_list['widget'], self.window)

        # check if the application is the parent of our window
        self.assertEqual(self.window.get_parent(), self.application)

        # test raise
        self.assertRaises(TypeError, self.application.add_window, int())

    def test_remove_window(self):
        """Test Application.remove_window()"""
        # create a new window
        self.window1 = GLXCurses.Window()
        self.window2 = GLXCurses.Window()

        # add a window to the application
        self.application.add_window(self.window1)

        # add a second window to the application
        self.application.add_window(self.window2)

        # the last list element must contain the same reference to our window
        self.assertEqual(self.application.get_active_window(), self.window2)

        self.application.remove_window(self.window2)

        # we get again the last windows children element
        self.assertEqual(self.application.get_active_window(), self.window1)

    def test_refresh(self):
        """Test Application.refresh() method """
        self.application.refresh()

    def test_draw(self):
        """Test Application.draw() method """
        self.application.draw()

    # def test_getch(self):
    #     """Test Application.getch() method"""
    #     pass

    def test_close(self):
        """Test Application.close() method """
        self.application.close()

    def test_set_get_default(self):
        """Test Application.set_default() and Application.get_default()"""
        self.window = GLXCurses.Window()
        # nothing happen
        self.application.set_default()
        # focus get_default return None
        self.assertEqual(self.application.get_default(), {
                'widget': None,
                'type': None,
                'id': None
            })
        # set_is_focus to the window
        self.application.set_default(self.window)
        # check if the window have the default
        self.assertEqual(self.application.get_default()['id'], self.window.get_widget_id())
        # Test None
        self.application.set_default(None)
        # focus get_default return None
        self.assertEqual(self.application.get_default(), {
                'widget': None,
                'type': None,
                'id': None
            })

    # focus
    def test_set_get_is_focus(self):
        """Test Application.set_is_focus() and Application.get_is_focus()"""
        self.window = GLXCurses.Window()
        # nothing happen
        self.application.set_is_focus()
        # focus get_is_focus return None
        self.assertEqual(self.application.get_is_focus(), {
                'widget': None,
                'type': None,
                'id': None
            })
        # set_is_focus to the window
        self.application.set_is_focus(self.window)
        # check if the window have the focus
        self.assertEqual(self.application.get_is_focus()['id'], self.window.get_widget_id())
        # Test None
        self.application.set_is_focus(None)
        # focus get_is_focus return None
        self.assertEqual(self.application.get_is_focus(), {
                'widget': None,
                'type': None,
                'id': None
            })

    def test_set_get_tooltip(self):
        """Test Application.set_tooltip() and Application.get_tooltip()"""
        self.window = GLXCurses.Window()
        # nothing happen
        self.application.set_tooltip()
        # focus get_tooltip return None
        self.assertEqual(self.application.get_tooltip(), {
                'widget': None,
                'type': None,
                'id': None
            })
        # set_tooltip to the window
        self.application.set_tooltip(self.window)
        # check if the window have the focus
        self.assertEqual(self.application.get_tooltip()['id'], self.window.get_widget_id())
        # Test None
        self.application.set_tooltip(None)
        # focus get_tooltip return None
        self.assertEqual(self.application.get_tooltip(), {
                'widget': None,
                'type': None,
                'id': None
            })

    # Test Internal methode
    def test__set__get_windows_list(self):
        """Test Application children windows list"""
        # List creation
        tested_list = [1, 2, 3]

        # flush teh children windows list with our list
        self.application._set_windows_list(tested_list)

        # list must be equal
        self.assertEqual(self.application._get_windows_list(), tested_list)

        # check if worng type is detected
        self.assertRaises(TypeError, self.application._set_windows_list, int())

        # Let the Application children list to None
        self.application._set_windows_list(list())

    def test__add_child_to_windows_list(self):
        """Test Application child add to the children windows list"""
        # create a new window
        self.window = GLXCurses.Window()

        # check the size of the children windows list before add a window
        windows_list_size_before = len(self.application._get_windows_list())

        # add a window to the children window list
        self.application._add_child_to_windows_list(self.window)

        # check the size of the children windows list after add a window
        windows_list_size_after = len(self.application._get_windows_list())

        # we must have one more children on the list
        self.assertGreater(windows_list_size_after, windows_list_size_before)

        # let list of children empty
        self.application._set_windows_list(list())

    def test__set_get_active_window_id(self):
        """Test Application._set_active_window_id() and Application._get_active_window_id()"""
        value1 = new_id()
        value2 = new_id()
        self.application._set_active_window_id(value1)
        self.assertEqual(self.application._get_active_window_id(), value1)
        self.assertNotEqual(self.application._get_active_window_id(), value2)

    def test__set__get_active_window_id_raise(self):
        """Test Application._set_active_window_id() TypeError"""
        self.assertRaises(TypeError, self.application._set_active_window_id, float())

    def test__set__get_active_window(self):
        """Test Application displayed Window"""
        # let list of children empty
        self.application._set_windows_list(list())

        # create a new window
        self.window = GLXCurses.Window()

        # add a window
        self.application.add_window(self.window)

        # _get_displayed_window() must return the last added window
        self.assertEqual(self.application.get_active_window(), self.window)

    def test_everything_menubar(self):
        """Test Application MenuBar"""
        # Create a MenuBar
        self.menubar = GLXCurses.MenuBar()
        # Default MenuBar value be None
        self.application._set_menubar(None)
        self.assertEqual(self.application._get_menubar(), None)
        # Add the MenuBar to application and set Parent
        self.application.add_menubar(self.menubar)
        # Test the set menu bar
        self.application._set_menubar(self.menubar)
        # check if we have the same menubar
        self.assertEqual(self.application._get_menubar(), self.menubar)
        # Test to remove the Menubar
        self.application.remove_menubar()
        # check if the menubar have been remove
        self.assertEqual(self.application._get_menubar(), None)
        # Check Type error
        self.assertRaises(TypeError, self.application._set_menubar, int())
        self.assertRaises(TypeError, self.application.add_menubar, int())

    def test_everything_statusbar(self):
        """Test Application StatusBar"""
        # Create a StatusBar
        self.statusbar = GLXCurses.StatusBar()
        # Default StatusBar value be None
        self.application._set_statusbar(None)
        self.assertEqual(self.application._get_statusbar(), None)
        # Add the StatusBar to application and set ot parent
        self.application.add_statusbar(self.statusbar)
        # Test the set status bar with internal method
        self.application._set_statusbar(self.statusbar)
        # check if we have the same statusbar
        self.assertEqual(self.application._get_statusbar(), self.statusbar)
        # Test to remove the StatusBar
        self.application.remove_statusbar()
        # check if the status bar have been removed
        self.assertEqual(self.application._get_statusbar(), None)
        # Check Type error
        self.assertRaises(TypeError, self.application._set_statusbar, int())
        self.assertRaises(TypeError, self.application.add_statusbar, int())

    def test_everything_messagebar(self):
        """Test Application MessageBar"""
        # Create a MessageBar
        self.messagebar = GLXCurses.MessageBar()
        # Default MessageBar value be None
        self.application._set_messagebar(None)
        self.assertEqual(self.application._get_messagebar(), None)
        # Add the MessageBar to application and set ot parent
        self.application.add_messagebar(self.messagebar)
        # Test the set MessageBar with internal method
        self.application._set_messagebar(self.messagebar)
        # check if we have the same MessageBar
        self.assertEqual(self.application._get_messagebar(), self.messagebar)
        # Test to remove the MessageBar
        self.application.remove_messagebar()
        # check if the MessageBar have been removed
        self.assertEqual(self.application._get_messagebar(), None)
        # Check Type error
        self.assertRaises(TypeError, self.application._set_messagebar, int())
        self.assertRaises(TypeError, self.application.add_messagebar, int())

    def test_everything_toolbar(self):
        """Test Application ToolBar"""
        # Create a StatusBar
        self.toolbar = GLXCurses.ToolBar()
        # Default ToolBar value be None
        self.application._set_toolbar(None)
        self.assertEqual(self.application._get_toolbar(), None)
        # Add the ToolBar to application and set ot parent
        self.application.add_toolbar(self.toolbar)
        # Test the set ToolBar with internal method
        self.application._set_toolbar(self.toolbar)
        # check if we have the same ToolBar
        self.assertEqual(self.application._get_toolbar(), self.toolbar)
        # Test to remove the ToolBar
        self.application.remove_toolbar()
        # check if the ToolBar have been removed
        self.assertEqual(self.application._get_toolbar(), None)
        # Check Type error
        self.assertRaises(TypeError, self.application._set_toolbar, int())
        self.assertRaises(TypeError, self.application.add_toolbar, int())

    def test_everything(self):
        """Test Application"""
        # Create a StatusBar
        self.menubar = GLXCurses.MenuBar()
        self.window = GLXCurses.Window()
        self.messagebar = GLXCurses.MessageBar()
        self.statusbar = GLXCurses.StatusBar()
        self.toolbar = GLXCurses.ToolBar()

        # Add the ToolBar to application and set ot parent
        self.application.add_menubar(self.menubar)
        self.application.add_window(self.window)
        self.application.add_messagebar(self.messagebar)
        self.application.add_statusbar(self.statusbar)
        self.application.add_toolbar(self.toolbar)
        # check if we have the same ToolBar

        # self.menubar.draw()
        # self.window.draw()
        # self.messagebar.draw()
        # self.statusbar.draw()
        # self.toolbar.draw()
