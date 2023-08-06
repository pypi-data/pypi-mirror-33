#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

import GLXCurses


class ToolBar(GLXCurses.Widget):
    def __init__(self):
        GLXCurses.Widget.__init__(self)
        self.glxc_type = 'GLXCurses.ToolBar'

        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.set_name(self.__class__.__name__)

        # Widget setting
        if self.get_style().get_attribute_states():
            self.set_attribute_states(self.get_style().get_attribute_states())

            self.text_fg = self.get_style().get_attribute_states()['dark']['STATE_NORMAL']
            self.text_bg = self.get_style().get_attribute_states()['light']['STATE_NORMAL']
            self.text_prefix_fg = self.get_style().get_attribute_states()['text']['STATE_PRELIGHT']
            self.text_prefix_bg = self.get_style().get_attribute_states()['dark']['STATE_NORMAL']
            self.widget_fg = self.get_style().get_attribute_states()['dark']['STATE_NORMAL']
            self.widget_bg = self.get_style().get_attribute_states()['dark']['STATE_NORMAL']

            self.color_text_normal = self.get_style().get_color_pair(
                foreground=self.text_fg,
                background=self.text_bg
            )
            self.color_text_prefix = self.get_style().get_color_pair(
                foreground=self.text_prefix_fg,
                background=self.text_prefix_bg
            )
            self.color_normal = self.get_style().get_color_pair(
                foreground=self.widget_fg,
                background=self.widget_bg
            )
        else:
            self.color_text_normal = 0
            self.color_text_prefix = 0
            self.color_normal = 0

        self.max_button_number = 10
        self.button_list = [
            'Help',
            'Options',
            'View',
            'Modif',
            'Copy',
            'Move',
            'Mkdir',
            'Sup',
            'Menu',
            'Quit'
        ]

    def draw(self):
        item_list = self.button_list
        labels_end_coord = ['', '', '', '', '', '', '', '', '', '', '', '']
        screen_height, screen_width = self.get_screen().getmaxyx()

        drawing_area = self.get_screen().subwin(
            0,
            0,
            int(screen_height - 1),
            0
        )

        self.draw_in_area(drawing_area, item_list, labels_end_coord, screen_width)

    def draw_in_area(self, drawing_area, item_list, labels_end_coord, screen_width):
        self.set_curses_subwin(drawing_area)
        widget_height, widget_width = self.get_curses_subwin().getmaxyx()
        widget_width -= 1
        req_button_number = len(item_list) + 1
        pos = 0
        if widget_width < req_button_number * 7:
            for i in range(0, req_button_number):
                if pos + 7 <= widget_width:
                    pos += 7
                labels_end_coord[i] = pos
        else:
            dv = widget_width / req_button_number + 1
            md = widget_width % req_button_number + 1
            i = 0
            for i in range(0, int(req_button_number / 2)):
                pos += dv
                if req_button_number / 2 - 1 - i < md / 2:
                    pos += 1
                labels_end_coord[i] = pos
            for i in range(i + 1, req_button_number):
                pos += dv
                if req_button_number - 1 - i < (md + 1) / 2:
                    pos += 1
                labels_end_coord[i] = pos
        if req_button_number > self.max_button_number:
            req_button_number = self.max_button_number

        # Limit crash about display size, by reduce the number of button's it can be display
        max_can_be_display = 1
        for I in range(1, req_button_number + 1):
            cumul = 0
            for U in range(0, max_can_be_display):
                cumul += len(str(item_list[U]))
            if widget_width - 1 > cumul + int((3 * max_can_be_display) - 0):
                max_can_be_display += 1
                self.curses_subwin.addstr(
                    0,
                    0,
                    str(" " * int(widget_width)),
                    self.color_text_normal
                )
                self.curses_subwin.insstr(
                    0,
                    int(widget_width - 1),
                    str(' '),
                    self.color_text_normal
                )
                self.curses_subwin.addstr(
                    0,
                    0,
                    "",
                    self.color_text_normal
                )
        count = 0
        for num in range(0, max_can_be_display - 1):
            if count == 0:
                self.curses_subwin.addstr(
                    str('{0: >2}'.format(count + 1)),
                    self.color_text_prefix
                )
                self.curses_subwin.addstr(
                    str(item_list[count]),
                    self.color_text_normal
                )
            elif 0 <= count < max_can_be_display - 1:
                if screen_width - (labels_end_coord[count - 1] + 0) >= len(item_list[count]) + 3:
                    self.curses_subwin.addstr(
                        0,
                        int((labels_end_coord[count - 1] + 0)),
                        str(''),
                        self.color_text_normal
                    )
                    self.curses_subwin.addstr(
                        str('{0: >2}'.format(count + 1)),
                        self.color_text_prefix
                    )
                    self.curses_subwin.addstr(
                        str(item_list[count]),
                        self.color_text_normal
                    )
            elif count >= max_can_be_display - 1:
                if screen_width - (labels_end_coord[count - 1] + 1) >= len(item_list[count]) + 3:
                    self.curses_subwin.addstr(
                        0,
                        int(labels_end_coord[count - 1] + 1),
                        str('{0: >2}'.format(count + 1)),
                        self.color_text_prefix
                    )
                    self.curses_subwin.addstr(
                        str(item_list[count]),
                        self.color_text_normal
                    )
            count += 1
