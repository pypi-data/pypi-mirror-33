#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

import GLXCurses
from GLXCurses import GLXC
import curses
import logging


def resize_text(text, max_width, separator='~'):
    if max_width < len(text):
        text_to_return = text[:(max_width / 2) - 1] + separator + text[-max_width / 2:]
        if len(text_to_return) == 1:
            text_to_return = text[:1]
        elif len(text_to_return) == 2:
            text_to_return = str(text[:1] + text[-1:])
        elif len(text_to_return) == 3:
            text_to_return = str(text[:1] + separator + text[-1:])
        return text_to_return
    else:
        return text


class ProgressBar(GLXCurses.Widget):
    def __init__(self):
        # Load heritage
        GLXCurses.Widget.__init__(self)

        # It's a GLXCurse Type
        self.glxc_type = 'GLXCurses.ProgressBar'

        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.set_name(self.__class__.__name__)

        # Make a Widget Style heritage attribute as local attribute
        if self.get_style().get_attribute_states():
            self.set_attribute_states(self.get_style().get_attribute_states())

        # The Percent value
        self.value = 0

        # Internal Widget Setting
        # Justification: LEFT, RIGHT, CENTER
        self.justification = GLXC.JUSTIFY_CENTER

        # Orientation: HORIZONTAL, VERTICAL
        self.orientation = GLXC.ORIENTATION_HORIZONTAL

        # PositionType: CENTER, TOP, BOTTOM
        self.position_type = 'CENTER'

        # Progress bars normally grow from top to bottom or left to right.
        # Inverted progress bars grow in the opposite direction
        self.inverted = 0

        # Label
        self.text = ''
        self.show_text = None
        # Interface
        self.progressbar_border = '[]'
        self.progressbar_vertical_border = '__'

        if self.orientation == 'HORIZONTAL':
            # WIDTH
            self.preferred_width = 0
            self.preferred_width += len(self.progressbar_border)
            # HEIGHT
            self.preferred_height = 1
        elif self.orientation == 'VERTICAL':
            # WIDTH
            self.preferred_width = 1
            # HEIGHT
            self.preferred_height = 0
            self.preferred_height += len(self.progressbar_border)

        self.char = ' '

    def draw_widget_in_area(self):
        # Orientation: HORIZONTAL, VERTICAL
        if self.get_orientation() == 'HORIZONTAL':
            self.draw_horizontal()

        elif self.get_orientation() == 'VERTICAL':
            self.draw_vertical()

    def draw_vertical(self):
        y_progress = 0

        # Check Justification
        x_progress = self.check_vertical_justification()
        if self.get_show_text():
            # PositionType: CENTER, TOP, BOTTOM
            progress_text = self.check_vertical_position_type()

        # Draw Vertical ProgressBar
        # Draw first interface_unactive Character
        self.get_curses_subwin().addch(
            y_progress,
            x_progress,
            curses.ACS_HLINE,
            self.get_style().get_color_pair(
                foreground=self.get_style().get_color_text('base', 'STATE_NORMAL'),
                background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
            )
        )
        # Draw the Vertical ProgressBar with Justification and PositionType
        if self.get_inverted():
            try:
                # Draw Background
                progress_text = progress_text[::-1]
                increment = 0
                for CHAR in progress_text:
                    self.get_curses_subwin().addch(
                        self.get_height() - 2 - increment,
                        x_progress,
                        CHAR,
                        self.get_style().get_color_pair(
                            foreground=self.get_style().get_color_text('base', 'STATE_NORMAL'),
                            background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
                        )
                    )
                    increment += 1

                count = 0
                for CHAR in progress_text[:int((self.get_height() - self.get_preferred_height()) * self.value / 100)]:
                    self.get_curses_subwin().addch(
                        self.get_height() - 2 - count,
                        x_progress,
                        CHAR,
                        self.get_style().get_color_pair(
                            foreground=self.get_style().get_color_text('bg', 'STATE_NORMAL'),
                            background=self.get_style().get_color_text('base', 'STATE_NORMAL')
                        )
                    )
                    count += 1

                # Draw last interface_unactive Character
                self.get_curses_subwin().insch(
                    self.get_height() - 1,
                    x_progress,
                    curses.ACS_HLINE,
                    self.get_style().get_color_pair(
                        foreground=self.get_style().get_color_text('base', 'STATE_NORMAL'),
                        background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
                    )
                )
            except curses.error:
                pass
        else:
            try:
                # Draw the Vertical ProgressBar with Justification and PositionType
                count = 1
                for CHAR in progress_text:
                    self.get_curses_subwin().addstr(
                        y_progress + count,
                        x_progress,
                        CHAR,
                        self.get_style().get_color_pair(
                            foreground=self.get_style().get_color_text('base', 'STATE_NORMAL'),
                            background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
                        )
                    )
                    count += 1

                # Redraw with color inverted but apply percent calculation
                count = 1
                for CHAR in progress_text[:int((self.get_height() - self.get_preferred_height()) * self.value / 100)]:
                    self.get_curses_subwin().addstr(
                        y_progress + count,
                        x_progress,
                        CHAR,
                        self.get_style().get_color_pair(
                            foreground=self.get_style().get_color_text('bg', 'STATE_NORMAL'),
                            background=self.get_style().get_color_text('base', 'STATE_NORMAL')
                        )
                    )
                    count += 1

                # Draw last interface_unactive Character
                self.get_curses_subwin().insch(
                    self.get_height()  - 1,
                    x_progress,
                    curses.ACS_HLINE,
                    self.get_style().get_color_pair(
                        foreground=self.get_style().get_color_text('base', 'STATE_NORMAL'),
                        background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
                    )
                )
            except curses.error:
                pass

    def check_vertical_justification(self):
        x_progress = 0
        if self.get_justify() == 'CENTER':
            x_progress = self.get_width() / 2
        elif self.get_justify() == 'LEFT':
            x_progress = 0
        elif self.get_justify() == 'RIGHT':
            x_progress = self.get_width() - (len(self.progressbar_border) / 2)

        return x_progress

    def check_vertical_position_type(self):
        progress_height = self.get_height()
        progress_height -= len(self.progressbar_border)
        progress_text = str(self.char * progress_height)
        tmp_string = ''
        if self.get_position_type().upper() == 'CENTER':
            if progress_height - (len(self.progressbar_border) / 2) > len(self.text):
                tmp_string += progress_text[:(len(progress_text) / 2) - len(self.text) / 2]
                tmp_string += self.text
                tmp_string += progress_text[-(len(progress_text) - len(tmp_string)):]
            elif progress_height - (len(self.progressbar_border) / 2) >= self.get_preferred_height():
                tmp_string += self.text
            else:
                tmp_string += progress_text[:progress_height]
            progress_text = tmp_string

        elif self.get_position_type().upper() == 'TOP':
            if progress_height - (len(self.progressbar_border) / 2) >= len(self.text):
                tmp_string += self.text
                tmp_string += progress_text[-(len(progress_text) - len(self.text)):]
            elif progress_height - (len(self.progressbar_border) / 2) >= self.get_preferred_height():
                tmp_string += self.text
            else:
                tmp_string += progress_text[:progress_height]
            progress_text = tmp_string

        elif self.get_position_type().upper() == 'BOTTOM':
            if progress_height - (len(self.progressbar_border) / 2) >= len(self.text):
                tmp_string += progress_text[:(len(progress_text) - len(self.text))]
                tmp_string += self.text
            elif progress_height - (len(self.progressbar_border) / 2) >= self.get_preferred_height():
                tmp_string += self.text
            else:
                tmp_string += progress_text[:progress_height]
            progress_text = tmp_string

        return progress_text

    def draw_horizontal(self):

        x_progress = len(self.progressbar_border) / 2

        progress_text = self.check_horizontal_justification()

        # PositionType: CENTER, TOP, BOTTOM
        y_progress, y_text = self.check_horizontal_position_type()

        # DRAWING

        # Justify the text to center of a string it have small len as the progress bar
        try:
            # First Pass when we draw everything in Normal color
            self.get_curses_subwin().addstr(
                y_text,
                x_progress - 1,
                self.progressbar_border[:len(self.progressbar_border) / 2],
                self.get_style().get_color_pair(
                    foreground=self.get_style().get_color_text('base', 'STATE_NORMAL'),
                    background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
                )
            )
            # Draw the progressbar1 background
            # Draw Left to Right Horizontal Progress Bar
            if self.get_inverted():
                progress_text = progress_text[::-1]
                increment = 0
                for CHAR in progress_text:
                    self.get_curses_subwin().addstr(
                        y_progress,
                        self.get_width() - 2 - increment,
                        CHAR,
                        self.get_style().get_color_pair(
                            foreground=self.get_style().get_color_text('base', 'STATE_NORMAL'),
                            background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
                        )
                    )
                    increment += 1
                increment = 0
                for CHAR in progress_text[:int((self.get_width() - self.get_preferred_width()) * self.get_value() / 100)]:
                    self.get_curses_subwin().addstr(
                        y_progress,
                        self.get_width() - 2 - increment,
                        CHAR,
                        self.get_style().get_color_pair(
                            foreground=self.get_style().get_color_text('bg', 'STATE_NORMAL'),
                            background=self.get_style().get_color_text('base', 'STATE_NORMAL')
                        )
                    )
                    increment += 1
        except curses.error:
            pass

        else:
            try:
                increment = 0
                for CHAR in progress_text:
                    self.get_curses_subwin().addstr(
                        y_progress,
                        x_progress + increment,
                        CHAR,
                        self.get_style().get_color_pair(
                            foreground=self.get_style().get_color_text('base', 'STATE_NORMAL'),
                            background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
                        )
                    )
                    increment += 1
                increment = 0
                for CHAR in progress_text[:int((self.get_width() - self.get_preferred_width()) * self.get_value() / 100)]:
                    self.get_curses_subwin().addstr(
                        y_progress,
                        x_progress + increment,
                        CHAR,
                        self.get_style().get_color_pair(
                            foreground=self.get_style().get_color_text('bg', 'STATE_NORMAL'),
                            background=self.get_style().get_color_text('base', 'STATE_NORMAL')
                        )
                    )
                    increment += 1
            except curses.error:
                pass

        # Interface management
        self.get_curses_subwin().insstr(
            y_progress,
            self.get_width() - 1,
            self.progressbar_border[-len(self.progressbar_border) / 2:],
            self.get_style().get_color_pair(
                foreground=self.get_style().get_color_text('base', 'STATE_NORMAL'),
                background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
            )
        )

    def check_horizontal_justification(self):
        progress_width = self.get_width()
        progress_width -= len(self.progressbar_border)
        progress_text = str(self.char * progress_width)
        # Justification:
        tmp_string = ''
        if self.get_show_text():
            if self.get_justify() == 'CENTER':
                tmp_string += progress_text[:(len(progress_text) / 2) - len(self.get_text()) / 2]
                tmp_string += self.get_text()
                tmp_string += progress_text[-(len(progress_text) - len(tmp_string)):]
                progress_text = tmp_string

            elif self.get_justify() == 'LEFT':
                tmp_string += self.get_text()
                tmp_string += progress_text[-(len(progress_text) - len(self.get_text())):]
                progress_text = tmp_string

            elif self.get_justify() == 'RIGHT':
                tmp_string += progress_text[:(len(progress_text) - len(self.get_text()))]
                tmp_string += self.get_text()
                progress_text = tmp_string

        return progress_text

    def check_horizontal_position_type(self):
        y_text = 0
        y_progress = 0
        position_type = self.get_position_type()
        if position_type == 'CENTER':
            if (self.get_height() / 2) > self.get_preferred_height():
                y_text = (self.get_height() / 2) - self.get_preferred_height()
                y_progress = (self.get_height() / 2) - self.get_preferred_height()
            else:
                y_text = 0
                y_progress = 0

        elif position_type == 'TOP':
            y_text = 0
            y_progress = 0

        elif position_type == 'BOTTOM':
            y_text = self.get_height() - self.get_preferred_height()
            y_progress = self.get_height() - self.get_preferred_height()

        return y_progress, y_text

    # Internal curses_subwin functions
    def set_text(self, text):
        self.text = text
        self._update_preferred_size()

    def get_text(self):
        return self.text

    def set_value(self, percent=0):
        if 0 > percent:
            self.value = 0
        elif percent > 100:
            self.value = 100
        else:
            self.value = percent

        self._update_preferred_size()

    def get_value(self):
        return self.value

    def set_show_text(self, show_text_int):
        self.show_text = show_text_int

    def get_show_text(self):
        return self.show_text

    # Justification: LEFT, RIGHT, CENTER
    def set_justify(self, justification):
        self.justification = str(justification).upper()
        self._update_preferred_size()

    def get_justify(self):
        return self.justification

    # Orientation: HORIZONTAL, VERTICAL
    def set_orientation(self, orientation):
        self.orientation = str(orientation).upper()
        self._update_preferred_size()

    def get_orientation(self):
        return self.orientation

    # PositionType: CENTER, TOP, BOTTOM
    def set_position_type(self, position_type):
        self.position_type = str(position_type).upper()
        self._update_preferred_size()

    def get_position_type(self):
        return self.position_type

    # Progress bars normally grow from top to bottom or left to right.
    # Inverted progress bars grow in the opposite direction
    def set_inverted(self, boolean=0):
        if boolean >= 0:
            self.inverted = boolean
        else:
            self.inverted = 0

    def get_inverted(self):
        if self.inverted < 0:
            self.inverted = 0
        return self.inverted

    # Internal
    def _update_preferred_size(self):
        if self.get_orientation() == 'HORIZONTAL':
            # WIDTH
            self.preferred_width = 0
            self.preferred_width += len(self.progressbar_border)
            self.preferred_width += len(self.get_text())
            # HEIGHT
            self.preferred_height = 1
        elif self.get_orientation() == 'VERTICAL':
            # WIDTH
            self.preferred_width = 1
            # HEIGHT
            self.preferred_height = 0
            self.preferred_height += len(self.progressbar_border)
            self.preferred_height += len(self.get_text())

