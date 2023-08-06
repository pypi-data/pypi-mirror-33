#!/usr/bin/env python
# -*- coding: utf-8 -*-
from GLXCurses import Box
from GLXCurses.Utils import clamp_to_zero
import curses

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved


class HBox(Box):
    """
    :Description:

    The :class:`HBox <GLXCurses.HBox.HBox>` is a container that organizes child widgets into a single row.

    Use the :class:`Box <GLXCurses.Box.Box>`  packing interface to determine the arrangement, spacing, width,
    and alignment of :class:`HBox <GLXCurses.HBox.HBox>` children.

    All children are allocated the same height.
    """

    def check_resize(self):
        pass

    def __init__(self):
        """
        :Attributes Details:

        .. py:attribute:: homogeneous

           TRUE if all children are to be given equal space allotments.

              +---------------+-------------------------------+
              | Type          | :py:data:`bool`               |
              +---------------+-------------------------------+
              | Flags         | Read / Write                  |
              +---------------+-------------------------------+
              | Default value | TRUE                          |
              +---------------+-------------------------------+

        .. py:attribute:: spacing

           The number of char to place by default between children.

              +---------------+-------------------------------+
              | Type          | :py:data:`int`                |
              +---------------+-------------------------------+
              | Flags         | Read / Write                  |
              +---------------+-------------------------------+
              | Default value | 0                             |
              +---------------+-------------------------------+
        """
        # Load heritage
        Box.__init__(self)

        # It's a GLXCurse Type
        self.glxc_type = 'GLXCurses.HBox'

        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.set_name(self.__class__.__name__)

        # Make a Widget Style heritage attribute as local attribute
        if self.get_style().get_attribute_states():
            self.set_attribute_states(self.get_style().get_attribute_states())

        self.preferred_height = 2
        self.preferred_width = 2

        # Default Value
        self.set_spacing(clamp_to_zero(0))
        self.set_homogeneous(False)

    def new(self, homogeneous=True, spacing=None):
        """
        Creates a new GLXCurses :class:`HBox <GLXCurses.HBox.HBox>`

        :param homogeneous: True if all children are to be given equal space allotments.
        :type homogeneous: bool
        :param spacing: The number of characters to place by default between children.
        :type spacing: int
        :return: a new :class:`HBox <GLXCurses.HBox.HBox>`.
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

    # GLXC HBox Functions called by GLXCurse.Widget.draw()
    def draw_widget_in_area(self):

        # Check widgets to display
        is_large_enough = (self.get_width() > self.preferred_width)
        is_high_enough = (self.get_height() > self.preferred_height)

        if is_high_enough and is_large_enough:
            if self.get_children():
                if self.get_homogeneous():
                    self._draw_homogeneous()
                else:
                    self._draw_not_homogeneous()

    def _draw_not_homogeneous(self):
        devised_box_size = int(self.get_width() / len(self.get_children()))
        total_horizontal_spacing = 0

        for children in self.get_children():

            # Check if that the first element
            if children['properties']['position'] == 0:
                sub_win = self.get_curses_subwin().subwin(
                    self.get_height() - self.get_spacing() * 2,
                    devised_box_size - self.get_spacing(),
                    self.get_y() + self.get_spacing(),
                    self.get_x() + self.get_spacing()
                )
                total_horizontal_spacing += self.get_spacing()
            # Check if that the last element
            elif children['properties']['position'] == len(self.get_children()) - 1:
                last_element_horizontal_size = self.get_width()
                last_element_horizontal_size -= (devised_box_size * children['properties']['position'])
                last_element_horizontal_size -= total_horizontal_spacing
                last_element_horizontal_size -= self.get_spacing()
                try:
                    sub_win = self.get_curses_subwin().subwin(
                        self.get_height() - self.get_spacing() * 2,
                        last_element_horizontal_size,
                        self.get_y() + self.get_spacing(),
                        self.get_x() + (devised_box_size * children['properties']['position']) + (self.get_spacing() / 2)
                    )
                except curses.error:
                    pass
            # Normal
            else:
                sub_win = self.get_curses_subwin().subwin(
                    self.get_height() - self.get_spacing() * 2,
                    devised_box_size - (self.get_spacing() / 2),
                    self.get_y() + self.get_spacing(),
                    self.get_x() + (devised_box_size * children['properties']['position']) + (self.get_spacing() / 2)
                )
                total_horizontal_spacing += self.get_spacing() / 2

            # Drawing
            children['widget'].set_curses_subwin(sub_win)
            children['widget'].draw_widget_in_area()

    def _draw_homogeneous(self):
        devised_box_size = int(self.get_width() / len(self.get_children()) - 1)
        total_horizontal_spacing = 0
        for children in self.get_children():

            # Check if that the first element
            if children['properties']['position'] == 0:
                # position compute
                pos_y = self.get_y() + self.get_spacing()
                pos_x = self.get_x() + self.get_spacing()
                try:
                    sub_win = self.get_curses_subwin().subwin(
                        self.get_height() - self.get_spacing() * 2,
                        devised_box_size - self.get_spacing(),
                        pos_y,
                        pos_x
                    )
                    total_horizontal_spacing += self.get_spacing()
                except curses.error:
                    pass

            # Check if that the last element
            elif children['properties']['position'] == len(self.get_children()) - 1:
                # Check if that the last element
                last_element_horizontal_size = self.get_width()
                last_element_horizontal_size -= int(devised_box_size * children['properties']['position'])
                last_element_horizontal_size -= total_horizontal_spacing
                last_element_horizontal_size -= self.get_spacing()
                # position compute
                pos_y = self.get_y() + self.get_spacing()
                pos_x = self.get_x()
                pos_x += int(devised_box_size * children['properties']['position'])
                pos_x += int(self.get_spacing() / 2)
                try:
                    sub_win = self.get_curses_subwin().subwin(
                        self.get_height() - self.get_spacing() * 2,
                        last_element_horizontal_size,
                        pos_y,
                        pos_x
                    )
                except curses.error:
                    pass
            else:
                # position compute
                pos_y = self.get_y() + self.get_spacing()
                pos_x = self.get_x()
                pos_x += int(devised_box_size * children['properties']['position'])
                pos_x += int(self.get_spacing() / 2)
                try:
                    sub_win = self.get_curses_subwin().subwin(
                        self.get_height() - self.get_spacing() * 2,
                        devised_box_size - (self.get_spacing() / 2),
                        pos_y,
                        pos_x
                    )
                    total_horizontal_spacing += self.get_spacing() / 2
                except curses.error:
                    pass

            # Drawing
            try:
                children['widget'].set_curses_subwin(sub_win)
                children['widget'].draw_widget_in_area()
            except UnboundLocalError:
                pass
