#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import Object
from GLXCurses import Style
from GLXCurses.Utils import new_id
from GLXCurses.Utils import glxc_type


class Widget(Object):
    def __init__(self):
        # Load heritage
        Object.__init__(self)

        # It's a GLXCurse Type
        self.glxc_type = 'GLXCurses.Widget'

        # Unique ID it permit to individually identify a widget by example for get_focus get_default
        self.id = new_id()

        # Widget Setting
        self.set_flags(self.get_default_flags())

        self.state = dict()
        self.state['NORMAL'] = True
        self.state['ACTIVE'] = False
        self.state['PRELIGHT'] = False
        self.state['SELECTED'] = False
        self.state['INSENSITIVE'] = False

        # Widget
        self.curses_subwin = None
        self.imposed_spacing = 0
        self.widget_decorated = False

        # Widget Parent
        # Set the Application
        self.screen = None
        self.attribute_states = None

        # Size Management
        self.screen_height = 0
        self.screen_width = 0
        self.screen_y = 0
        self.screen_x = 0
        self.parent_y = 0
        self.parent_x = 0
        self.parent_width = 0
        self.parent_height = 0
        self.y = 0
        self.x = 0
        self.width = 0
        self.height = 0
        self.preferred_height = 0
        self.preferred_width = 0
        self.natural_height = 0
        self.natural_width = 0
        self.preferred_size = 0

        # Property
        # If True, the application will paint directly on the widget
        self.set_app_paintable(False)

        # If True, the widget can be the default widget
        self.set_can_default(False)

        # If True, the widget can accept the input focus
        self.set_can_focus(False)

        # If True, the widget is part of a composite widget
        self.set_composite_child(False)

        # If True, the widget is double buffered
        self.set_double_buffered(False)

        # The event mask that decides what kind of Event this widget gets.
        self.events = None

        # The mask that decides what kind of extension events this widget gets.
        self.extension_events = None

        # If True, the widget is the default widget
        self.set_has_default(False)

        # If True, the widget has the input focus
        self.set_has_focus(False)

        # A value of True indicates that widget can have a tooltip
        self.has_tooltip = False

        # The height request of the widget, or 0 if natural/expendable request should be used.
        self.height_request = 0

        # If True, the widget is the focus widget within the widget
        self.is_focus = False

        # The name of the widget
        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.name = self.__class__.__name__

        # If True show_all() should not affect this widget
        self.no_show_all = False

        # The parent widget of this widget. Must be a Container widget.
        self.parent = None

        # If True, the widget will receive the default action when it is focused.
        self.receives_default = None

        # If True, the widget responds to input
        self.sensitive = False

        # The style of the widget, which contains information about how it will look (colors etc).
        # Each Widget come with it own Style by default
        # It can receive parent Style() or a new Style() during a set_parent() / un_parent() call
        # GLXCApplication is a special case where it have no parent, it role is to impose it own style to each Widget
        self.style = Style()

        self.style_backup = None

        # Sets the text of tooltip to be the given string.
        self.tooltip_text = None

        # If True, the widget is visible
        self.set_visible(True)

        # The width request of the widget, or -1 if natural/expendable request should be used.
        self.width_request = 0

        # The widget's window if realized, None otherwise.
        self.window = None

        self.sensitive = None

    # Common Widget mandatory
    def destroy(self):
        self.unparent()
        self.get_flags()['IN_DESTRUCTION'] = True

    # Screen
    def get_screen_height(self):
        self.screen_height, self.screen_width = self.get_screen().getmaxyx()
        return self.screen_height

    def get_screen_width(self):
        self.screen_height, self.screen_width = self.get_screen().getmaxyx()
        return self.screen_width

    def get_screen_x(self):
        self.screen_y, self.screen_x = self.get_screen().getbegyx()
        return self.screen_x

    def gef_screen_y(self):
        self.screen_y, self.screen_x = self.get_screen().getbegyx()
        return self.screen_y

    # The set_child_visible() method determines if the widget should be mapped along with its parent.
    # If is_visible is True the widget will be mapped with its parent if it has called the show() method.
    def set_child_visible(self, is_visible):
        self.set_visible(bool(is_visible))

    def get_child_visible(self):
        return self.set_visible

    def get_parent(self):
        if self.parent:
            return self.parent
        else:
            return self

    def get_toplevel(self):
        return self.flags['TOPLEVEL']

    # Parent Management
    def get_parent_size(self):
        return self.get_parent().curses_subwin.getmaxyx()

    def get_parent_origin(self):
        return self.get_parent().curses_subwin.getbegyx()

    # This function is useful only when implementing subclasses of GtkContainer.
    # Sets the container as the parent of curses_subwin , and takes care of some details such as updating the state
    # and style of the child to reflect its new location. The opposite function is gtk_widget_unparent().
    def _set_parent(self, parent):
        self.parent = parent

    def adopt(self, orphan):
        if hasattr(self, 'get_children'):
            pass
            # child_info = dict()
            # child_info['widget'] = orphan
            # self.get_children().append(child_info)

    def set_parent(self, parent):
        """
        This function is useful only when implementing subclasses of GtkContainer.
        Sets the container as the parent of widget , and takes care of some details such as updating
        the state and style of the child to reflect its new location.
        The opposite function is :func:`GLXCurses.Widget.unparent() <GLXCurses.Widget.Widget.unparent()>`.

        :param parent: parent container
        :type parent: GLXCurses.Container subclass
        :raise TypeError: if ``parent`` is not a GLXCurses type as tested by \
        :func:`glxc_type() <GLXCurses.Utils.glxc_type>`
        """
        # Try to exit as soon of possible
        if not glxc_type(parent) and parent is not None:
            raise TypeError('"parent" argument must be a GLXCurses object type or None')

        self._set_parent(parent)
        self.set_screen(self.get_parent().get_screen())

        # self.get_parent().adopt(self)

        # Widget start with own Style, and will use the Style of it parent when it add to a contener
        # GLXCApplication Widget is a special case where it parent is it self.

        self.style_backup = self.get_style()
        self.set_style(self.get_parent().get_style())

    def unparent(self):
        """
        This function is only for use in widget implementations.
        Should be called by implementations of the remove method on Container,
        to dissociate a child from the container.
        """
        self.get_parent()._unchild(self)
        self.set_parent(None)
        self.set_style(self.style_backup)

    def get_parent_spacing(self):
        return self.get_parent().get_spacing()

    def get_parent_style(self):
        return self.get_parent().get_style()

    def get_screen(self):
        return self.screen

    def set_screen(self, screen):
        self.screen = screen

    # Widget
    def get_widget_id(self):
        return self.id

    def get_curses_subwin(self):
        return self.curses_subwin

    def set_curses_subwin(self, subwin):
        self.curses_subwin = subwin
        self.height, self.width = self.get_size()
        self.y, self.x = self.get_origin()

    def get_origin(self):
        return self.get_curses_subwin().getbegyx()

    def set_decorated(self, decorated):
        self.widget_decorated = decorated

    def get_decorated(self):
        return self.widget_decorated

    def refresh(self):
        self.draw()

    def show(self):
        self.draw()

    def show_all(self):
        self.draw()
        self.get_parent().draw()

    # Name management use for GLXCStyle color's
    def override_color(self, color):
        self.get_style().get_attribute_states()['text']['STATE_NORMAL'] = str(color).upper()

    def override_background_color(self, color):
        self.get_style().get_attribute_states()['bg']['STATE_NORMAL'] = str(color).upper()

    # Size management
    def get_width(self):
        return self.width

    def set_width(self, width):
        if self.get_width() != width:
            self.width = width

    def get_height(self):
        return self.height

    def set_height(self, height):
        if self.get_height() != height:
            self.height = height

    def get_preferred_height(self):
        return self.preferred_height

    def set_preferred_height(self, height):
        if self.get_preferred_height() != height:
            self.preferred_height = height

    def get_preferred_width(self):
        return self.preferred_width

    def set_preferred_width(self, preferred_width):
        if self.get_preferred_width() != preferred_width:
            self.preferred_width = preferred_width

    def get_preferred_size(self):
        return self.preferred_size

    def set_preferred_size(self):
        self.preferred_size

    def get_size(self):
        return self.get_curses_subwin().getmaxyx()

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    # State
    # Sets the sensitivity of a curses_subwin.
    # A curses_subwin is sensitive if the user can interact with it. Insensitive widgets are “grayed out”
    # and the user can’t interact with them.

    def set_attribute_states(self, attribute_states):
        if self.attribute_states != attribute_states:
            self.attribute_states = attribute_states

    def get_attribute_states(self):
        return self.attribute_states

    # Properties
    def set_app_paintable(self, boolean):
        if self.flags['APP_PAINTABLE'] != bool(boolean):
            self.flags['APP_PAINTABLE'] = bool(boolean)

    def get_app_paintable(self):
        return self.flags['APP_PAINTABLE']

    def set_can_default(self, boolean):
        if self.flags['CAN_DEFAULT'] != bool(boolean):
            self.flags['CAN_DEFAULT'] = bool(boolean)

    def get_can_default(self):
        return self.flags['CAN_DEFAULT']

    def set_can_focus(self, boolean):
        if self.flags['CAN_FOCUS'] != bool(boolean):
            self.flags['CAN_FOCUS'] = bool(boolean)

    def get_can_focus(self):
        return self.flags['CAN_FOCUS']

    def set_composite_child(self, boolean):
        if self.flags['COMPOSITE_CHILD'] != bool(boolean):
            self.flags['COMPOSITE_CHILD'] = bool(boolean)

    def get_composite_child(self):
        return self.flags['COMPOSITE_CHILD']

    def set_double_buffered(self, boolean):
        if self.flags['COMPOSITE_CHILD'] != bool(boolean):
            self.flags['DOUBLE_BUFFERED'] = bool(boolean)

    def get_double_buffered(self):
        return self.flags['DOUBLE_BUFFERED']

    def set_events(self, events):
        if self.events != events:
            self.events = events

    def get_events(self):
        return self.events

    def set_extension_events(self, extension_events):
        if self.extension_events != extension_events:
            self.extension_events = extension_events

    def get_extension_events(self):
        return self.extension_events

    def set_has_default(self, boolean):
        if self.flags['HAS_DEFAULT'] != bool(boolean):
            self.flags['HAS_DEFAULT'] = bool(boolean)

    def get_has_default(self):
        return self.flags['HAS_DEFAULT']

    def set_has_tooltip(self, boolean):
        if self.has_tooltip != bool(boolean):
            self.has_tooltip = bool(boolean)

    def get_has_tooltip(self):
        return self.has_tooltip

    def set_height_request(self, height):
        if self.height_request != height:
            self.height_request = height

    def get_height_request(self):
        return self.height_request

    def set_is_focus(self, boolean):
        if not self.get_sensitive():
            if self.is_focus is not False:
                self.is_focus = False
        else:
            if self.is_focus != bool(boolean):
                self.is_focus = bool(boolean)

    def get_is_focus(self):
        return self.is_focus

    def set_name(self, name=None):
        """
        Widgets can be named, which allows you to refer to them from a JSon file.
        You can apply a style to widgets with a particular name in the JSon file.

        See the documentation for the JSon syntax (on the same page as the docs for GLXCurses.StyleContext).

        :param name: Name of the widget, or None or widget Class Name
        :type name: str or None
        """
        # Tr to exit as soon of possible
        if name is None:
            name = self.__class__.__name__

        if type(name) != str:
            raise TypeError("'name' must be an str type or None")

        # make the job
        if self.name != name:
            self.name = name

    def get_name(self):
        """
        Retrieves the name of a widget.

        See GLXCurses.Widget.set_name() for the significance of widget names.

        :return: name of the widget. This string is owned by GLXCurses and should not be modified or freed
        :rtype: str
        """
        return self.name

    def set_no_show_all(self, boolean):
        if self.no_show_all != bool(boolean):
            self.no_show_all = bool(boolean)

    def get_no_show_all(self):
        return self.no_show_all

    def set_receives_default(self, boolean):
        if self.receives_default != bool(boolean):
            self.receives_default = bool(boolean)

    def get_receives_default(self):
        return self.receives_default

    def set_style(self, style):
        if self.style != style:
            self.style = style

    def get_style(self):
        return self.style

    def set_tooltip_text(self, text):
        if self.tooltip_text != text:
            self.tooltip_text = text

    def get_tooltip_text(self):
        return self.tooltip_text

    def set_visible(self, boolean):
        if self.flags['VISIBLE'] != bool(boolean):
            self.flags['VISIBLE'] = bool(boolean)

    def get_visible(self):
        return self.flags['VISIBLE']

    def set_has_focus(self, boolean):
        if self.flags['HAS_FOCUS'] != bool(boolean):
            self.flags['HAS_FOCUS'] = bool(boolean)

    def get_has_focus(self):
        return self.flags['HAS_FOCUS']

    def set_sensitive(self, boolean):
        if self.sensitive != bool(boolean):
            self.sensitive = bool(boolean)
        if self.state['INSENSITIVE'] != bool(boolean):
            self.state['INSENSITIVE'] = bool(boolean)
        if not self.get_sensitive():
            self.set_is_focus(0)

    def get_sensitive(self):
        return self.sensitive

    def set_width_request(self, width):
        if self.width_request != width:
            self.width_request = width

    def get_width_request(self):
        return self.width_request

    def get_window(self):
        return self.window

    # DRAW
    def draw(self):
        try:
            self.height, self.width = self.get_parent().get_curses_subwin().getmaxyx()
            self.y, self.x = self.get_parent().get_curses_subwin().getbegyx()

            # Check if the Parent have decoration add and 1 to spacing in case
            padding = 0
            if self.get_parent().get_decorated():
                padding += self.get_parent().get_border_width()

            min_size_width = (padding * 2) + 1
            min_size_height = (padding * 2) + 1

            height_ok = self.get_height() >= min_size_height
            width_ok = self.get_width() >= min_size_width

            if not height_ok or not width_ok:
                return

            drawing_area = self.get_parent().get_curses_subwin().subwin(
                self.get_height() - (padding * 2),
                self.get_width() - (padding * 2),
                self.get_y() + padding,
                self.get_x() + padding
            )

            self.set_curses_subwin(drawing_area)
            if (self.get_height() > self.preferred_height) and (self.get_width() > self.preferred_width):
                self.draw_widget_in_area()

        except AttributeError:
            pass

    # Selection and Focus

    # Internal
    def _get_imposed_spacing(self):
        return int(self.imposed_spacing)

    def _set_imposed_spacing(self, spacing):
        if self.imposed_spacing != int(spacing):
            self.imposed_spacing = int(spacing)

    def _unchild(self, orphan):

        if hasattr(self, 'get_children'):
            if bool(self.get_children()):
                count = 0
                last_found = None
                for children in self.get_children():
                    if orphan == children['widget']:
                        last_found = count
                    count += 1
                if last_found is not None:
                    self.get_children().pop(last_found)

        if hasattr(self, 'get_child'):
            if bool(self.child):
                if self.child['widget'] == orphan:
                    self.child = None

    # Signal management Client part

