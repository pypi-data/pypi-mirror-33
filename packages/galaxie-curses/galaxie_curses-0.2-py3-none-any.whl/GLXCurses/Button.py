#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import Widget
from GLXCurses import Application
from GLXCurses import GLXC
from GLXCurses.Utils import clamp_to_zero
from GLXCurses.Utils import resize_text
import curses
import logging


class Button(Widget):

    def __init__(self):
        # Load heritage
        Widget.__init__(self)

        # It's a GLXCurse Type
        self.glxc_type = 'GLXCurses.Button'

        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.set_name(self.__class__.__name__)

        # Make a Widget Style heritage attribute as local attribute
        if self.get_style().get_attribute_states():
            self.set_attribute_states(self.get_style().get_attribute_states())

        # Internal Widget Setting
        self.text = None
        self._x_offset = 0
        self._y_offset = 0

        # Interface
        self.interface = '[  ]'
        self.interface_selected = '[<  >]'
        self.button_border = self.interface

        # Size management
        self._update_preferred_sizes()

        # Justification: LEFT, RIGHT, CENTER
        self._justify = GLXC.JUSTIFY_CENTER

        # PositionType: CENTER, TOP, BOTTOM
        self._position_type = GLXC.POS_CENTER

        # States
        self.curses_mouse_states = {
            curses.BUTTON1_PRESSED: 'BUTTON1_PRESS',
            curses.BUTTON1_RELEASED: 'BUTTON1_RELEASED',
            curses.BUTTON1_CLICKED: 'BUTTON1_CLICKED',
            curses.BUTTON1_DOUBLE_CLICKED: 'BUTTON1_DOUBLE_CLICKED',
            curses.BUTTON1_TRIPLE_CLICKED: 'BUTTON1_TRIPLE_CLICKED',

            curses.BUTTON2_PRESSED: 'BUTTON2_PRESSED',
            curses.BUTTON2_RELEASED: 'BUTTON2_RELEASED',
            curses.BUTTON2_CLICKED: 'BUTTON2_CLICKED',
            curses.BUTTON2_DOUBLE_CLICKED: 'BUTTON2_DOUBLE_CLICKED',
            curses.BUTTON2_TRIPLE_CLICKED: 'BUTTON2_TRIPLE_CLICKED',

            curses.BUTTON3_PRESSED: 'BUTTON3_PRESSED',
            curses.BUTTON3_RELEASED: 'BUTTON3_RELEASED',
            curses.BUTTON3_CLICKED: 'BUTTON3_CLICKED',
            curses.BUTTON3_DOUBLE_CLICKED: 'BUTTON3_DOUBLE_CLICKED',
            curses.BUTTON3_TRIPLE_CLICKED: 'BUTTON3_TRIPLE_CLICKED',

            curses.BUTTON4_PRESSED: 'BUTTON4_PRESSED',
            curses.BUTTON4_RELEASED: 'BUTTON4_RELEASED',
            curses.BUTTON4_CLICKED: 'BUTTON4_CLICKED',
            curses.BUTTON4_DOUBLE_CLICKED: 'BUTTON4_DOUBLE_CLICKED',
            curses.BUTTON4_TRIPLE_CLICKED: 'BUTTON4_TRIPLE_CLICKED',

            curses.BUTTON_SHIFT: 'BUTTON_SHIFT',
            curses.BUTTON_CTRL: 'BUTTON_CTRL',
            curses.BUTTON_ALT: 'BUTTON_ALT'
        }

        # Sensitive
        self.set_can_focus(1)
        self.set_can_default(1)
        self.set_sensitive(1)
        self.states_list = None

        # Subscription
        self.connect('MOUSE_EVENT', Button._handle_mouse_event)

    def draw_widget_in_area(self):

        # Many Thing's
        # Check if the text can be display
        text_have_necessary_width = (self.get_preferred_width() >= 1)
        text_have_necessary_height = (self.get_preferred_height() >= 1)
        if not text_have_necessary_height or not text_have_necessary_width:
            return

        if self.get_text():

            # Check if the text can be display
            text_have_necessary_width = (self.get_preferred_width() >= 1)
            text_have_necessary_height = (self.get_preferred_height() >= 1)
            if text_have_necessary_width and text_have_necessary_height:
                self._draw_button()

    # Internal Widget functions
    def set_text(self, text):
        self.text = text
        self.preferred_width = len(self.get_text())

    def get_text(self):
        return self.text

    # Justification: LEFT, RIGHT, CENTER
    def set_justify(self, justify):
        """
        Set the Justify of the Vertical separator

         Justify:
          - LEFT
          - CENTER
          - RIGHT

        :param justify: a Justify
        :type justify: str
        """
        if justify in [GLXC.JUSTIFY_LEFT, GLXC.JUSTIFY_CENTER, GLXC.JUSTIFY_RIGHT]:
            if self.get_justify() != str(justify).upper():
                self._justify = str(justify).upper()
                # When the justify is set update preferred sizes store in Widget class
                self._update_preferred_sizes()
        else:
            raise TypeError(u'PositionType must be LEFT or CENTER or RIGHT')

    def get_justify(self):
        """
        Return the Justify of the CheckButton

         Justify:
          - LEFT
          - CENTER
          - RIGHT

        :return: str
        """
        return self._justify

    # PositionType: CENTER, TOP, BOTTOM
    def set_position_type(self, position_type):
        """
        Set the Position type

        PositionType:
         .glxc.POS_TOP
         .glxc.POS_CENTER
         .glxc.POS_BOTTOM

        :param position_type: a PositionType
        :type position_type: str
        """
        if position_type in [GLXC.POS_TOP, GLXC.POS_CENTER, GLXC.POS_BOTTOM]:
            if self.get_position_type() != str(position_type).upper():
                self._position_type = str(position_type).upper()
                # When the position type is set update preferred sizes store in Widget class
                self._update_preferred_sizes()
        else:
            raise TypeError(u'PositionType must be CENTER or TOP or BOTTOM')

    def get_position_type(self):
        """
        Return the Position Type

        PositionType:
         .glxc.POS_TOP
         .glxc.POS_CENTER
         .glxc.POS_BOTTOM

        :return: str
        """
        return self._position_type

    # State
    def get_states(self):
        return self.states_list

    # Internal
    def _draw_button(self):
        self._check_selected()
        self._update_preferred_sizes()
        self._check_justify()
        self._check_position_type()

        if not self.get_sensitive():
            self._draw_the_good_button(
                color=self.get_style().get_color_pair(
                    foreground=self.get_style().get_color_text('bg', 'STATE_NORMAL'),
                    background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
                )
            )
        elif self.state['PRELIGHT']:
            self._draw_the_good_button(
                color=self.get_style().get_color_pair(
                    foreground=self.get_style().get_color_text('dark', 'STATE_NORMAL'),
                    background=self.get_style().get_color_text('bg', 'STATE_PRELIGHT')
                )
            )
        elif self.state['NORMAL']:
            self._draw_the_good_button(
                color=self.get_style().get_color_pair(
                    foreground=self.get_style().get_color_text('text', 'STATE_NORMAL'),
                    background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
                )
            )

    def _draw_the_good_button(self, color):
        try:
            # Interface management
            self.get_curses_subwin().addstr(
                self._y_offset,
                self._x_offset,
                self.button_border[:len(self.button_border) / 2],
                color
            )
        except curses.error:
            pass
        try:

            # Draw the Horizontal Button with Justification and PositionType
            message_to_display = resize_text(self.get_text(), self.get_width() - len(self.button_border), '~')
            self.get_curses_subwin().addstr(
                self._y_offset,
                self._x_offset + len(self.button_border) / 2,
                message_to_display,
                color
            )
        except curses.error:
            pass
        try:
            # Interface management
            message_to_display = resize_text(self.get_text(), self.get_width() - len(self.button_border), '~')
            self.get_curses_subwin().insstr(
                self._y_offset,
                self._x_offset + (len(self.button_border) / 2) + len(message_to_display),
                self.button_border[-len(self.button_border) / 2:],
                color
            )
        except curses.error:
            pass

    def _handle_mouse_event(self, event_signal, event_args):
        if self.get_sensitive():
            (mouse_event_id, x, y, z, event) = event_args
            # Be sure we select really the Button
            y -= self.y
            x -= self.x
            if self._get_y_offset() >= y > self._get_y_offset() - self.get_preferred_height():
                if (self._get_x_offset() - 1) + len(self.button_border) + len(self.get_text()) >= x > (self._get_x_offset() - 1):
                    # We are sure about the button have been clicked
                    self.states_list = '; '.join(state_string for state, state_string
                                                 in self.curses_mouse_states.viewitems()
                                                 if event & state)
                    # INTERNAL METHOD
                    # BUTTON1
                    if event == curses.BUTTON1_PRESSED:
                        Application().set_is_focus(self)
                        self._check_selected()
                        self._set_state_prelight(True)
                    elif event == curses.BUTTON1_RELEASED:
                        Application().set_is_focus(self)
                        self._check_selected()
                        self._set_state_prelight(False)
                    if event == curses.BUTTON1_CLICKED:
                        Application().set_is_focus(self)
                    if event == curses.BUTTON1_DOUBLE_CLICKED:
                        Application().set_is_focus(self)
                    if event == curses.BUTTON1_TRIPLE_CLICKED:
                        Application().set_is_focus(self)

                    # BUTTON2
                    if event == curses.BUTTON2_PRESSED:
                        Application().set_is_focus(self)
                        self._check_selected()
                        self._set_state_prelight(True)
                    elif event == curses.BUTTON2_RELEASED:
                        self._set_state_prelight(False)
                        Application().set_is_focus(self)
                    if event == curses.BUTTON2_CLICKED:
                        Application().set_is_focus(self)
                    if event == curses.BUTTON2_DOUBLE_CLICKED:
                        Application().set_is_focus(self)
                    if event == curses.BUTTON2_TRIPLE_CLICKED:
                        Application().set_is_focus(self)

                    # BUTTON3
                    if event == curses.BUTTON3_PRESSED:
                        Application().set_is_focus(self)
                        self._check_selected()
                        self._set_state_prelight(True)
                    elif event == curses.BUTTON3_RELEASED:
                        self._set_state_prelight(False)
                        Application().set_is_focus(self)
                    if event == curses.BUTTON3_CLICKED:
                        Application().set_is_focus(self)
                    if event == curses.BUTTON3_DOUBLE_CLICKED:
                        Application().set_is_focus(self)
                    if event == curses.BUTTON3_TRIPLE_CLICKED:
                        Application().set_is_focus(self)

                    # BUTTON4
                    if event == curses.BUTTON4_PRESSED:
                        Application().set_is_focus(self)
                        self._check_selected()
                        self._set_state_prelight(True)
                    elif event == curses.BUTTON4_RELEASED:
                        self._set_state_prelight(False)
                        Application().set_is_focus(self)
                    if event == curses.BUTTON4_CLICKED:
                        Application().set_is_focus(self)
                    if event == curses.BUTTON4_DOUBLE_CLICKED:
                        Application().set_is_focus(self)
                    if event == curses.BUTTON4_TRIPLE_CLICKED:
                        Application().set_is_focus(self)

                    if event == curses.BUTTON_SHIFT:
                        pass
                    if event == curses.BUTTON_CTRL:
                        pass
                    if event == curses.BUTTON_ALT:
                        pass

                    # Create a Dict with everything
                    instance = {
                        'class': self.__class__.__name__,
                        'label': self.get_text(),
                        'id': self.get_widget_id()
                    }
                    # EVENT EMIT
                    # Application().emit(self.curses_mouse_states[event], instance)
                    self.emit(self.curses_mouse_states[event], instance)
            else:
                # Nothing the better is to clean the prelight
                self._set_state_prelight(False)
        else:
            logging.debug(self.__class__.__name__ + ': ' + self.get_text() + ' ' + self.get_widget_id() + 'is not '
                                                                                                          'sensitive.')

    def _check_selected(self):
        if self.get_can_focus():
            if Application().get_is_focus()['id'] == self.get_widget_id():
                self.set_is_focus(True)
                self.button_border = self.interface_selected
                self._update_preferred_sizes()
            else:
                self.set_is_focus(False)
                self.button_border = self.interface
                self._update_preferred_sizes()
        else:
            pass

    def _set_state_prelight(self, value):
        if bool(value):
            self.state['PRELIGHT'] = True
        else:
            self.state['PRELIGHT'] = False

    def _get_state_prelight(self):
        return self.state['PRELIGHT']

    def _check_justify(self):
        """Check the justification of the X axe"""
        width = self.get_width()
        preferred_width = self.get_preferred_width()

        self._set_x_offset(0)
        if self.get_justify() == GLXC.JUSTIFY_CENTER:
            # Clamp value and impose the center
            if width is None:
                estimated_width = 0
            elif width <= 0:
                estimated_width = 0
            elif width == 1:
                estimated_width = 0
            else:
                estimated_width = int(width / 2)

            # Clamp value and impose the center
            if preferred_width is None:
                estimated_preferred_width = 0
            elif preferred_width <= 0:
                estimated_preferred_width = 0
            elif preferred_width == 1:
                estimated_preferred_width = 0
            else:
                estimated_preferred_width = int(preferred_width / 2)

            # Make the compute
            final_value = int(estimated_width - estimated_preferred_width)

            # clamp the result
            if final_value <= 0:
                final_value = 0

            # Finally set the value
            self._set_x_offset(final_value)

        elif self.get_justify() == GLXC.JUSTIFY_LEFT:

            # Finally set the value
            self._set_x_offset(0)

        elif self.get_justify() == GLXC.JUSTIFY_RIGHT:
            # Clamp estimated_width
            estimated_width = clamp_to_zero(width)

            # Clamp preferred_width
            estimated_preferred_width = clamp_to_zero(preferred_width)

            # Make the compute
            final_value = int(estimated_width - estimated_preferred_width )

            # clamp the result
            if final_value <= 0:
                final_value = 0

            # Finally set the value
            self._x_offset = final_value

    def _check_position_type(self):
        # PositionType: CENTER, TOP, BOTTOM
        height = self.get_height()
        preferred_height = self.get_preferred_height()

        if self.get_position_type() == GLXC.POS_CENTER:
            # Clamp height
            if height is None:
                estimated_height = 0
            elif height <= 0:
                estimated_height = 0
            elif height == 1:
                # prevent a 1/2 = float(0.5) case
                estimated_height = 0
            else:
                estimated_height = int(height / 2)

            # Clamp preferred_height
            if preferred_height is None:
                estimated_preferred_height = 0
            elif preferred_height <= 0:
                estimated_preferred_height = 0
            elif preferred_height == 1:
                # prevent a 1/2 = float(0.5) case
                estimated_preferred_height = 0
            else:
                estimated_preferred_height = int(preferred_height / 2)

            # Make teh compute
            final_value = int(estimated_height - estimated_preferred_height)

            # Clamp the result to a positive
            if final_value <= 0:
                final_value = 0

            self._set_y_offset(final_value)

        elif self.get_position_type() == GLXC.POS_TOP:
            self._set_y_offset(0)

        elif self.get_position_type() == GLXC.POS_BOTTOM:
            # Clamp height
            estimated_height = clamp_to_zero(height)

            # Clamp preferred_height
            estimated_preferred_height = clamp_to_zero(preferred_height)

            # Make the compute
            final_value = int(estimated_height - estimated_preferred_height)

            # Clamp the result to a positive
            if final_value <= 0:
                final_value = 0

            # Clamp height
            estimated_height = clamp_to_zero(height)

            # Clamp preferred_height
            estimated_preferred_height = clamp_to_zero(preferred_height)

            # Make the compute
            final_value = int(estimated_height - estimated_preferred_height)

            # Clamp the result to a positive
            if final_value <= 0:
                final_value = 0

            self._set_y_offset(final_value)

    def _update_preferred_sizes(self):
        self.set_preferred_width(self._get_estimated_preferred_width())
        self.set_preferred_height(self._get_estimated_preferred_height())

    def _get_estimated_preferred_width(self):
        """
        Estimate a preferred width, by consider X Location, allowed width

        :return: a estimated preferred width
        :rtype: int
        """
        if self.get_text():
            estimated_preferred_width = 0
            estimated_preferred_width += len(self.get_text())
            estimated_preferred_width += len(self.button_border)
        else:
            estimated_preferred_width = 0
            estimated_preferred_width += len(self.button_border)

        return estimated_preferred_width

    def _get_estimated_preferred_height(self):
        """
        Estimate a preferred height, by consider Y Location

        :return: a estimated preferred height
        :rtype: int
        """
        estimated_preferred_height = 1
        return estimated_preferred_height

    def _set_x_offset(self, value=None):
        """
        Set _x

        :param value: A value to set to _x attribute
        :type value: int or None
        :raise TypeError: when value is not int or None
        """
        if type(value) is None or type(value) == int:
            self._x_offset = value
        else:
            raise TypeError(u'>value< must be a int or None type')

    def _get_x_offset(self):
        """
        Return the x space add to text for justify computation

        :return: _label_x attribute
        """
        return self._x_offset

    def _set_y_offset(self, value=None):
        """
        Set _y

        :param value: A value to set to _y attribute
        :type value: int or None
        :raise TypeError: when value is not int or None
        """
        if type(value) is None or type(value) == int:
            self._y_offset = value
        else:
            raise TypeError(u'>y< must be a int or None type')

    def _get_y_offset(self):
        """
        Return the _y space add to text for position computation

        :return: y attribute
        """
        return self._y_offset

    # Unimplemented
    def _enter(self):
        raise NotImplementedError

    def _leave(self):
        raise NotImplementedError

    def _key_pressed(self, char):
        if char > 255:
            return 0  # skip control-characters
        # if chr(char).upper() == self.LabelButton[self.Underline]:
        #     return 1
        else:
            return 0
