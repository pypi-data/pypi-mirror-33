#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

import GLXCurses
import curses


class MenuBar(GLXCurses.Widget):
    def __init__(self):
        GLXCurses.Widget.__init__(self)
        self.glxc_type = 'GLXCurses.MenuBar'

        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.set_name(self.__class__.__name__)

        # Internal Widget Setting
        self.app_info_label = None

        self.sensitive = None

        # Make a Style heritage attribute
        if self.get_style().get_attribute_states():
            self.set_attribute_states(self.get_style().get_attribute_states())

    def draw_widget_in_area(self):
        """
        White the menubar to the screen, the location is imposed to top left corner
        """
        app_info_label = self.app_info_label

        drawing_area = self.get_screen().subwin(
            0,
            0,
            0,
            0
        )
        self.set_curses_subwin(drawing_area)

        if curses.has_colors():
            self.get_curses_subwin().addstr(
                    0,
                    0,
                    str(' ' * (self.get_width() - 1)),
                    self.get_style().get_color_pair(
                        foreground=self.get_style().get_color_text('dark', 'STATE_NORMAL'),
                        background=self.get_style().get_color_text('light', 'STATE_NORMAL')
                    )
                )
            self.get_curses_subwin().bkgdset(
                    ord(' '),
                    self.get_style().get_color_pair(
                        foreground=self.get_style().get_color_text('dark', 'STATE_NORMAL'),
                        background=self.get_style().get_color_text('light', 'STATE_NORMAL')
                    )
                )
        if self.app_info_label:
            if not self.get_height() + 1 <= len(app_info_label):
                try:
                    self.get_curses_subwin().addstr(
                        0,
                        (self.get_width() - 1) - len(str(app_info_label[:-1])),
                        app_info_label[:-1],
                        self.get_style().get_color_pair(
                            foreground=self.get_style().get_color_text('dark', 'STATE_NORMAL'),
                            background=self.get_style().get_color_text('light', 'STATE_NORMAL')
                        )
                    )
                    self.get_curses_subwin().insstr(
                        0,
                        self.get_width() - 1,
                        app_info_label[-1:],
                        self.get_style().get_color_pair(
                            foreground=self.get_style().get_color_text('dark', 'STATE_NORMAL'),
                            background=self.get_style().get_color_text('light', 'STATE_NORMAL')
                        )
                    )
                except curses.error:
                    pass
