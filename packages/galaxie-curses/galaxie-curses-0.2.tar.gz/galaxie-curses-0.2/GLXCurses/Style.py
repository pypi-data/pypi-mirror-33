#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

import curses


class Style(object):
    """
    :Description:

    Galaxie Curses Style is equivalent to a skin feature, the entire API receive a common Style from Application
    and each individual Widget can use it own separate one.

    Yet it's a bit hard to explain how create you own Style, in summary it consist to a dict() it have keys
    with a special name call ``Attribute``, inside that dictionary we create a second level of dict() dedicated
    to store color value of each ``States``
    """
    def __init__(self):
        """
        :GLXCurses Style Attributes Type:

         +-------------+---------------------------------------------------------------------------------------------+
         | ``text_fg`` | An color to be used for the foreground colors in each curses_subwin state.                  |
         +-------------+---------------------------------------------------------------------------------------------+
         | ``bg``      | An color to be used for the background colors in each curses_subwin state.                  |
         +-------------+---------------------------------------------------------------------------------------------+
         | ``light``   | An color to be used for the light colors in each curses_subwin state.                       |
         +-------------+---------------------------------------------------------------------------------------------+
         | ``dark``    | An color to be used for the dark colors in each curses_subwin state.                        |
         +-------------+---------------------------------------------------------------------------------------------+
         | ``mid``     | An color to be used for the mid colors (between light and dark) in each curses_subwin state |
         +-------------+---------------------------------------------------------------------------------------------+
         | ``text``    | An color to be used for the text colors in each curses_subwin state.                        |
         +-------------+---------------------------------------------------------------------------------------------+
         | ``base``    | An color to be used for the base colors in each curses_subwin state.                        |
         +-------------+---------------------------------------------------------------------------------------------+
         | ``black``   | Used for the black color.                                                                   |
         +-------------+---------------------------------------------------------------------------------------------+
         | ``white``   | Used for the white color.                                                                   |
         +-------------+---------------------------------------------------------------------------------------------+

        :GLXCurses States Type:

         +------------------------+----------------------------------------------------------------+
         | ``STATE_NORMAL``       | The state during normal operation                              |
         +------------------------+----------------------------------------------------------------+
         | ``STATE_ACTIVE``       | The curses_subwin is currently active, such as a button pushed |
         +------------------------+----------------------------------------------------------------+
         | ``STATE_PRELIGHT``     | The mouse pointer is over the curses_subwin                    |
         +------------------------+----------------------------------------------------------------+
         | ``STATE_SELECTED``     | The curses_subwin is selected                                  |
         +------------------------+----------------------------------------------------------------+
         | ``STATE_INSENSITIVE``  | The curses_subwin is disabled                                  |
         +------------------------+----------------------------------------------------------------+

        """
        self.glxc_type = 'GLXCurses.Style'

        # Internal storage
        self._allowed_fg_colors = list()
        self._allowed_bg_colors = list()
        self._text_pairs = list()

        # Internal init
        self._gen_curses_colors_pairs()

        # init
        self.attribute_states = self.get_default_attribute_states()

    @staticmethod
    def get_default_attribute_states():
        """
        Return a default style, that will be use by the entire GLXCurses API via the ``attribute_states`` object. \
        every Widget's  will receive it style by default.

        :return: A Galaxie Curses Style dictionary
        :rtype: dict
        """
        attribute_states = dict()

        # An color to be used for the foreground colors in each curses_subwin state.
        attribute_states['text_fg'] = dict()
        attribute_states['text_fg']['STATE_NORMAL'] = 'WHITE'
        attribute_states['text_fg']['STATE_ACTIVE'] = 'WHITE'
        attribute_states['text_fg']['STATE_PRELIGHT'] = 'WHITE'
        attribute_states['text_fg']['STATE_SELECTED'] = 'WHITE'
        attribute_states['text_fg']['STATE_INSENSITIVE'] = 'WHITE'

        # An color to be used for the background colors in each curses_subwin state.
        attribute_states['bg'] = dict()
        attribute_states['bg']['STATE_NORMAL'] = 'BLUE'
        attribute_states['bg']['STATE_ACTIVE'] = 'BLUE'
        attribute_states['bg']['STATE_PRELIGHT'] = 'CYAN'
        attribute_states['bg']['STATE_SELECTED'] = 'CYAN'
        attribute_states['bg']['STATE_INSENSITIVE'] = 'BLUE'

        # An color to be used for the light colors in each curses_subwin state.
        # The light colors are slightly lighter than the bg colors and used for creating shadows.
        attribute_states['light'] = dict()
        attribute_states['light']['STATE_NORMAL'] = 'CYAN'
        attribute_states['light']['STATE_ACTIVE'] = 'WHITE'
        attribute_states['light']['STATE_PRELIGHT'] = 'WHITE'
        attribute_states['light']['STATE_SELECTED'] = 'WHITE'
        attribute_states['light']['STATE_INSENSITIVE'] = 'WHITE'

        # An color to be used for the dark colors in each curses_subwin state.
        # The dark colors are slightly darker than the bg colors and used for creating shadows.
        attribute_states['dark'] = dict()
        attribute_states['dark']['STATE_NORMAL'] = 'BLACK'
        attribute_states['dark']['STATE_ACTIVE'] = 'BLACK'
        attribute_states['dark']['STATE_PRELIGHT'] = 'BLACK'
        attribute_states['dark']['STATE_SELECTED'] = 'BLACK'
        attribute_states['dark']['STATE_INSENSITIVE'] = 'BLACK'

        # An color to be used for the mid colors (between light and dark) in each curses_subwin state
        attribute_states['mid'] = dict()
        attribute_states['mid']['STATE_NORMAL'] = 'YELLOW'
        attribute_states['mid']['STATE_ACTIVE'] = 'WHITE'
        attribute_states['mid']['STATE_PRELIGHT'] = 'WHITE'
        attribute_states['mid']['STATE_SELECTED'] = 'WHITE'
        attribute_states['mid']['STATE_INSENSITIVE'] = 'WHITE'

        # An color to be used for the text colors in each curses_subwin state.
        attribute_states['text'] = dict()
        attribute_states['text']['STATE_NORMAL'] = 'GRAY'
        attribute_states['text']['STATE_ACTIVE'] = 'WHITE'
        attribute_states['text']['STATE_PRELIGHT'] = 'WHITE'
        attribute_states['text']['STATE_SELECTED'] = 'WHITE'
        attribute_states['text']['STATE_INSENSITIVE'] = 'WHITE'

        # An color to be used for the base colors in each curses_subwin state.
        attribute_states['base'] = dict()
        attribute_states['base']['STATE_NORMAL'] = 'WHITE'
        attribute_states['base']['STATE_ACTIVE'] = 'WHITE'
        attribute_states['base']['STATE_PRELIGHT'] = 'WHITE'
        attribute_states['base']['STATE_SELECTED'] = 'WHITE'
        attribute_states['base']['STATE_INSENSITIVE'] = 'WHITE'

        # Used for the black color.
        attribute_states['black'] = dict()
        attribute_states['black']['STATE_NORMAL'] = 'BLACK'
        attribute_states['black']['STATE_ACTIVE'] = 'BLACK'
        attribute_states['black']['STATE_PRELIGHT'] = 'BLACK'
        attribute_states['black']['STATE_SELECTED'] = 'BLACK'
        attribute_states['black']['STATE_INSENSITIVE'] = 'BLACK'

        # Used for the white color.
        attribute_states['white'] = dict()
        attribute_states['white']['STATE_NORMAL'] = 'WHITE'
        attribute_states['white']['STATE_ACTIVE'] = 'WHITE'
        attribute_states['white']['STATE_PRELIGHT'] = 'WHITE'
        attribute_states['white']['STATE_SELECTED'] = 'WHITE'
        attribute_states['white']['STATE_INSENSITIVE'] = 'WHITE'

        return attribute_states

    def get_color_pair(self, foreground='WHITE', background='BLACK'):
        """
        Return a curses color pairs correspondent with the right foreground and background.
        All possible foreground/background combination have been generate automatically during GLXC.Style init.

        :param foreground: Foreground  color like 'WHITE'
        :param background: Background color like 'BLACK'
        :return: Curse color pair it correspond to the right foreground and background
        :rtype: int
        """
        special_color = [
            'YELLOW',
            'ORANGE',
            'PINK',
            'RED',
            'WHITE',
            'GRAY'
        ]
        color_need_bold = [
            'YELLOW',
            'PINK',
            'WHITE'
        ]

        # all special color will be estimate here
        if str(foreground).upper() in special_color:
            if str(foreground).upper() in color_need_bold:
                pairs = self._get_text_pairs().index(
                    str(foreground).upper() + '/' + str(background).upper()
                )

                return curses.color_pair(pairs) | curses.A_BOLD

            else:
                if str(foreground).upper() == 'GRAY':
                    pairs = self._get_text_pairs().index(
                        'WHITE' + '/' + str(background).upper()
                    )
                else:
                    pairs = self._get_text_pairs().index(
                        str(foreground).upper() + '/' + str(background).upper()
                    )
                return curses.color_pair(pairs)

        # native color here
        else:
            pairs = self._get_text_pairs().index(
                str(foreground).upper() + '/' + str(background).upper()
            )
            return curses.color_pair(pairs)

    def get_color_text(self, attribute='base', state='STATE_NORMAL'):
        """
        Return a text color, for a attribute and a state passed as argument, it's use by widget for know which color
        use, when a state change.

        By example: When color change if the button is pressed

        :param attribute: accepted value: text_fg        :return: , bg, light, dark, mid, text, base, black, white
        :param state: accepted value: STATE_NORMAL, STATE_ACTIVE, STATE_PRELIGHT, STATE_SELECTED, STATE_INSENSITIVE
        :return: text color
        :rtype: str
        """
        return self.get_attribute_states()[attribute][state]

    def set_attribute_states(self, attribute_states):
        """
        Set the ``attribute_states`` attribute, it consist to a dictionary it store a second level of dictionary \
        with keys if have special name.

        see: get_default_attribute_states() for generate a default Style.

        :param attribute_states: a Dictionary with Galaxie Curses Style format
        :type attribute_states: dict(dict(str()))
        """
        # Try to found a way to not be execute
        # Check first level dictionary
        if type(attribute_states) != dict:
            raise TypeError('"attribute_states" is not a dictionary')

        # For each key's
        for attribute in ['text_fg', 'bg', 'light', 'dark', 'mid', 'text', 'base', 'black', 'white']:
            # Check if the key value is a dictionary
            try:
                if type(attribute_states[attribute]) != dict:
                    raise TypeError('"attribute_states" key is not a dict')
            except KeyError:
                raise KeyError('"attribute_states" is not a Galaxie Curses Style')
            # For each key value, in that case a sub dictionary
            for state in ['STATE_NORMAL', 'STATE_ACTIVE', 'STATE_PRELIGHT', 'STATE_SELECTED', 'STATE_INSENSITIVE']:
                # Check if the key value is a string
                try:
                    if type(attribute_states[attribute][state]) != str:
                        raise TypeError('"attribute_states" key is not a str')
                except KeyError:
                    raise KeyError('"attribute_states" is not a Galaxie Curses Style')

        # If it haven't quit that ok
        if attribute_states != self.get_attribute_states():
            self.attribute_states = attribute_states

    def get_attribute_states(self):
        """
        Return the ``attribute_states`` attribute, it consist to a dictionary it store a second level of dictionary \
        with keys if have special name.

        :return: attribute states dictionary on Galaxie Curses Style format
        :rtype: dict
        """
        return self.attribute_states

    # Internal
    def _get_allowed_fg_colors(self):
        """
        Internal method for return ``_allowed_fg_colors`` attribute

        :return the _allowed_fg_colors attribute
        :rtype: list
        """
        return self._allowed_fg_colors

    def _set_allowed_fg_colors(self, allowed_fg_colors=list()):
        """
        Internal method for set ``_curses_colors`` attribute

        :param allowed_fg_colors: A list of color name
        :type allowed_fg_colors: list
        :raise TypeError: if ``allowed_fg_colors`` parameter is not a :py:data:`list` type
        """
        if type(allowed_fg_colors) != list:
            raise TypeError('"allowed_fg_colors" argument must be a list type')
        if allowed_fg_colors != self._get_allowed_fg_colors():
            self._allowed_fg_colors = allowed_fg_colors
            # Can emit modification signal here

    def _gen_allowed_fg_colors(self):
        """
        Internal it generate color list name of supported color by Galaxie Curses, the method work directly with \
        other internal method's and have no parameter or return.

        That list will be use as source for generate a color pair.
        """

        # Start by clean the list
        self._set_allowed_fg_colors(list())

        # Append allowed colors
        self._get_allowed_fg_colors().append('BLACK')
        self._get_allowed_fg_colors().append('RED')
        self._get_allowed_fg_colors().append('GREEN')
        self._get_allowed_fg_colors().append('YELLOW')
        self._get_allowed_fg_colors().append('WHITE')
        self._get_allowed_fg_colors().append('BLUE')
        self._get_allowed_fg_colors().append('MAGENTA')
        self._get_allowed_fg_colors().append('CYAN')
        # no more color, curse not permit it

    def _get_allowed_bg_colors(self):
        """
        Internal method for return ``_allowed_bg_colors`` attribute

        :return the _allowed_bg_colors attribute
        :rtype: list
        """
        return self._allowed_bg_colors

    def _set_allowed_bg_colors(self, allowed_bg_colors=list()):
        """
        Internal method for set ``_curses_colors`` attribute

        :param allowed_bg_colors: A list of color name
        :type allowed_bg_colors: list
        :raise TypeError: if ``allowed_bg_colors`` parameter is not a :py:data:`list` type
        """
        if type(allowed_bg_colors) != list:
            raise TypeError('"allowed_bg_colors" argument must be a list type')

        if allowed_bg_colors != self._get_allowed_bg_colors():
            self._allowed_bg_colors = allowed_bg_colors
            # Can emit modification signal here

    def _gen_allowed_bg_colors(self):
        """
        Internal it generate color list name of supported color by Galaxie Curses, the method work directly with \
        other internal method's and have no parameter or return.

        That list will be use as source for generate a color pair.
        """

        # Start by clean the list
        self._set_allowed_bg_colors(list())

        # Append allowed colors
        self._get_allowed_bg_colors().append('BLACK')
        self._get_allowed_bg_colors().append('RED')
        self._get_allowed_bg_colors().append('GREEN')
        self._get_allowed_bg_colors().append('YELLOW')
        self._get_allowed_bg_colors().append('WHITE')
        self._get_allowed_bg_colors().append('BLUE')
        self._get_allowed_bg_colors().append('MAGENTA')
        self._get_allowed_bg_colors().append('CYAN')
        # no more color, curse not permit it

    def _set_text_pairs(self, text_pairs):
        """
        Internal method for set ``_text_pairs`` attribute with a list

        :param text_pairs: A list of color name
        :type text_pairs: list
        :raise TypeError: if ``text_pairs`` parameter is not a :py:data:`list` type
        """
        if type(text_pairs) == list:
            if text_pairs != self._text_pairs:
                self._text_pairs = text_pairs
                # Can emit modification signal here
        else:
            raise TypeError(u'>text_pairs< argument must be a list type')

    def _get_text_pairs(self):
        """
        Internal method for return ``_text_pairs`` attribute

        :return _text_pairs list ex: ['WHITE/BLACK', 'WHITE/RED']
        :rtype: list
        """
        return self._text_pairs

    def _gen_curses_colors_pairs(self):
        """
        Internal it generate color list pair name of supported color by Galaxie Curses, the method work directly with \
        other internal method's and have no parameter or return.

        That list index number match with the curses colors pair number.
        """
        self._gen_allowed_fg_colors()
        self._gen_allowed_bg_colors()

        # Start by clean the list
        self._set_text_pairs(list())

        # The first color pair is WHITE/BLACK for no color support
        self._get_text_pairs().append('WHITE' + '/' + 'BLACK')
        curses.init_pair(
            0,
            curses.COLOR_WHITE,
            curses.COLOR_BLACK
        )

        # Init a counter it start to 1 and not 0
        counter = 1
        fg = None
        bg = None

        for background in self._get_allowed_bg_colors():
            if str(background).upper() == 'BLACK':
                bg = curses.COLOR_BLACK
            elif str(background).upper() == 'WHITE':
                bg = curses.COLOR_WHITE
            elif str(background).upper() == 'BLUE':
                bg = curses.COLOR_BLUE
            elif str(background).upper() == 'RED':
                bg = curses.COLOR_RED
            elif str(background).upper() == 'MAGENTA':
                bg = curses.COLOR_MAGENTA
            elif str(background).upper() == 'CYAN':
                bg = curses.COLOR_CYAN
            elif str(background).upper() == 'GREEN':
                bg = curses.COLOR_GREEN
            elif str(background).upper() == 'YELLOW':
                bg = curses.COLOR_YELLOW

            # For each foreground colors
            for foreground in self._get_allowed_fg_colors():
                # And each background colors
                if str(foreground).upper() == 'BLACK':
                    fg = curses.COLOR_BLACK
                elif str(foreground).upper() == 'WHITE':
                    fg = curses.COLOR_WHITE
                elif str(foreground).upper() == 'BLUE':
                    fg = curses.COLOR_BLUE
                elif str(foreground).upper() == 'RED':
                    fg = curses.COLOR_RED
                elif str(foreground).upper() == 'MAGENTA':
                    fg = curses.COLOR_MAGENTA
                elif str(foreground).upper() == 'CYAN':
                    fg = curses.COLOR_CYAN
                elif str(foreground).upper() == 'GREEN':
                    fg = curses.COLOR_GREEN
                elif str(foreground).upper() == 'YELLOW':
                    fg = curses.COLOR_YELLOW

                # Curses pair provisioning it have a index it match with the _get_text_pairs list index
                # Generate a colors pair like 'WHITE/RED'.

                # if color is inside allowed color list
                if foreground in self._get_allowed_fg_colors() and background in self._get_allowed_bg_colors():
                    # if the text_pair is not all ready inside the pairs list.
                    if str(foreground).upper() + '/' + str(background).upper() not in self._get_text_pairs():
                        # the text pair to the list where counter and index MUST match.
                        self._get_text_pairs().append(
                            str(foreground).upper() + '/' + str(background).upper()
                        )
                        curses.init_pair(
                            counter,
                            fg,
                            bg
                        )
                        counter += 1


