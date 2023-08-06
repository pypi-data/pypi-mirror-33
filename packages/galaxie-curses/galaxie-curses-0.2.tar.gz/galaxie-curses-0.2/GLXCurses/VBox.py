#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import Box
from GLXCurses.Utils import clamp_to_zero
import curses


class VBox(Box):

    def check_resize(self):
        pass

    def __init__(self):
        # Load heritage
        Box.__init__(self)

        # It's a GLXCurse Type
        self.glxc_type = 'GLXCurses.VBox'

        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.set_name(self.__class__.__name__)

        # Make a Widget Style heritage attribute as local attribute
        if self.get_style().get_attribute_states():
            self.set_attribute_states(self.get_style().get_attribute_states())

        self.preferred_height = 2
        self.preferred_width = 2

    def new(self, homogeneous=True, spacing=None):
        """
        Creates a new GLXCurses :class:`VBox <GLXCurses.VBox.VBox>`

        :param homogeneous: True if all children are to be given equal space allotments.
        :type homogeneous: bool
        :param spacing: The number of characters to place by default between children.
        :type spacing: int
        :return: a new :class:`VBox <GLXCurses.VBox.VBox>`.
        :raise TypeError: if ``homogeneous`` is not bool type
        :raise TypeError: if ``spacing`` is not int type or None
        """
        if type(homogeneous) != bool:
            raise TypeError('"homogeneous" argument must be a bool type')
        if spacing is not None:
            if type(spacing) != int:
                raise TypeError('"spacing" must be int type or None')

        self.__init__()
        self.set_spacing(clamp_to_zero(spacing))
        self.set_homogeneous(homogeneous)
        return self

    # GLXC VBox Functions
    def draw_widget_in_area(self):

        # Check widgets to display
        is_large_enough = (self.get_width() > self.preferred_width)
        is_high_enough = (self.get_height() > self.preferred_height)
        curses_have_crash = False

        if is_high_enough and is_large_enough:
            if self.get_children():
                devised_box_size = int(self.get_height() / len(self.get_children()))
                total_vertical_spacing = 0
                for children in self.get_children():

                    # Check if that the first element
                    if children['properties']['position'] == 0:

                        pos_y = 0
                        pos_y += self.get_y()
                        pos_y += self.get_spacing()

                        pos_x = 0
                        pos_x += self.get_x()
                        pos_x += self.get_spacing()

                        try:
                            sub_win = self.get_curses_subwin().subwin(
                                devised_box_size - self.get_spacing(),
                                self.get_width() - self.get_spacing() * 2,
                                pos_y,
                                pos_x
                            )
                        except curses.error:
                            curses_have_crash = True

                        total_vertical_spacing += self.get_spacing()

                    # Check if that the last element
                    elif children['properties']['position'] == len(self.get_children()) - 1:
                        last_element_vertical_size = self.get_height()
                        last_element_vertical_size -= int(devised_box_size * children['properties']['position'])
                        last_element_vertical_size -= total_vertical_spacing

                        pos_y = 0
                        pos_y += self.get_y()
                        pos_y += int(devised_box_size * children['properties']['position'])
                        pos_y += int(self.get_spacing() / 2)

                        pos_x = 0
                        pos_x += self.get_x()
                        pos_x += self.get_spacing()

                        try:
                            sub_win = self.get_curses_subwin().subwin(
                                last_element_vertical_size,
                                self.get_width() - self.get_spacing() * 2,
                                pos_y,
                                pos_x
                            )
                        except curses.error:
                            curses_have_crash = True

                    # Normal
                    else:
                        pos_y = 0
                        pos_y += self.get_y()
                        pos_y += int(devised_box_size * children['properties']['position'])
                        pos_y += int(self.get_spacing() / 2)

                        pos_x = 0
                        pos_x += self.get_x()
                        pos_x += self.get_spacing()

                        try:
                            sub_win = self.get_curses_subwin().subwin(
                                devised_box_size - (self.get_spacing() / 2),
                                self.get_width() - self.get_spacing() * 2,
                                pos_y,
                                pos_x
                            )
                        except curses.error:
                            curses_have_crash = True

                        total_vertical_spacing += self.get_spacing() / 2

                    # Drawing
                    if not curses_have_crash:
                        children['widget'].set_curses_subwin(sub_win)
                    children['widget'].draw_widget_in_area()
