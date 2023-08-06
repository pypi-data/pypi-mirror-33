#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

# Inspired by: https://developer.gnome.org/gtk3/stable/GtkRange.html

from GLXCurses import Widget
from GLXCurses import Adjustment
from GLXCurses import GLXC
from GLXCurses.Utils import new_id
from GLXCurses.Utils import glxc_type
from GLXCurses.Utils import clamp


class Range(Widget):
    """
    Range — Base class for widgets which visualize an adjustment
    """

    def __init__(self):
        """
        **Properties**

        .. py:attribute:: adjustment

           The GLXCurses.Adjustment.Adjustment that contains the current value of this range object.

              :Type: GLXCurses.Adjustment.Adjustment
              :Flags: Read / Write / Construct

        .. py:attribute:: fill_level

           The fill level (e.g. prebuffering of a network stream). See GLXCurses.Adjustment.Adjustment.set_fill_level().

              :Type: float
              :Flags: Read / Write
              :Default value: 1.79769e+308

        .. py:attribute:: inverted

           Invert direction slider moves to increase range value.

              :Type: bool
              :Flags: Read / Write
              :Default value: False

        .. py:attribute:: model

           The model to find matches in.

              :Type: TreeModel
              :Flags: Read / Write

        .. py:attribute:: lower_stepper_sensitivity

           The sensitivity policy for the stepper that points to the adjustment's lower side.

              :Type: bool
              :Flags: Read / Write
              :Default value: GLXC.SENSITIVITY_AUTO

        .. py:attribute:: restrict_to_fill_level

           The restrict-to-fill-level property controls whether slider movement is restricted to an upper boundary set
           by the fill level. See GLXCurses.Adjustment.Adjustment.set_restrict_to_fill_level().

              :Type: bool
              :Flags: Read / Write
              :Default value: True

        .. py:attribute:: round-digits

           The number of digits to round the value to when it changes, or -1. See “change-value”.

              :Type: int
              :Flags: Read / Write
              :Allowed values: >= -1
              :Default value: -1

        .. py:attribute:: show_fill_level

           The show-fill-level property controls whether fill level indicator graphics are displayed on the trough.
           See GLXCurses.Adjustment.Adjustment.set_show_fill_level().

              :Type: bool
              :Flags: Read / Write
              :Default value: False

        .. py:attribute:: upper_stepper_sensitivity

           The sensitivity policy for the stepper that points to the adjustment's upper side.

              :Type: GLXC.SensitivityType
              :Flags: Read / Write
              :Default value: GLXC.SENSITIVITY_AUTO

        """
        # Load heritage
        Widget.__init__(self)

        # It's a GLXCurse Type
        self.glxc_type = 'GLXCurses.Range'

        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.set_name(self.__class__.__name__)

        # Unique ID it permit to individually identify a widget by example for get_focus get_default
        self.id = new_id()

        # Widget Setting
        self.set_flags(self.get_default_flags())

        # Properties
        self.adjustment = Adjustment()
        self.fill_level = 1.79769e+308
        self.inverted = False
        self.lower_stepper_sensitivity = GLXC.SENSITIVITY_AUTO
        self.restrict_to_fill_level = True
        self.round_digits = -1
        self.show_fill_level = False
        self.upper_stepper_sensitivity = GLXC.SENSITIVITY_AUTO

        # Private
        self._flippable = False
        self._slider_size_fixed = False

    def get_fill_level(self):
        """
        Gets the current position of the fill level indicator.

        :return: The current fill level
        :rtype: int
        """
        return self.fill_level

    def get_restrict_to_fill_level(self):
        """
        Gets whether the range is restricted to the fill level.

        :return: True if range is restricted to the fill level.
        :rtype: bool
        """
        return self.restrict_to_fill_level

    def get_show_fill_level(self):
        """
        Gets whether the range displays the fill level graphically.

        :return: True if range shows the fill level.
        :rtype: bool
        """
        return self.show_fill_level

    def set_fill_level(self, fill_level=1.79769e+308):
        """
        Set the new position of the fill level indicator.

        The “fill level” is probably best described by its most prominent use case, which is an indicator for the
        amount of pre-buffering in a streaming media player. In that use case, the value of the range would indicate
        the current play position, and the fill level would be the position up to which the file/stream has been
        downloaded.

        This amount of prebuffering can be displayed on the range’s trough and is themeable separately from the
        trough. To enable fill level display, use GLXCurses.Range.Range.set_show_fill_level().
        The range defaults to not showing the fill level.

        Additionally, it’s possible to restrict the range’s slider position to values which are smaller than
        the fill level. This is controller by GLXCurses.Range.Range.set_restrict_to_fill_level() and is by default
        enabled.

        :param fill_level: the new position of the fill level indicator
        :type fill_level: float
        :raise TypeError: if ``fill_level`` is not a float type
        """
        # try to exit as soon of possible
        if type(fill_level) != float:
            raise TypeError("'fill_level' must be a float type")
        # In case we can do nothing
        if self.fill_level != fill_level:
            self.fill_level = fill_level

    def set_restrict_to_fill_level(self, restrict_to_fill_level=True):
        """
        Sets whether the slider is restricted to the fill level.
        See GLAXCurses.Range.Range.set_fill_level() for a general description of the fill level concept.

        :param restrict_to_fill_level: Whether the fill level restricts slider movement.
        :type restrict_to_fill_level: bool
        :raise TypeError: if ``restrict_to_fill_level`` is not a bool type
        """
        # try to exit as soon of possible
        if type(restrict_to_fill_level) != bool:
            raise TypeError("'restrict_to_fill_level' must be a bool type")
        # In case we can do nothing
        if self.restrict_to_fill_level != restrict_to_fill_level:
            self.restrict_to_fill_level = restrict_to_fill_level

    def set_show_fill_level(self, show_fill_level):
        """
        Sets whether a graphical fill level is show on the trough.
        See GLXCurses.Range.Range.set_fill_level() for a general description of the fill level concept.

        :param show_fill_level: Whether a fill level indicator graphics is shown.
        :type show_fill_level: bool
        :raise TypeError: if ``show_fill_level`` is not a bool type
        """
        # try to exit as soon of possible
        if type(show_fill_level) != bool:
            raise TypeError("'show_fill_level' must be a bool type")
        # In case we can do nothing
        if self.show_fill_level != show_fill_level:
            self.show_fill_level = show_fill_level

    def get_adjustment(self):
        """
        Get the GLXCurses.Adjustment.Adjustment which is the “model” object for GLXCurses.Range.Range.
        See GLXCurses.Range.Range.set_adjustment() for details.

        That because GLXCurses.Range.Range use internally a GLXCurses.Adjustment.Adjustment, the Attribute
        ``adjustment`` should never been touch or unreferenced.

        :return: A GLXCurses.Adjustment.Adjustment
        :rtype: GLXCurses.Adjustment.Adjustment
        """
        return self.adjustment

    def set_adjustment(self, adjustment=None):
        """
        Sets the adjustment to be used as the “model” object for this range widget.

        The adjustment indicates the current range value, the minimum and maximum range values, the step/page
        increments used for keybindings and scrolling, and the page size. The page size is normally 0 for
        GtkScale and nonzero for Scrollbar, and indicates the size of the visible area of the widget being
        scrolled. The page size affects the size of the scrollbar slider.

        :param adjustment: GLXCurses.Adjustment.Adjustment or None for create a new one
        :type adjustment: GLXCurses.Adjustment.Adjustment or None
        :raise TypeError: if ``adjustment`` is not a GLXCurses.Adjustment.Adjustment or None
        """
        if adjustment is None:
            self.adjustment = Adjustment()
        else:
            if glxc_type(adjustment):
                if adjustment != self.adjustment:
                    self.adjustment = adjustment
            else:
                raise TypeError("'adjustment' must be GLXCurses.Adjustment.Adjustment or None")

    def get_inverted(self):
        """
        Gets the value set by GLXCurses.Range.Range.set_inverted().

        :return: True if the range is inverted
        :rtype: bool
        """
        return self.inverted

    def set_inverted(self, setting=False):
        """
        Ranges normally move from lower to higher values as the slider moves from top to bottom or left to right.
        Inverted ranges have higher values at the top or on the right rather than on the bottom or left.

        :param setting: True to invert the range
        :type setting: bool
        :raise TypeError: if ``setting`` is not a a bool type
        """
        # try to exit as soon of possible
        if type(setting) != bool:
            raise TypeError("'setting' must be a bool type")
        # In case we can do nothing
        if self.inverted != setting:
            self.inverted = setting

    def get_value(self):
        """
        Gets the current value of the range.

        :return: current value of the range.
        :rtype: float
        """
        return self.get_adjustment().get_value()

    def set_value(self, value=float):
        """
        Sets the current value of the range; if the value is outside the minimum or maximum range values,
        it will be clamped to fit inside them. The range emits the “value-changed” signal if the value changes.

        :param value: new value of the range
        :type value: float
        :raise TypeError: if ``value`` is not a a float type
        """
        if type(value) != float:
            raise TypeError("'value' must be a float type")
        # clamp value just because the GTK source make it like that
        if self.get_restrict_to_fill_level():
            value = clamp(
                value=value,
                smallest=self.get_adjustment().get_lower(),
                largest=self.get_fill_level()
            )
        # just in case we can do nothing
        if self.get_adjustment().get_value() != value:
            self.get_adjustment().value = value

    def set_increments(self, step=float, page=float):
        """
        Sets the step increment and page increment for the range. The step increment is used when the user clicks the
        GLXCurses.Scrollbar.Scrollbar arrows or moves GLXCurses.Scale.Scale via arrow keys.
        The page size is used for example when moving via Page Up or Page Down keys.

        Care: the GTK documentation is worng compare to the the GTK Code source:
        https://github.com/GNOME/gtk/blob/master/gtk/gtkrange.c#L1001

        That is step_increment and page_increment it be upgrade via a Adjustment.configure() and not
        step size and page size.

        :param step: the new step increment
        :type step: float
        :param page: the new page increment
        :type page: float
        """

        self.get_adjustment().configure(
            value=self.get_adjustment().get_value(),
            lower=self.get_adjustment().get_lower(),
            upper=self.get_adjustment().get_upper(),
            step_increment=step,
            page_increment=page,
            page_size=self.get_adjustment().get_page_size()
        )

    def set_range(self, min=None, max=None):
        """
        Sets the allowable values in the GLXCurses.Range.Range, and clamps the range value to be between min and max .
        (If the range has a non-zero page size, it is clamped between min and max - page-size.)

        :param min: minimum range value
        :type min: float
        :param max: maximum range value
        :type max: float
        """

        value = self.get_adjustment().get_value()
        if self.get_restrict_to_fill_level():
            value = clamp(
                value=value,
                smallest=self.get_adjustment().get_lower(),
                largest=self.get_fill_level()
            )

        self.get_adjustment().configure(
            value=value,
            lower=min,
            upper=max,
            step_increment=self.get_adjustment().get_step_increment(),
            page_increment=self.get_adjustment().get_page_increment(),
            page_size=self.get_adjustment().get_page_size()
        )

    def get_round_digits(self):
        """
        Gets the number of digits to round the value to when it changes. See “change-value”.

        :return: the number of digits to round to
        :rtype: int
        """
        return self.round_digits

    def set_round_digits(self, round_digits=-1):
        """
        Sets the number of digits to round the value to when it changes. See “change-value”.

        :param round_digits: the precision in digits, or -1
        :type round_digits: int
        :raise TypeError: if ``round_digits`` is not a a int type
        """
        # check if we can exit before do something
        if type(round_digits) != int:
            raise TypeError("'round_digits' must be a int type")
        # check if we have really to do something
        if self.round_digits != round_digits:
            self.round_digits = round_digits

    def set_lower_stepper_sensitivity(self, sensitivity=GLXC.SENSITIVITY_AUTO):
        """
        Sets the sensitivity policy for the stepper that points to the 'lower' end of the
        GLXCurses.Range.Range’s adjustment.

        Allowed Type:

        **The arrow is made insensitive if the thumb is at the end**
         GLXC.SENSITIVITY_AUTO = 'AUTO'

        **The arrow is always sensitive**
         GLXC.SENSITIVITY_ON = 'ON'

        **The arrow is always insensitive**
         GLXC.SENSITIVITY_OFF = 'OFF'

        :param sensitivity: the lower stepper’s sensitivity policy.
        :type sensitivity: GLXC.SensitivityType
        :raise TypeError: if ``sensitivity`` is not a GLXC.SensitivityType
        """
        # exit as soon of possible
        if sensitivity not in GLXC.SensitivityType:
            raise TypeError("'sensitivity' must be a valid GLXC.SensitivityType")
        # check if we can to nothing
        if self.lower_stepper_sensitivity != sensitivity:
            self.lower_stepper_sensitivity = sensitivity

    def get_lower_stepper_sensitivity(self):
        """
        Gets the sensitivity policy for the stepper that points to the 'lower' end of the
        GLXCurses.Range.Range’s adjustment.

        :return: The lower stepper’s sensitivity policy.
        :rtype: GLXC.SensitivityType
        """
        return self.lower_stepper_sensitivity

    def set_upper_stepper_sensitivity(self, sensitivity=GLXC.SENSITIVITY_AUTO):
        """
        Sets the sensitivity policy for the stepper that points to the 'upper' end of the
        GLXCurses.Range.Range’s adjustment.

        :param sensitivity: The upper stepper’s sensitivity policy.
        :type sensitivity: GLXC.SensitivityType
        :raise TypeError: if ``sensitivity`` is not a GLXC.SensitivityType
        """
        # exit as soon of possible
        if sensitivity not in GLXC.SensitivityType:
            raise TypeError("'sensitivity' must be a valid GLXC.SensitivityType")
        # check if we can to nothing
        if self.upper_stepper_sensitivity != sensitivity:
            self.upper_stepper_sensitivity = sensitivity

    def get_upper_stepper_sensitivity(self):
        """
        Gets the sensitivity policy for the stepper that points to the 'upper' end of the
        GLXCurses.Range.Range’s adjustment.

        :return: The upper stepper’s sensitivity policy.
        :rtype: GLXC.SensitivityType
        """
        return self.upper_stepper_sensitivity

    def get_flippable(self):
        """
        Gets the value set by GLXCurses.Range.Range.set_flippable().

        :return: True if the range is flippable
        :rtype: bool
        """
        return self._flippable

    def set_flippable(self, flippable=False):
        """
        If a range is flippable, it will switch its direction if it is horizontal and its direction is
        GLXC.TEXT_DIR_RTL.

        :param flippable: True to make the range flippable
        :type flippable: bool
        :raise TypeError: if ``flippable`` is not a bool type.
        """
        # check if we can to nothing
        if type(flippable) != bool:
            raise TypeError("'flippable' must be bool type")
        # upgrade value just in case
        if self._flippable != flippable:
            self._flippable = flippable
            # update_fill_position (range);
            # update_highlight_position (range)

    def get_range_rect(self):
        """
        This function returns the area that contains the range’s trough and its steppers, in widget->window coordinates.

        This function is useful mainly for Range subclasses.

        :return: list(x, y, width, height)
        :rtype: list
        """
        return [
            self.get_x(),
            self.get_y(),
            self.get_width(),
            self.get_height()
        ]

    # https://github.com/GNOME/gtk/blob/master/gtk/gtkrange.c#L962
    def get_slider_range(self, slider_start=None, slider_end=None):
        """
        This function returns sliders range along the long dimension, in widget->window coordinates.

        This function is useful mainly for Range subclasses.

        If slider_start or slider_end are not None it will return the value.

        Example:

        slider_start=None, slider_end=None return list [None; None]

        slider_start=1, slider_end=1 return list [the_calculated_slider_start; the_calculated_slider_end]

        :param slider_start: return location for the slider's start, or None
        :param slider_end: return location for the slider's end, or None

        """
        try:
            if self.orientation == GLXC.ORIENTATION_VERTICAL:
                if slider_start:
                    slider_start = self.y
                if slider_end:
                    slider_end = self.y + self.height
            else:
                if slider_start:
                    slider_start = self.y
                if slider_end:
                    slider_end = self.x + self.width
            # return something
            return [slider_start, slider_end]
        except AttributeError:
            return [None, None]

    def get_slider_size_fixed(self):
        """
        This function is useful mainly for GtkRange subclasses.

        See GLXCurses.Range.Range.set_slider_size_fixed().

        :return: whether the range’s slider has a fixed size.
        :rtype: bool
        """
        return self._slider_size_fixed

    def set_slider_size_fixed(self, size_fixed=bool):
        """
        Sets whether the range’s slider has a fixed size, or a size that depends on its adjustment’s page size.

        This function is useful mainly for GtkRange subclasses.

        :param size_fixed: True to make the slider size constant
        :type size_fixed: bool
        :raise TypeError: if ``size_fixed`` is not a bool type.
        """
        # try to exit a soon of possible
        if type(size_fixed) != bool:
            raise TypeError("'size_fixed' must be a bool type")
        # just in case it have nothing to do
        if self._slider_size_fixed != size_fixed:
            self._slider_size_fixed = size_fixed
