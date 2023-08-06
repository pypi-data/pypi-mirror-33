#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import Bin
from GLXCurses import Application
from GLXCurses.Utils import resize_text


class Window(Bin):
    def __init__(self):
        Bin.__init__(self)
        self.glxc_type = 'GLXCurses.Window'

        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.set_name(self.__class__.__name__)

        # Make a Style heritage attribute
        if self.get_style().get_attribute_states():
            self.set_attribute_states(self.get_style().get_attribute_states())

        self.preferred_height = 2
        self.preferred_width = 2

        #####################
        # Window Properties #
        #####################

        # Set the Application
        self.application = Application()

        # If True, the window should receive the input focus. Default value: True.
        self.accept_focus = True

        # If True, the user can expand the window beyond its minimum size. Default value: True.
        self.allow_grow = True

        # If True, the window has no minimum size.
        # Setting this to True is a bad idea 99% of the time. Default value: False.
        self.allow_shrink = False

        # If True, the window should be decorated by the window manager. Default value: True.
        self.decorated = True

        # The default height of the window, used when initially showing the window.
        # Allowed values: >= 0. Default value: 0
        self.default_height = 0

        # The default width of the window, used when initially showing the window.
        # Allowed values: >= 0. Default value: 0
        self.default_width = 0

        # If True, the window should be destroyed when its parent is destroyed. Default value: False.
        self.destroy_with_parent = False

        # If True, the window should receive the input focus when mapped. Default value: True
        self.focus_on_map = True

        # Gravity
        # GRAVITY_NORTH_WEST    The reference point is at the top left corner.
        # GRAVITY_NORTH         The reference point is in the middle of the top edge.
        # GRAVITY_NORTH_EAST    The reference point is at the top right corner.
        # GRAVITY_WEST          The reference point is at the middle of the left edge.
        # GRAVITY_CENTER        The reference point is at the center of the window.
        # GRAVITY_EAST          The reference point is at the middle of the right edge.
        # GRAVITY_SOUTH_WEST    The reference point is at the lower left corner.
        # GRAVITY_SOUTH         The reference point is at the middle of the lower edge.
        # GRAVITY_SOUTH_EAST    The reference point is at the lower right corner.
        # GRAVITY_STATIC        The reference point is at the top left corner of the window itself,
        #                       ignoring window manager decorations.
        self.gravity = 'GRAVITY_NORTH_WEST'

        # If True, the input focus is within the window. Default value: False.
        self.has_toplevel_focus = False

        # The icon for this window
        self.icon = None

        # The name of the themed icon to use as the window icon. See IconTheme for more details. Default value: None
        self.icon_name = None

        # If True, the toplevel is the current active window. Default value: False.
        self.is_active = False

        # If True, mnemonics are currently visible in the window. Default value: True.
        self.mnemonics_visible = True

        # If True, the window is modal (other windows are not usable while this one is up). Default value: False.
        self.modal = False

        # opacity
        # Unsuport

        # If True, the user can resize the window. Default value: True.
        self.resizable = True

        # Unique identifier for the window to be used when restoring a session. Default value: None.
        self.role = None

        # The screen where this window will be displayed
        self.screen = None

        # If True, the window should not be in the pager. Default value: False.
        self.skip_pager_hint = False

        # If True, the window should not be in the task bar. Default value: False.
        self.skip_taskbar_hint = False

        # The :startup-id is a write-only property for setting window's startup notification identifier.
        # See Window.set_startup_id() for more details. Default value: None
        self.startup_id = None

        # The title of the window. Default value: None.
        self.title = None

        # The transient parent of the window.
        # See gtk.Window.set_transient_for() for more details about transient windows.
        self.transient_for = None

        # The type of the window. Default value: WINDOW_TOPLEVEL
        self.type = 'WINDOW_TOPLEVEL'

        # Hint to help the desktop environment understand what kind of window this is and how to treat it.
        # Default value: gtk.gdk.WINDOW_TYPE_HINT_NORMAL.
        self.type_hint = 'WINDOW_TYPE_HINT_NORMAL'

        # If True the window should be brought to the users attention. Default value: False.
        self.urgency_hint = False

        # The initial position of the window.
        # Default value: WIN_POS_NONE
        self.window_position = 'WIN_POS_NONE'

        ###########################
        # Window Style Properties #
        ###########################

    # GLXC Window Functions
    def new(self):
        """
        Creates a new :func:`GLXCurses.Window <GLXCurses.Window.Window>` instance ready to use.

        :return: the new Window
        :rtype: GLXCurses.Window
        """
        self.__init__()
        return self

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

        # Check widgets to display in side the GLXCurses.Bin
        if bool(self.get_child()):
            self.get_child().set_style(self.get_style())
            self.get_child().draw()

        # Create a box and add the name of the windows like a king, who trust that !!!
        if self.get_decorated():
            self.get_curses_subwin().box()
            if self.get_title():
                self.get_curses_subwin().addstr(
                    0,
                    1,
                    resize_text(self.get_title(), self.get_width() - 2, '~')
                )
        else:
            if self.get_title():
                self.get_curses_subwin().addstr(
                    0,
                    0,
                    resize_text(self.get_title(), self.get_width() - 1, '~')
                )

    # The set_title() method sets the "title" property of the Window to the value specified by title.
    # The title of a window will be displayed in its title bar
    def set_title(self, title):
        if self.get_title() != title:
            self.title = title

    # The get_title() method returns the value of the "title" property of the window. See the set_title() method.
    def get_title(self):
        return self.title

    # The set_wmclass() method sets the X Window System "class" and "name" hints for a window.
    # def set_wmclass(self, wmclass_name, wmclass_class):
    #     pass

    # In combination with the window title,
    # the window role allows a terminal to identify "the same" window when an application is restarted.
    # def set_role(self, role):
    #     pass

    # The get_role() method returns the role of the window. See the set_role() method for further explanation.
    # def get_role(self):
    #     return self.role

    # The add_accel_group() method associates the accelerator group specified by accel_group with the window.
    def add_accel_group(self, accel_group):
        pass

    # The remove_accel_group() method dissociates the accelerator group specified by accel_group from the widget.
    # This method reverses the effects of the add_accel_group() method.
    def remove_accel_group(self, accel_group):
        pass

    def set_position(self, position):
        # The Window Position constants specify hints for initial window placement.
        # WIN_POS_NONE                No influence is made on placement.
        # WIN_POS_CENTER              Windows should be placed in the center of the screen.
        # WIN_POS_MOUSE               Windows should be placed at the current mouse position.
        # WIN_POS_CENTER_ALWAYS       Keep window centered as it changes size, etc.
        # WIN_POS_CENTER_ON_PARENT    Center the window on its transient parent (see the set_transient_for()) method.
        self.window_position = str(position).upper()

    # The activate_focus() method activates the child widget with the focus.
    # This method returns True if the window has a widget with the focus.
    def activate_focus(self):
        if self.get_child().get_has_focus():
            return True
        else:
            return False

    def get_focus(self):
        """
        The get_focus() method returns the current focused widget within the window.

        The focus widget is the widget that would have the focus if the toplevel window is focused.

        :return: The current focused widget
        :rtype: GLXCurses.Widget or None
        """
        if self.get_child().get_has_focus() and self.get_is_focus():
            return self.get_child()
        else:
            return None

    # The set_default() method sets the window's default widget to the value specified by default_widget.
    # If default_widget is None the window's default widget is unset.
    # The default widget is the widget that's activated when the user presses Enter in a window.
    # When setting (rather than unsetting) the default widget
    # it's generally easier to call the grab_default() method on the widget.
    # Before making a widget the default widget, you must set the CAN_DEFAULT
    def set_default(self, default_widget):
        # default_widget , the widget to be the default, or None to unset the default widget.
        if default_widget.get_can_default():
            self.set_has_default(default_widget)
        else:
            self.set_has_default(None)

    # The activate_default() method activates the default widget.
    # If there is no default widget or the default widget cannot be activated,
    # the window's focus widget (if any) is activated.
    # This method returns False if no default widget could be activated or there is no focus widget.
    def activate_default(self):
        if not self.get_child():
            return False
        elif not self.get_child().get_has_default():
            return False
        else:
            return 'sa maman'

    def set_application(self, application=None):
        """
        Set the :class:`Application <GLXCurses.Application.Application>` manager \
        of the :class:`Window <GLXCurses.Window.Window>` widget.

        The :class:`Application <GLXCurses.Application.Application>`, is reponsable of the init \
        of the mainloop, states, and many other thing.

        :class:`Application <GLXCurses.Application.Application>` is a Singleton instance, then normally you'll never \
        have multiple instances of :class:`Application <GLXCurses.Application.Application>`, it \
        method is here for assist :func:`Application.add_window() <GLXCurses.Application.Application.add_window()>` \
        and :func:`Application.remove_window() <GLXCurses.Application.Application.remove_window()>`

        Note if application is None the application will be remove.

        :param application: a Galaxie Curses :class:`Application <GLXCurses.Application.Application>` , as application \
        manager.
        :type   application: GLXCurses.Application or None
        :raise TypeError: if ``application`` parameter is not a \
        :class:`Application <GLXCurses.Application.Application>` type
        """
        if (hasattr(application, 'glxc_type') and application.glxc_type == 'GLXCurses.Application')\
                or (application is None):
            if application != self.get_application():
                self.application = application
        else:
            raise TypeError(u'>application< is not a GLXCurses.Application type')

    def get_application(self):
        """
        Gets the :class:`Application <GLXCurses.Application.Application>` associated with the \
        :class:`Window <GLXCurses.Window.Window>` (if any).

        :return: a Singleton :class:`Application <GLXCurses.Application.Application>` instance, or None
        :rtype: GLXCurses.Application or None
        """
        return self.application
