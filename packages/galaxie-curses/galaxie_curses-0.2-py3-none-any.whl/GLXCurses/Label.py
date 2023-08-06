#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

import curses
import textwrap
import GLXCurses
from GLXCurses import GLXC


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


class Label(GLXCurses.Misc):
    def __init__(self):
        # Load heritage
        GLXCurses.Misc.__init__(self)

        # It's a GLXCurse Type
        self.glxc_type = 'GLXCurses.Label'

        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.set_name(self.__class__.__name__)

        # Make a Widget Style heritage attribute as local attribute
        if self.get_style().get_attribute_states():
            self.set_attribute_states(self.get_style().get_attribute_states())

        # Label Properties
        # The current position of the insertion cursor in chars. Allowed values: >= 0. Default value: 0
        self.cursor_position = 0

        # justify
        # The alignment of the lines in the text of the label relative to each other.
        # The possible values are:
        # glxc.JUSTIFY_LEFT,
        # glxc.JUSTIFY_RIGHT,
        # glxc.JUSTIFY_CENTER,
        # glxc.JUSTIFY_FILL.
        # This does NOT affect the alignment of the label within its allocation.
        # Default value: glxc.JUSTIFY_LEFT
        self.justify = GLXC.JUSTIFY_LEFT

        # The text of the label.
        # Default value: None
        self.label = None

        # The desired maximum width of the label, in characters.
        # If this property is set to -1, the width will be calculated automatically,
        # otherwise the label will request space for no more than the requested number of characters.
        # If the "width_chars" property is set to a positive value, then the "max_width_chars" property is ignored.
        # Allowed values: >= -1.
        # Default value: -1
        self.max_width_chars = -1

        # The mnemonic accelerator key for this label.
        # Default value: 16777215
        self.mnemonic_keyval = 16777215

        # The widget to be activated when the label's mnemonic key is pressed.
        self.mnemonic_widget = None

        # A string with _ characters in positions used to identify to characters in the text to underline.
        # Default value: None
        self.pattern = '_'

        # If True, the label text can be selected with the mouse.
        # Default value: False
        self.selectable = False

        # The position of the opposite end of the selection from the cursor in chars.
        # Allowed values: >= 0.
        # Default value: 0.
        self.selection_bound = 0

        # If True the label is in single line mode.
        # In single line mode, the height of the label does not depend on the actual text,
        # it is always set to ascent + descent of the font. This can be an advantage
        # in situations where resizing the label because of text changes would be distracting, e.g. in a statusbar.
        # Default value: False
        self.single_line_mode = False

        # If True the label tracks which links have been clicked.
        # It will then apply the "visited-link-color" color, instead of "link-color". False
        self.track_visited_links = False

        # If True, an underscore in the text indicates the next character should be used
        # for the mnemonic accelerator key.
        # Default value: False
        self.use_underline = False

        # The desired width of the label, in characters.
        # If this property is set to -1, the width will be calculated automatically,
        # otherwise the label will request either 3 characters or the property value, whichever is greater.
        # Allowed values: >= -1.
        # Default value: -1.
        self.width_chars = -1

        # If True, wrap lines if the text becomes too wide.
        # Default value: False
        self.wrap = False

        # If line wrapping is on, this controls how the line wrapping is done.
        # The default is glxc.WRAP_WORD, which means wrap on word boundaries.
        self.wrap_mode = GLXC.WRAP_WORD

        self.text_x = 0
        self.text_y = 0
        
        # Size management
        self.set_preferred_height(1)
        self.update_preferred_sizes()

    ###########
    # Methods #
    ###########
    # The set_text() method sets the text within the Label widget.
    # It replaces any text that was there before and will clear any previously set mnemonic accelerators.
    def set_text(self, text):
        self.label = text
        self.update_preferred_sizes()

    # The get_text() method fetches the text from a label widget, as displayed on the screen.
    # This does not include any markup or embedded underscore characters indicating mnemonics. (See get_label()).
    def get_text(self):
        return self.label

    # The set_label() method sets the text of the label.
    # The label is parsed for embedded underscores and markup depending on
    # the values of the "use-underline" and "use-markup" properties.
    def set_label(self, text):
        self.label = text
        self.update_preferred_sizes()

    # The get_label() method returns the text from a label widget including any markup
    # and embedded underscores indicating mnemonics. (See get_text() that just returns the text).
    def get_label(self):
        return self.label

    # set_markup
    # set_use_markup
    # get_use_markup

    # The set_use_underline() method sets the "use-underline" property to the value of setting.
    # If setting is True,
    # an underscore in the text indicates the next character should be used for the mnemonic accelerator key.
    def set_use_underline(self, setting):
        if bool(setting):
            self.use_underline = True
        else:
            self.use_underline = False

    # The get_use_underline() method returns the value of the "use-underline" property.
    # If True an embedded underscore in the label indicates the next character is a mnemonic. See set_use_underline().
    def get_use_underline(self):
        return bool(self.use_underline)

    # set_markup_with_mnemonic

    # The get_mnemonic_keyval() method returns the value of the "mnemonic-keyval" property that contains the keyval
    # used for the mnemonic accelerator if one has been set on the label.
    # If there is no mnemonic set up it returns the void symbol keyval.
    def get_mnemonic_keyval(self):
        if self.mnemonic_keyval:
            return self.mnemonic_keyval
        else:
            return None

    # The set_mnemonic_widget() method sets the "mnemonic-widget" property using the value of widget.
    # This method associates the label mnemonic with a widget that will be activated
    #   when the mnemonic accelerator is pressed.
    # When the label is inside a widget (like a Button or a Notebook tab) it is automatically associated
    #  with the correct widget, but sometimes (i.e. when the target is a gtk.Entry next to the label)
    #  you need to set it explicitly using this function.
    # The target widget will be activated by emitting "mnemonic_activate" on it.
    def set_mnemonic_widget(self, widget):
        self.mnemonic_widget = widget
        # emitting "mnemonic_activate"

    # The get_mnemonic_widget() method retrieves the value of the "mnemonic-widget" property which is the target
    # of the mnemonic accelerator of this label.
    # See set_mnemonic_widget().
    def get_mnemonic_widget(self):
        return self.mnemonic_widget

    # The set_text_with_mnemonic() method sets the label's text from the string str.
    # If characters in str are preceded by an underscore,
    # they are underlined indicating that they represent a mnemonic accelerator.
    # The mnemonic key can be used to activate another widget, chosen automatically,
    # or explicitly using the set_mnemonic_widget() method.
    def set_text_with_mnemonic(self, string):
        string = str(string)
        if self.pattern in string:
            newstring = str(string).replace(self.pattern, '')
            mnemonic_index = ''
            for i in range(0, len(string)):
                if self.pattern == string[i]:
                    mnemonic_index = i
            self.set_text(str(newstring) + str(newstring[mnemonic_index]))
            self.set_mnemonic_widget(self)
        else:
            self.set_text(string.index(self.pattern))

    def draw_widget_in_area(self):
        if self.get_text():
            if self.get_single_line_mode():
                self._draw_single_line_mode()
            else:
                self._draw_multi_line_mode()

    def update_preferred_sizes(self):
        if self.get_text():
            preferred_width = 0
            preferred_height = 1

            preferred_width += len(self.get_text())
            preferred_width += self._get_imposed_spacing() * 2

            self.set_preferred_height(preferred_height)
            self.set_preferred_width(preferred_width)
        else:
            return

    # Justification: LEFT, RIGHT, CENTER
    def set_justify(self, justify):
        justify = str(justify).upper()
        if justify == 'LEFT':
            self.justify = GLXC.JUSTIFY_LEFT
        elif justify == 'CENTER':
            self.justify = GLXC.JUSTIFY_CENTER
        elif justify == 'RIGHT':
            self.justify = GLXC.JUSTIFY_RIGHT
        elif justify == GLXC.JUSTIFY_LEFT:
            self.justify = GLXC.JUSTIFY_LEFT
        elif justify == GLXC.JUSTIFY_CENTER:
            self.justify = GLXC.JUSTIFY_CENTER
        elif justify == GLXC.JUSTIFY_RIGHT:
            self.justify = GLXC.JUSTIFY_RIGHT
        else:
            self.justify = GLXC.JUSTIFY_CENTER

        self.update_preferred_sizes()

    def get_justify(self):
        return self.justify

    # The set_wrap() method sets the "wrap" property tot he value of wrap.
    # If wrap is True the label text will wrap if it is wider than the widget size;
    # otherwise, the text gets cut off at the edge of the widget.
    # Default, False
    def set_line_wrap(self, wrap=False):
        if bool(wrap):
            self.wrap = bool(wrap)
        else:
            self.wrap = False

    # The get_line_wrap() method returns the value of the "wrap" property.
    # If "wrap" is True the lines in the label are automatically wrapped. See set_line_wrap().
    def get_line_wrap(self):
        return bool(self.wrap)

    # The set_width_chars() method sets the "width-chars" property to the value of n_chars.
    # The "width_chars" property specifies the desired width of the label in characters.
    def set_width_chars(self, n_chars):
        self.width_chars = int(n_chars)

    # The get_width_chars() method returns the value of the "width-chars"
    # property that specifies the desired width of the label in characters.
    def get_width_chars(self):
        return int(self.width_chars)

    # The set_single_line_mode() method sets the "single-line-mode" property to the value of single_line_mode.
    # If single_line_mode is True the label is in single line mode where the height of the label does not
    # depend on the actual text, it is always set to ascent + descent of the font.
    def set_single_line_mode(self, single_line_mode):
        self.single_line_mode = bool(single_line_mode)

    # The get_single_line_mode() method returns the value of the "single-line-mode" property.
    # See the set_single_line_mode() method for more information
    def get_single_line_mode(self):
        return bool(self.single_line_mode)

    # The set_max_width_chars() method sets the "max-width-chars" property to the value of n_chars.
    def set_max_width_chars(self, n_chars):
        self.max_width_chars = n_chars

    # The get_max_width_chars() method returns the value of the "max-width-chars" property
    # which is the desired maximum width of the label in characters.
    def get_max_width_chars(self):
        return self.max_width_chars

    # The set_line_wrap_mode() method controls how line wrapping is done (if it is enabled, see refetch()).
    # The default is glxc.WRAP_WORD which means wrap on word boundaries.

    def set_line_wrap_mode(self, wrap_mode):
        self.wrap_mode = wrap_mode

    def get_line_wrap_mode(self):
        return self.wrap_mode

    # Internal
    def _get_x_offset(self):
        xalign, _ = self.get_alignment()
        xpadd, _ = self.get_padding()
        value = 0
        if self.get_label():
            value += int((self.get_width() - len(self.get_label())) * xalign)
        else:
            value += int((self.get_width() - 1) * xalign)

        if value <= 0:
            value = xpadd
            return value
        if 0 < xalign <= 0.5:
            value += xpadd
        elif 0.5 <= xalign <= 1.0:
            value -= xpadd
        return value

    def _get_y_offset(self):
        _, yalign = self.get_alignment()
        _, ypadd = self.get_padding()

        # substract 1 that because :)
        value = int((self.get_height() - 1) * yalign)
        if value <= 0:
            value = ypadd
            return value
        if 0 < ypadd <= 0.5:
            value += ypadd
        elif 0.5 <= yalign <= 1.0:
            value -= ypadd
        return value

    def _get_single_line_resided_label_text(self, separator='~'):

        xpadd, _ = self.get_padding()
        max_width = self.get_width() - (xpadd * 2)

        dedented_text = textwrap.dedent(self.get_label()).strip()
        filled_text = textwrap.fill(dedented_text)

        border_width = self.get_width() - len(filled_text) + (xpadd * 2)
        if self.get_max_width_chars() <= -1:
            if border_width <= xpadd * 2 + 1:
                return filled_text[:(max_width / 2) - 1] + separator + filled_text[-max_width / 2:]
            else:
                return filled_text
        elif self.get_max_width_chars() == 0:
            return ''
        else:
            return filled_text[:self.get_max_width_chars()]

    def _draw_single_line_mode(self):
        try:
            self.get_curses_subwin().addstr(
                self._get_y_offset(),
                self._get_x_offset(),
                self._get_single_line_resided_label_text(),
                self.get_style().get_color_pair(
                    foreground=self.get_style().get_color_text('text', 'STATE_NORMAL'),
                    background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
                )
            )
        except curses.error:
            pass

    def _draw_multi_line_mode(self):
        xpadd, ypadd = self.get_padding()
        max_height = self.get_height() - (ypadd * 2)
        max_width = self.get_width() - (xpadd * 2)
        increment = 0
        for line in self._textwrap(text=self.get_label(), height=max_height, width=max_width):
            try:
                if self.get_max_width_chars() <= -1:
                    self.get_curses_subwin().addstr(
                        self._get_y_offset() + increment,
                        self._get_x_offset(),
                        self._check_justification(text=line, width=max_width),
                        self.get_style().get_color_pair(
                            foreground=self.get_style().get_color_text('text', 'STATE_NORMAL'),
                            background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
                        )
                    )
                elif self.get_max_width_chars() == 0:
                    pass
                else:
                    self.get_curses_subwin().addstr(
                        self._get_y_offset() + increment,
                        self._get_x_offset(),
                        self._check_justification(
                            text=line,
                            width=self.get_max_width_chars()
                        )[:self.get_max_width_chars()],
                        self.get_style().get_color_pair(
                            foreground=self.get_style().get_color_text('text', 'STATE_NORMAL'),
                            background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
                        )
                    )
            except curses.error:
                pass
            increment += 1

    def _textwrap(self, text='Hello World!', height=24, width=80):
        if self.get_line_wrap():
            lines = []
            for paragraph in text.split('\n'):
                line = []
                len_line = 0
                if self.get_line_wrap_mode() == GLXC.WRAP_WORD_CHAR:
                    # Wrap this text.
                    wraped = textwrap.wrap(
                        paragraph,
                        width=width,
                        fix_sentence_endings=True,
                        break_long_words=True,
                        break_on_hyphens=True,
                    )

                    if len(lines) <= height:
                        lines += wraped
                elif self.get_line_wrap_mode() == GLXC.WRAP_CHAR:
                    if len(paragraph) < width:
                        if len(lines) < height:
                            lines.append(paragraph)
                    else:
                        if len(lines) < height:
                            lines += [paragraph[ind:ind + width] for ind in range(0, len(paragraph), width)]
                else:
                    for word in paragraph.split(' '):
                        len_word = len(word)
                        if len_line + len_word <= width:
                            line.append(word)
                            len_line += len_word + 1
                        else:
                            lines.append(' '.join(line))
                            line = [word]
                            len_line = len_word + 1

                    if len(lines) < height:
                        lines.append(' '.join(line))
            return lines
        else:
            # This is the default display/view
            lines = []
            for paragraph in text.split('\n'):
                if len(paragraph) < width:
                    if len(lines) < height:
                        lines.append(paragraph)
                else:
                    if len(lines) < height:
                        lines.append(paragraph[:width])
            return lines

    def _check_justification(self, text="Hello World!", width=80):
        # Check Justification
        self.text_x = 0
        if self.get_justify() == GLXC.JUSTIFY_CENTER:
            return text.center(width, ' ')
        elif self.get_justify() == GLXC.JUSTIFY_LEFT:
            return "{0:<{1}}".format(text, width)
        elif self.get_justify() == GLXC.JUSTIFY_RIGHT:
            return "{0:>{1}}".format(text, width)
        else:
            self.set_alignment(self._get_x_offset(), self._get_y_offset())
        return self.text_x

    def _check_position_type(self):
        self.text_y = self._get_y_offset()
        return self.text_y
