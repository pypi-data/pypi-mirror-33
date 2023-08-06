#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import GLXC
from GLXCurses import Bin


# Reference Document: https://developer.gnome.org/gtk3/stable/GtkFrame.html
class Frame(Bin):
    """
    :Description:

    The frame widget is a bin that surrounds its child with a decorative frame and an optional label.
    If present, the label is drawn in a gap in the top side of the frame.

    The position of the label can be
    controlled with :func:`Frame.set_label_align() <GLXCurses.Frame.Frame.set_label_align()>`.
    """
    def __init__(self):
        """
        :Attributes Details:

        .. py:attribute:: label

           Text of the frame's label.

              +----------------+-------------------------------------------+
              | Type           | :py:data:`str`                            |
              +----------------+-------------------------------------------+
              | Flags          | Read / Write                              |
              +----------------+-------------------------------------------+
              | Default value  | :py:data:`None`                           |
              +----------------+-------------------------------------------+


        .. py:attribute:: label_widget

           A widget to display in place of the usual frame label.

              +----------------+-------------------------------------------+
              | Type           | :class:`Widget <GLXCurses.Widget.Widget>` |
              +----------------+-------------------------------------------+
              | Flags          | Read / Write                              |
              +----------------+-------------------------------------------+
              | Default value  | :py:data:`None`                           |
              +----------------+-------------------------------------------+


        .. py:attribute:: label_xalign

           The horizontal alignment of the label.

              +----------------+-------------------------------------------+
              | Type           | :py:data:`float`                          |
              +----------------+-------------------------------------------+
              | Flags          | Read / Write                              |
              +----------------+-------------------------------------------+
              | Allowed values | [0,1]                                     |
              +----------------+-------------------------------------------+
              | Default value  | 0.0                                       |
              +----------------+-------------------------------------------+


        .. py:attribute:: label_yalign

           The vertical alignment of the label.

              +----------------+-------------------------------------------+
              | Type           | :py:data:`float`                          |
              +----------------+-------------------------------------------+
              | Flags          | Read / Write                              |
              +----------------+-------------------------------------------+
              | Allowed values | [0,1]                                     |
              +----------------+-------------------------------------------+
              | Default value  | 0.5                                       |
              +----------------+-------------------------------------------+


        .. py:attribute:: shadow_type

           Appearance of the frame border.

              +----------------+-------------------------------------------+
              | Type           | :py:data:`ShadowType`                     |
              +----------------+-------------------------------------------+
              | Flags          | Read / Write                              |
              +----------------+-------------------------------------------+
              | Default value  | glxc.SHADOW_ETCHED_IN                     |
              +----------------+-------------------------------------------+

        """
        # Load heritage
        Bin.__init__(self)

        # It's a GLXCurse Type
        self.glxc_type = 'GLXCurses.Frame'

        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.set_name(self.__class__.__name__)

        # Make a Widget Style heritage attribute as local attribute
        if self.get_style().get_attribute_states():
            self.set_attribute_states(self.get_style().get_attribute_states())

        self.preferred_height = 2
        self.preferred_width = 2

        self.set_decorated(1)
        self.set_border_width(1)
        self._set_imposed_spacing(1)

        ####################
        # Frame Attribute  #
        ####################
        self.label = ''
        self.label_widget = None
        self.label_xalign = 0
        self.label_yalign = 0
        self.shadow_type = GLXC.SHADOW_NONE

    # GLXC Frame Functions
    def draw_widget_in_area(self):

        # Apply the Background color
        self.get_curses_subwin().bkgdset(
            ord(' '),
            self.get_style().get_color_pair(
                foreground=self.get_style().get_color_text('text', 'STATE_NORMAL'),
                background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
            )
        )
        self.get_curses_subwin().bkgd(
            ord(' '),
            self.get_style().get_color_pair(
                foreground=self.get_style().get_color_text('text', 'STATE_NORMAL'),
                background=self.get_style().get_color_text('bg', 'STATE_NORMAL')
            )
        )

        # Check widgets to display
        if bool(self.get_child()):
            self.get_child().set_style(self.get_style())
            self.get_child().draw()

        # Create a box and add the name of the windows like a king, who trust that !!!
        self.get_curses_subwin().box()

        # Add the Label
        if self.get_label():
            self.get_curses_subwin().addstr(
                self._get_label_y(),
                self._get_label_x(),
                self._get_resided_label_text()
            )

    def new(self, label=None):
        """
        Create a new :class:`Frame <GLXCurses.Frame.Frame>`, with optional label text .
        If label is None, the label is omitted.

        :param label: the text to use as the label of the frame.
        :type label: str or None
        :return: a new :class:`Frame <GLXCurses.Frame.Frame>` widget
        :rtype: :class:`Widget <GLXCurses.Widget.Widget>`
        """
        self.__init__()
        if label is None:
            self.set_label('')
        else:
            self.set_label(label)

        return self

    def set_label(self, label):
        """
        Sets the text of the label. If label is :py:data:`None`, the current label is removed.

        :param label: the text to use as the label of the frame.
        :type label: :py:data:`str` or :py:data:`None`
        """
        if bool(label):
            self.label = label
        else:
            self.label = None

    def set_label_widget(self, label_widget):
        """
        Sets the label widget for the frame. This is the widget that will appear embedded in the top edge of the
        frame as a title.

        :param label_widget: the new label widget
        :type label_widget: :class:`Widget <GLXCurses.Widget.Widget>`
        """
        self.label_widget = label_widget

    def set_label_align(self, xalign, yalign):
        """
        Sets the alignment of the frame widget’s label. The default values for a newly created frame are 0.0 and 0.5.

        :param xalign: The position of the label along the top edge of the widget. A value of 0.0 represents left \
        alignment; 1.0 represents right alignment.
        :param yalign: The y alignment of the label. A value of 0.0 aligns under the frame; 1.0 aligns above the \
        frame. If the values are exactly 0.0 or 1.0 the gap in the frame won’t be painted because the label will \
        be completely above or below the frame.
        :type xalign: float
        :type yalign: float
        """
        # xalign :
        # the horizontal alignment of the label widget along the top edge of the frame (in the range of 0.0 to 1.0)
        xalign = float(xalign)
        if xalign > 1.0:
            xalign = 1.0
        elif xalign < 0.0:
            xalign = 0.0
        # yalign :
        # the vertical alignment of the decoration with respect to the label widget (in the range 0.0 to 1.0)
        yalign = float(yalign)
        if yalign > 1.0:
            yalign = 1.0
        elif yalign < 0.0:
            yalign = 0.0

        self.label_xalign = xalign
        self.label_yalign = yalign

    def set_shadow_type(self, shadow_type=GLXC.SHADOW_NONE):
        """
        Sets the shadow type for frame .

        :param shadow_type: the new :py:data:`ShadowType`
        """
        if shadow_type is None:
            shadow_type = GLXC.SHADOW_NONE
        shadow_type = shadow_type

        self.shadow_type = shadow_type

    # The get_label() method returns the text in the label widget.
    # If there is no label widget or the label widget is not a Label the method returns None.
    def get_label(self):
        """
        If the frame’s label widget is a :class:`Label <GLXCurses.Label.Label>`, returns the text in the label widget. \
        (The frame will have a :class:`Label <GLXCurses.Label.Label>` for the label widget if \
        a non-NULL argument was passed when create the  :class:`Frame <GLXCurses.Frame.Frame>` .)

        :return: the text in the label, or :py:data:`None` if there was no label widget or the label widget was not a \
        :class:`Label <GLXCurses.Label.Label>` . This string is owned by GLXCurses and must not be modified or freed.
        :rtype: :py:data:`str` or :py:data:`None`
        """
        if self.get_label_widget():
            return None
        else:
            return self.label

    def get_label_align(self):
        """
        Retrieves the X and Y alignment of the frame’s label.

        .. seealso:: :func:`Frame.set_label_align() <GLXCurses.Frame.Frame.set_label_align()>`

        **xalign**: X location of frame label

        **yalign**: Y location of frame label


        :return: xalign, yalign
        :rtype: :py:data:`float`, :py:data:`float`
        """
        return self.label_xalign, self.label_yalign

    def get_label_widget(self):
        """
        Retrieves the label widget for the frame.

        .. seealso:: :func:`Frame.set_label_widget() <GLXCurses.Frame.Frame.set_label_widget()>`

        :return: the label widget, or NULL if there is none.
        :rtype: :class:`Widget <GLXCurses.Widget.Widget>` or :py:data:`None`
        """
        return self.label_widget

    def get_shadow_type(self):
        """
        Retrieves the shadow type of the frame.

        .. seealso:: :func:`Frame.set_shadow_type() <GLXCurses.Frame.Frame.set_shadow_type()>`

        :return: the current shadow type of the frame.
        :rtype: ShadowType
        """
        return self.shadow_type

    # Internal
    def _get_label_x(self):
        xalign, yalign = self.get_label_align()
        value = 0
        value += int((self.get_width() - len(self.get_label())) * xalign)
        if value <= 0:
            value = self._get_imposed_spacing()
            return value
        if 0 < xalign <= 0.5:
            value += self._get_imposed_spacing()
        elif 0.5 <= xalign <= 1.0:
            value -= self._get_imposed_spacing()
        return value

    def _get_label_y(self):
        xalign, yalign = self.get_label_align()
        value = int(self.get_height() * yalign)
        if value < 0:
            value = 0
        return value

    def _get_resided_label_text(self, separator='~'):
        border_width = self.get_width() - len(self.get_label()) + (self._get_imposed_spacing() * 2)
        max_width = self.get_width() - (self._get_imposed_spacing() * 2)
        if border_width <= self._get_imposed_spacing() * 2 + 1:
            text_to_return = self.get_label()[:(max_width / 2) - 1] + separator + self.get_label()[-max_width / 2:]
            return text_to_return
        else:
            return self.get_label()
