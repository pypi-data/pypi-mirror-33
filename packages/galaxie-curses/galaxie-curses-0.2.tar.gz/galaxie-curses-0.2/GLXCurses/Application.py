#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import GLXC
import GLXCurses
from GLXCurses.EventBusClient import EventBusClient
from GLXCurses.Utils import new_id
from GLXCurses.Utils import glxc_type


import curses
import sys
import os
import locale

# Locales Setting
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


__author__ = 'Tuux'


class Singleton(type):
    def __init__(cls, name, bases, dict):

        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args)
        return cls.instance


# https://developer.gnome.org/gtk3/stable/GtkApplication.html

class EventBus(EventBusClient):
    def __init__(self):
        EventBusClient.__init__(self)

    @staticmethod
    def adopt(orphan):
        """
        not implemented yet

        :param orphan: a poor widget orphan
        """
        pass

    def emit(self, detailed_signal, args=None):
        """
        Emit signal in direction to the Mainloop.

        :param detailed_signal: a string containing the signal name
        :type detailed_signal: str
        :param args: additional parameters arg1, arg2
        :type args: list
        """
        # If args is still None replace it by a empty list
        if args is None:
            args = list()

        # Emit inside the Mainloop
        GLXCurses.mainloop.emit(detailed_signal, args)

    def events_dispatch(self, detailed_signal, args=None):
        if args is None:
            args = []

        # Flush internal event
        self.events_flush(detailed_signal, args)

        if GLXCurses.application.get_active_window():
            GLXCurses.application.get_active_window().events_dispatch(detailed_signal, args)


class Application(EventBus):
    """
    :Description:

    Create a Application singleton instance.

    That class have the role of a Controller and a NCurses Wrapper.

    It have particularity to not be a GLXCurses.Widget, then have a tonne of function for be a fake GLXCurses.Widget.

    From GLXCurses point of view everything start with it component. All widget will be display and store inside it
    component.

    Attributes:
        **active_window** --
        The window which most recently had focus.\n
        Default value: :py:obj:`None`


        **app_menu** --
        The GMenuModel for the application menu.\n
        Default value: :py:obj:`None`


        **menubar** --
        The GMenuModel for the menubar.\n
        Default value: :py:obj:`None`


        **register_session** --
        Set this property to :py:obj:`True` to register with the session manager.\n
        Default value: :py:obj:`False`
    """
    __metaclass__ = Singleton

    def __init__(self):
        """
        Initialize the Curses Screen and all attribute
        :Property's Details:

        .. py:data:: width

            The width size in characters, considered as the hard limit.

              +---------------+-------------------------------+
              | Type          | :py:data:`int`                |
              +---------------+-------------------------------+
              | Flags         | Read / Write                  |
              +---------------+-------------------------------+
              | Default value | 0                             |
              +---------------+-------------------------------+

        .. py:data:: height

            The height size in characters, considered as the hard limit.

              +---------------+-------------------------------+
              | Type          | :py:data:`int`                |
              +---------------+-------------------------------+
              | Flags         | Read / Write                  |
              +---------------+-------------------------------+
              | Default value | 0                             |
              +---------------+-------------------------------+

        .. py:data:: preferred_height

            The preferred height size in characters, considered as the shoft limit.

              +---------------+-------------------------------+
              | Type          | :py:data:`int`                |
              +---------------+-------------------------------+
              | Flags         | Read / Write                  |
              +---------------+-------------------------------+
              | Default value | 0                             |
              +---------------+-------------------------------+

        .. py:data:: preferred_width

            The preferred width size in characters, considered as the shoft limit.

              +---------------+-------------------------------+
              | Type          | :py:data:`int`                |
              +---------------+-------------------------------+
              | Flags         | Read / Write                  |
              +---------------+-------------------------------+
              | Default value | 0                             |
              +---------------+-------------------------------+

        .. py:data:: name

            Name for the widget Application.

              +---------------+-------------------------------+
              | Type          | :py:data:`char`               |
              +---------------+-------------------------------+
              | Flags         | Read / Write                  |
              +---------------+-------------------------------+
              | Default value | Application                   |
              +---------------+-------------------------------+

        .. py:data:: x

            ``x`` location of the ``main_window`` supposed to be the children widgets area, it value can change when a \
            menu is added

              +---------------+-------------------------------+
              | Type          | :py:data:`int`                |
              +---------------+-------------------------------+
              | Flags         | Read / Write                  |
              +---------------+-------------------------------+
              | Default value | 0                             |
              +---------------+-------------------------------+

        .. py:data:: y

            ``y`` location of the ``main_window`` supposed to be the children widgets area, it value can change when a \
            menu is added

              +---------------+-------------------------------+
              | Type          | :py:data:`int`                |
              +---------------+-------------------------------+
              | Flags         | Read / Write                  |
              +---------------+-------------------------------+
              | Default value | 0                             |
              +---------------+-------------------------------+


        """
        EventBus.__init__(self)
        self.glxc_type = 'GLXCurses.Application'
        try:
            # Initialize curses
            # os.environ["NCURSES_NO_UTF8_ACS"] = '1'
            # Make escape key more responsive
            os.environ['ESCDELAY'] = '25'

            # Initialize curses
            self.screen = curses.initscr()

            # Turn off echoing of keys, and enter cbreak mode,
            # where no buffering is performed on keyboard input
            curses.noecho()
            curses.cbreak()

            # use set_input_timeouts to adjust
            curses.halfdelay(10)

            # In keypad mode, escape sequences for special keys
            # (like the cursor keys) will be interpreted and
            # a special value like curses.KEY_LEFT will be returned
            self.screen.keypad(1)

            # accept mouse events
            # curses.mousemask(0
            #                  | curses.BUTTON1_PRESSED | curses.BUTTON1_RELEASED
            #                  | curses.BUTTON2_PRESSED | curses.BUTTON2_RELEASED
            #                  | curses.BUTTON3_PRESSED | curses.BUTTON3_RELEASED
            #                  | curses.BUTTON4_PRESSED | curses.BUTTON4_RELEASED
            #                  | curses.BUTTON1_DOUBLE_CLICKED | curses.BUTTON1_TRIPLE_CLICKED
            #                  | curses.BUTTON2_DOUBLE_CLICKED | curses.BUTTON2_TRIPLE_CLICKED
            #                  | curses.BUTTON3_DOUBLE_CLICKED | curses.BUTTON3_TRIPLE_CLICKED
            #                  | curses.BUTTON4_DOUBLE_CLICKED | curses.BUTTON4_TRIPLE_CLICKED
            #                  | curses.BUTTON_SHIFT | curses.BUTTON_ALT
            #                  | curses.BUTTON_CTRL)
            curses.mousemask(-1)
            curses.mouseinterval(200)
            curses.meta(1)

            # Access ^c before shell does.
            curses.raw()

        except ValueError:
            sys.stdout.write("Curses library not installed defaulting to standard console output\n")
            sys.stdout.write("Error initializing screen.\n")
            sys.stdout.flush()
            self.close()
            sys.exit(1)

        except TypeError:
            sys.stdout.write("Curses library not installed defaulting to standard console output\n")
            sys.stdout.write("Error initializing screen.\n")
            sys.stdout.flush()
            self.close()
            sys.exit(1)

        if not curses.has_colors():
            sys.stdout.write("Your terminal does not support color\n")
            sys.stdout.flush()
            self.close()
            sys.exit(1)
        else:
            curses.start_color()
            curses.use_default_colors()
            self.style = GLXCurses.Style()

        # Curses setting
        self.screen.clear()
        # curses.curs_set(0)
        # curses.mousemask(-1)

        # Store GLXC object
        self.menubar = None
        self.main_window = None
        self.statusbar = None
        self.messagebar = None
        self.toolbar = None

        # Store Variables
        self.name = 'Application'
        self.windows_id_number = None
        self.active_window_id = None
        self.windows = list()
        self.attribute = self.style.get_attribute_states()

        # Controller
        self.widget_it_have_default = {
                'widget': None,
                'type': None,
                'id': None
            }
        self.widget_it_have_focus = {
                'widget': None,
                'type': None,
                'id': None
            }
        self.widget_it_have_tooltip = {
                'widget': None,
                'type': None,
                'id': None
            }

        # Fake Widget
        self.curses_subwin = None
        self.spacing = 0
        self.decorated = 0
        self.screen_height = 0
        self.screen_width = 0
        self.screen_y = 0
        self.screen_x = 0
        self.parent = None
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

        self.parent_spacing = 0
        self.parent_style = self.style

        # Unique ID it permit to individually identify a widget by example for get_focus get_default
        self.id = new_id()

    # Parent
    @staticmethod
    def set_parent(parent=None):
        """
        Suppose to set the parent, but Application haven't any parent, and don't need.
        That method exist for be compatible with a normal Widget.

        :param parent: what you want it will be ignore
        """
        pass

    def get_parent(self):
        """
        Application haven't parent, then return false information's about it parent.

        Return the area object where draw widget , that cover all the area it is not all ready use by \
         MenuBar, ToolBar, MessageBar and StatusBar

        :return: A curses object
        :rtype: <type '_curses.curses window'>
        """
        return self.curses_subwin

    @staticmethod
    def remove_parent():
        """
        The Application have no parent , then that impossible to remove it parent. That function is here for be \
        presented as a true Widget with all functionality.

        It function do nothing
        """
        pass

    def get_parent_size(self):
        """
        Return the size of the main window of the Application. Application haven't any parent then it function return \
        the size of the area dedicated to display widget.

        :return: the size of the main window area X,Y
        :rtype: tuple of int
        """
        return self.get_parent().getmaxyx()

    def get_parent_origin(self):
        """
        Return the origin location of the main window of the Application.
        Application haven't any parent then it function return the origin of the area dedicated to display widget.

        :return: the origin of the main window X,Y
        :rtype: tuple of int
        """
        return self.get_parent().getbegyx()

    def get_parent_spacing(self):
        """
        Return the parent spacing, Application haven't any parent , then it must return the spacing of the Application.

        From Application point of view it function is equivalent to Application.set_spacing()

        :return: The spacing in Character
        :rtype: int
        """
        return self.spacing

    def get_parent_style(self):
        """
        Return the parent Style, Application haven't parent then it return it own Style.
        It function is the top end , after it have noting. The Style will be it Style for everyone

        From Application point of view it function is equivalent to Application.get_style()

        :return: a Galaxie Curses Style
        :rtype: GLXCurses.Style
        """
        return self.style

    # Widget
    def get_curses_subwin(self):
        """
        Return the area object where draw widget , that cover all the area it is not all ready use by \
        MenuBar, ToolBar, MessageBar and StatusBar

        :return: A curses object
        :rtype: <type '_curses.curses window'>
        """
        return self.curses_subwin

    def get_origin(self):
        """
        Return the origin location of the main window of the Application.

        :return: the origin of the area dedicated to display widget. X,Y
        :rtype: tuple of int
        """
        return self.curses_subwin.getbegyx()

    def set_spacing(self, spacing=0):
        """
        Set the Spacing for add a artificial space around Widget's, in that case it will be apply to the Window \
        container added via Application.add_window().

        :param spacing: Spacing in character
        :return: int
        """
        if type(spacing) == int:
            if spacing != self.get_spacing():
                self.spacing = spacing
        else:
            raise TypeError(u'>spacing< argument must be a int type')

    def get_spacing(self):
        """
        Get the Spacing value to apply as artificial space around Widget's, in that case it will be apply to the \
        Window container added via Application.add_window().

        :return: Spacing in character
        :return: int
        """
        return self.spacing

    def set_decorated(self, decorated=0):
        """
        Set if the area main window, will be decorated, that mean have a outer line as decoration.

        :param decorated: 1 if decorated
        :type decorated: int
        """
        if type(decorated) == int:
            if decorated != self.get_decorated():
                self.decorated = decorated
        else:
            raise TypeError(u'>decorated< argument must be a int type')

    def get_decorated(self):
        """
        Return the decorated attribute, in charge to store if the main window area will be decorated.

        :return: True if decorated
        :rtype: bool
        """
        return self.decorated

    def get_screen(self):
        """
        Only Applictaion initialize curses.screen and store it on screen attribute.
        It function return the curses.screen object.

        :return: a Curses Screen, it consist to the entire terminal
        :rtype: curses.curses.screen
        """
        return self.screen

    @staticmethod
    def set_screen(screen):
        """
        The Application have role to initialize the curses.screen, it have no way to change the screen on fly.

        Actually it have no plan for permit to change the default screen for a other one. technically it should be \
        possible. But yet Galaxie Curses is designed for have only Application singleton it use the curses.screen

        It function do nothing
        """
        pass

    # Size management
    def get_width(self):
        """
        Get the :class:`Application <GLXCurses.Application.Application>` :py:obj:`width` property value.

        .. seealso:: \
        :func:`Application.set_width() <GLXCurses.Application.Application.set_width()>`

        :return: :py:obj:`width` property
        :rtype: int
        """
        return self.width

    def set_width(self, width):
        """
        Set the :class:`Application <GLXCurses.Application.Application>` :py:obj:`width` property value.

        .. seealso:: :func:`Application.get_width() <GLXCurses.Application.Application.get_width()>`

        :param width:
        :type width: int
        :raise TypeError: if ``width`` parameter is not a :py:data:`int` type
        """
        if type(width) == int:
            if width != self.get_width():
                self.width = width
                # Can emit signal
        else:
            raise TypeError(u'>width< argument must be a int type')

    def get_height(self):
        """
        Get the :py:obj:`height` property value.

        .. seealso:: \
        :func:`Application.set_height() <GLXCurses.Application.Application.set_height()>`

        :return: :py:obj:`height` property value
        :rtype: int
        """
        return self.height

    def set_height(self, height):
        """
        Set the :py:obj:`height` property.

        .. seealso:: \
        :func:`Application.get_height() <GLXCurses.Application.Application.get_height()>`

        :param height:
        :type height: int
        :raise TypeError: if ``height`` parameter is not a :py:data:`int` type
        """
        if type(height) == int:
            if height != self.get_height():
                self.height = height
                # Can emit signal
        else:
            raise TypeError(u'>height< argument must be a int type')

    def get_preferred_height(self):
        """
        Get the :py:obj:`preferred_height` property.

        .. seealso:: \
        :func:`Application.set_preferred_height() <GLXCurses.Application.Application.set_preferred_height()>`

        :return: :py:obj:`preferred_height` property
        :rtype: int
        """
        return self.preferred_height

    def set_preferred_height(self, preferred_height):
        """
        Set the :py:obj:`preferred_height` property.

        .. seealso:: \
        :func:`Application.set_preferred_height() <GLXCurses.Application.Application.set_preferred_height()>`

        :param preferred_height:
        :type preferred_height: int
        :raise TypeError: if ``preferred_height`` parameter is not a :py:data:`int` type
        """
        if type(preferred_height) == int:
            if preferred_height != self.get_preferred_height():
                self.preferred_height = preferred_height
                # Can emit signal
        else:
            raise TypeError(u'>preferred_height< argument must be a int type')

    def get_preferred_width(self):
        """
        Get the :py:obj:`preferred_width` property.

        .. seealso:: \
        :func:`Application.set_preferred_width() <GLXCurses.Application.Application.preferred_width()>`

        :return: :py:obj:`preferred_width` property
        :rtype: int
        """
        return self.preferred_width

    def set_preferred_width(self, preferred_width):
        """
        Set the :py:obj:`preferred_width` property.

        .. seealso:: \
        :func:`Application.set_preferred_width() <GLXCurses.Application.Application.set_preferred_width()>`

        :param preferred_width:
        :type preferred_width: int
        :raise TypeError: if ``preferred_width`` parameter is not a :py:data:`int` type
        """
        if type(preferred_width) == int:
            if preferred_width != self.get_preferred_width():
                self.preferred_width = preferred_width
                # Can emit signal
        else:
            raise TypeError(u'>preferred_width< argument must be a int type')

    def get_preferred_size(self):
        """
        Return the preferred size of the Application.

        :return: the preferred size
        :rtype: list
        """
        # should preserve the Y X of ncuses ?
        return self.preferred_size

    def set_preferred_size(self, x=0, y=0):
        """
        Set the preferred size, of the Application. It have not big importance for a Application component.
        It here as informal thing.

        :param x: X size in characters
        :type x: int
        :param y: Y size in characters
        :type y: int
        """
        # should preserve the Y X of ncuses ?
        if (type(x) == int) and (type(y) == int):
            if self.preferred_size != [x, y]:
                self.preferred_size = [x, y]
        else:
            raise TypeError(u'>x and y parameters must be int type<')

    def get_size(self):
        """
        Return the size of the main window of the Application.

        :return: the size of the main window area X,Y
        :rtype: tuple of int
        """
        return self.get_curses_subwin().getmaxyx()

    def get_x(self):
        """
        ``x`` location of the ncurses subwin call ``main_window``, it area is use to display a \
        :class:`Window <GLXCurses.Window.Window>`

        :return: ``x`` location in char, 0 correspond to left
        :rtype: int
        """
        return self.x

    def set_x(self, x):
        """
        ``x`` location of the ncurses subwin call ``main_window``, it area is use to display a \
        :class:`Window <GLXCurses.Window.Window>`

        :param x: ``x`` location in char, 0 correspond to left

        """
        if type(x) == int:
            if self.get_x() != x:
                self.x = x
        else:
            raise TypeError(u'>x< parameter is not int type')

    def get_y(self):
        """
        ``y`` location of the ncurses subwin call ``main_window``, it area is use to display a \
        :class:`Window <GLXCurses.Window.Window>`

        :return: ``y`` location in char, 0 correspond to top
        :rtype: int
        """
        return self.y

    def set_y(self, y):
        """
        ``y`` location of the ncurses subwin call ``main_window``, it area is use to display a \
        :class:`Window <GLXCurses.Window.Window>`

        :param y: ``y`` location in char, 0 correspond to top
        :type y: int
        """
        if type(y) == int:
            if self.get_y() != y:
                self.y = y
        else:
            raise TypeError(u'>y< parameter is not int type')

    # GLXCApplication function
    def set_name(self, name):
        """
        Like a widget :class:`Application <GLXCurses.Application.Application>` can be named, which allows you to
        refer to them from config file. You can apply a style to widgets with a particular name.

        .. seealso:: \
        :func:`Application.get_name() <GLXCurses.Application.Application.get_name()>`

        :param name: name for the widget, limit to 256 Char
        :type name: str
        :raise ValueError: if ``name`` argument length is sup to 256 chars
        :raise TypeError: if ``name`` argument length is not a str or unicode type

        """
        if name is not None:
            for character in name:
                if character not in GLXC.Printable:
                    raise TypeError('"name" must be printable string')
        # Check length of name
        if len(name) >= 256:
            raise ValueError(u'>name< argument length must <= 256 chars')

        # And check if value have to be change
        if name != self.get_name():
            self.name = name

    def get_name(self):
        """
        Get the :py:obj:`name` property.

        .. seealso:: \
        :func:`Application.set_name() <GLXCurses.Application.Application.set_name()>`

        :return: :py:obj:`name` property value, type depends about how it have been stored via \
        :func:`Application.set_name() <GLXCurses.Application.Application.set_name()>`
        :rtype: str or unicode
        """
        return self.name

    def set_style(self, style):
        """
        Set the Style, it must be a :class:`Style <GLXCurses.Style.Style>` class, with a valid attribute_states

        .. seealso:: :class:`Style <GLXCurses.Style.Style>`

        :param style: a :class:`Style <GLXCurses.Style.Style>` previously declared
        :type style: GLXCurses.Style
        :raise TypeError: if ``style`` parameter is not a :class:`Style <GLXCurses.Style.Style>` type
        """
        if glxc_type(style):
            if style != self.get_style():
                self.style = style
        else:
            raise TypeError(u'>style< is not a GLXCurses.Style type')

    def get_style(self):
        """
        Return the global Galaxie Curses Style

        .. seealso:: :class:`Style <GLXCurses.Style.Style>`

        :return: a Galaxie Curses Style dictionary
        :rtype: dict
        """
        return self.style

    def add_window(self, window):
        """
        Add a :class:`Window <GLXCurses.Window.Window>` widget to the\
        :class:`Application <GLXCurses.Application.Application>` windows children's list.

        :param window: a window to add
        :type window: GLXCurses.Window
        :raise TypeError: if ``window`` parameter is not a :class:`Window <GLXCurses.Window.Window>` type
        """
        # Check if window is a Galaxie Class
        if glxc_type(window):
            # set the Application it self as parent of the child window
            window.set_parent(self)
            # create a dictionary structure for add it to windows list
            self._add_child_to_windows_list(window)
            # Make the last added element active
            if self.get_active_window() != self._get_windows_list()[-1]['widget']:
                self._set_active_window(self._get_windows_list()[-1]['widget'])
        else:
            raise TypeError(u'>window< is not a GLXCurses.Window type')

    def remove_window(self, window):
        """
        Remove a :class:`Window <GLXCurses.Window.Window>` widget from the\
        :class:`Application <GLXCurses.Application.Application>` windows children's list.

        Set"application" and "parent' attribute of the :func:`GLXCurses.Window <GLXCurses.Window.Window>`
        to :py:obj:`None`.

        :param window: a window to add
        :type window: GLXCurses.Window
        """
        if hasattr(window, 'glxc_type') and window.glxc_type == 'GLXCurses.Window':
            # Detach the children
            window.set_parent(None)
            window.set_application(None)

            # Search for the good window id and delete it from the window list
            count = 0
            last_found = None
            for child in self._get_windows_list():
                if child['id'] == window.get_widget_id():
                    last_found = count
                count += 1

            if last_found is not None:
                self._get_windows_list().pop(last_found)
                if len(self._get_windows_list()) - 1 >= 0:
                    self._set_active_window(self._get_windows_list()[-1]['widget'])
        else:
            raise TypeError(u'>window< is not a GLXCurses.Window type')

    def add_menubar(self, menubar):
        """
        Sets the menubar of application .

        This can only be done in the primary instance of the application, after it has been registered.
        “startup” is a good place to call this.

        :param menubar: a :class:`MenuBar <GLXCurses.MenuBar.MenuBar>`
        :type menubar: GLXCurses.MenuBar
        """
        if glxc_type(menubar):
            menubar.set_parent(self)
            self._set_menubar(menubar)
        else:
            raise TypeError(u'>menubar< is not a GLXCurses.MenuBar')

    def remove_menubar(self):
        """
        Unset the menubar of application
        """
        if self._get_menubar() is not None:
            self._get_menubar().set_parent(None)
        self._set_menubar(None)

    def add_statusbar(self, statusbar):
        """
        Sets the statusbar of application .

        This can only be done in the primary instance of the application, after it has been registered.
        “startup” is a good place to call this.

        :param statusbar: a :class:`StatusBar <GLXCurses.StatusBar.StatusBar>`
        :type statusbar: GLXCurses.StatusBar
        """
        if glxc_type(statusbar):
            statusbar.set_parent(self)
            self._set_statusbar(statusbar)
        else:
            raise TypeError(u'>statusbar< is not a GLXCurses.StatusBar')

    def remove_statusbar(self):
        """
        Unset the statusbar of application
        """
        if self._get_statusbar() is not None:
            self._get_statusbar().set_parent(None)
        self._set_statusbar(None)

    def add_messagebar(self, messagebar):
        """
        Sets the messagebar of application .

        This can only be done in the primary instance of the application, after it has been registered.
        “startup” is a good place to call this.

        :param messagebar: a :class:`MessageBar <GLXCurses.MessageBar.MessageBar>`
        :type messagebar: GLXCurses.MessageBar
        """
        if glxc_type(messagebar):
            messagebar.set_parent(self)
            self._set_messagebar(messagebar)
            self.refresh()
        else:
            raise TypeError(u'>messagebar< is not a GLXCurses.MessageBar')

    def remove_messagebar(self):
        """
        Unset the messagebar of application
        """
        if self._get_messagebar() is not None:
            self._get_messagebar().set_parent(None)
        self._set_messagebar(None)

    def add_toolbar(self, toolbar):
        """
        Sets the toolbar of application .

        This can only be done in the primary instance of the application, after it has been registered.
        “startup” is a good place to call this.

        :param toolbar: a :class:`ToolBar <GLXCurses.ToolBar.ToolBar>`
        :type toolbar: GLXCurses.ToolBar
        """
        if glxc_type(toolbar):
            toolbar.set_parent(self)
            self._set_toolbar(toolbar)
            self.refresh()
        else:
            raise TypeError(u'>toolbar< is not a GLXCurses.ToolBar')

    def remove_toolbar(self):
        """
        Unset the toolbar of application
        """
        if self._get_toolbar() is not None:
            self._get_toolbar().set_parent(None)
        self._set_toolbar(None)

    def refresh(self):
        """
        Refresh the NCurses Screen, and redraw each contain widget's

        It's a central refresh point for the entire application.
        """
        # Clean the screen
        self.get_screen().clear()

        # Calculate the Main Window size
        try:
            self.draw()

            if glxc_type(self._get_menubar()):
                self._get_menubar().draw()

            # Check main curses_subwin to display
            if self.curses_subwin is not None:
                if glxc_type(self.get_active_window()):
                    self.get_active_window().draw()

            if glxc_type(self._get_messagebar()):
                self._get_messagebar().draw()

            if glxc_type(self._get_statusbar()):
                self._get_statusbar().draw()

            if glxc_type(self._get_toolbar()):
                self._get_toolbar().draw()

        except AttributeError:
            pass

        # After have redraw everything it's time to refresh the screen
        self.get_screen().refresh()

    def draw(self):
        """
        Special code for rendering to the screen
        """
        parent_height, parent_width = self.get_screen().getmaxyx()

        menu_bar_height = 0
        message_bar_height = 0
        status_bar_height = 0
        tool_bar_height = 0

        if glxc_type(self._get_menubar()):
            menu_bar_height += 1

        if glxc_type(self._get_messagebar()):
            message_bar_height += 1

        if glxc_type(self._get_statusbar()):
            status_bar_height += 1

        if glxc_type(self._get_toolbar()):
            tool_bar_height += 1

        interface_elements_height = 0
        interface_elements_height += menu_bar_height
        interface_elements_height += message_bar_height
        interface_elements_height += status_bar_height
        interface_elements_height += tool_bar_height

        self.set_height(parent_height - interface_elements_height)
        self.set_width(0)
        self.set_x(0)
        self.set_y(menu_bar_height)
        self.set_preferred_height(self.get_height())
        self.set_preferred_width(self.get_width())

        try:
            self.curses_subwin = self.get_screen().subwin(
                int(self.get_height()),
                int(self.get_width()),
                int(self.get_y()),
                int(self.get_x())
            )
        except curses.error:
            pass

    def getch(self):
        """
        Use by the Mainloop for interact with teh keyboard and the mouse.

        getch() returns an integer corresponding to the key pressed. If it is a normal character, the integer value
        will be equivalent to the character. Otherwise it returns a number which can be matched with the constants
        defined in curses.h.

        For example if the user presses F1, the integer returned is 265.

        This can be checked using the macro KEY_F() defined in curses.h. This makes reading keys portable and easy
        to manage.

        .. code-block:: python

           ch = Application.getch()

        getch() will wait for the user to press a key, (unless you specified a timeout) and when user presses a key,
        the corresponding integer is returned. Then you can check the value returned with the constants defined in
        curses.h to match against the keys you want.

        .. code-block:: python

           if ch == curses.KEY_LEFT
               print("Left arrow is pressed")


        :return: an integer corresponding to the key pressed.
        :rtype: int
        """
        return self.get_screen().getch()

    def close(self):
        """
        A Application must be close properly for permit to Curses to clean up everything and get back the tty \
        in startup condition

        Generally that is follow  by a sys.exit(0) for generate a exit code.
        """
        # Set everything back to normal
        self.get_screen().keypad(False)
        #curses.reset_shell_mode()
        curses.echo()
        curses.nocbreak()
        curses.endwin()


    # Focus and Selection
    def get_default(self):
        """
        Return the unique id of the widget it have been set by \
        :func:`Application.set_default() <GLXCurses.Application.Application.set_default()>`

        .. seealso:: \
         :func:`Application.set_default() <GLXCurses.Application.Application.set_default()>`

         :func:`Widget.get_widget_id() <GLXCurses.Widget.Widget.get_widget_id()>`

        :return: a unique id generate by uuid module
        :rtype: long or None
        """
        return self.widget_it_have_default

    def set_default(self, widget=None):
        """
        The default widget is the widget that’s activated when the user presses Enter in a dialog (for example).

        :param widget: a Widget or None to unset the default widget.
        :type widget: GLXCurses.Widget or None
        """
        if glxc_type(widget):
            info = {
                'widget': widget,
                'type': widget.glxc_type,
                'id': widget.get_widget_id()
            }
            if self.widget_it_have_default != info:
                self.widget_it_have_default = info
        else:
            info = {
                'widget': None,
                'type': None,
                'id': None
            }
            if self.widget_it_have_default != info:
                self.widget_it_have_default = info

    def get_is_focus(self):
        """
        Return the unique id of the widget it have been set by \
        :func:`Application.set_is_focus() <GLXCurses.Application.Application.set_is_focus()>`

        .. seealso:: \
         :func:`Application.set_is_focus() <GLXCurses.Application.Application.set_is_focus()>`

         :func:`Widget.get_widget_id() <GLXCurses.Widget.Widget.get_widget_id()>`

        :return: a unique id generate by uuid module
        :rtype: long or None
        """
        return self.widget_it_have_focus

    def set_is_focus(self, widget=None):
        """
        Determines if the widget is the focus widget within its toplevel. \
        (This does not mean that the “has-focus” property is necessarily set; “has-focus” will only be set \
        if the toplevel widget additionally has the global input focus.)

        .. seealso:: \
        :func:`Application.get_is_focus() <GLXCurses.Application.Application.get_is_focus()>`

        :param widget: a Widget
        :type widget: widget
        """
        if glxc_type(widget):
            info = {
                'widget': widget,
                'type': widget.glxc_type,
                'id': widget.get_widget_id()
            }
            if self.widget_it_have_focus != info:
                self.widget_it_have_focus = info
        else:
            info = {
                'widget': None,
                'type': None,
                'id': None
            }
            if self.widget_it_have_focus != info:
                self.widget_it_have_focus = info

    def get_tooltip(self):
        """
        Return the unique id of the widget it have been set by \
        :func:`Application.set_tooltip() <GLXCurses.Application.Application.set_tooltip()>`

        .. seealso:: \
         :func:`Application.set_tooltip() <GLXCurses.Application.Application.set_tooltip()>`

         :func:`Widget.get_widget_id() <GLXCurses.Widget.Widget.get_widget_id()>`

        :return: a unique id generate by uuid module
        :rtype: long or None
        """
        return self.widget_it_have_tooltip

    def set_tooltip(self, widget=None):
        """
        Determines if the widget have to display a tooltip

        "Not implemented yet"

        .. seealso:: \
        :func:`Application.get_tooltip() <GLXCurses.Application.Application.get_tooltip()>`

        :param widget: a Widget
        :type widget: GLXCurses.Widget or None
        """
        if glxc_type(widget):
            info = {
                'widget': widget,
                'type': widget.glxc_type,
                'id': widget.get_widget_id()
            }
            if self.widget_it_have_tooltip != info:
                self.widget_it_have_tooltip = info
        else:
            info = {
                'widget': None,
                'type': None,
                'id': None
            }
            if self.widget_it_have_tooltip != info:
                self.widget_it_have_tooltip = info

    # Internal

    def _get_windows_list(self):
        """
        Internal method for return self.windows list

        :return: Windows children list
        :rtype: list
        """
        return self.windows

    def _set_windows_list(self, windows_list=list()):
        """
        Internal method for set self.windows list

        :param windows_list: a windows children list
        :type windows_list: list
        """
        if type(windows_list) == list:
            if windows_list != self._get_windows_list():
                self.windows = windows_list
        else:
            raise TypeError(u'>windows_list< is not a int type')

    def _add_child_to_windows_list(self, window):
        """
        Create a dictionary structure for add it to windows list

        :param window: a Window to add on children windows list
        :type window: GLXCurses.Window
        """
        child_property = {

        }

        child_info = {
            'widget': window,
            'type': window.glxc_type,
            'id': window.get_widget_id(),
            'property': child_property
        }

        self._get_windows_list().append(child_info)

    def _set_active_window_id(self, window_id):
        """
        Set the active_window_id attribute

        :param window_id: a uuid generate by Widget
        :type window_id: unicode
        """
        if type(new_id()) != type(window_id):
            raise TypeError(u'>window_id< is not a unicode type')

        if window_id != self._get_active_window_id():
            self.active_window_id = window_id

    def _get_active_window_id(self):
        """
        Return the active_window_id attribute

        :return: active_window_id attribute
        :rtype: unicode
        """
        return self.active_window_id

    def _set_active_window(self, window):
        """
        Set the window widget passed as argument as active

        :param window: a window to add
        :type window: GLXCurses.Window
        :return:
        """
        if window.get_widget_id() != self._get_active_window_id():
            self._set_active_window_id(window.get_widget_id())

    def get_active_window(self):
        """
        Return A :class:`Window <GLXCurses.Window.Window>` widget if any.

        A return to None mean it have no :class:`Window <GLXCurses.Window.Window>` to display

        :return: A :class:`Window <GLXCurses.Window.Window>` widget if any or None
        :rtype: GLXCurses.Window or None
        """
        # Search for the good window id to display
        windows_to_display = None
        for child in self._get_windows_list():
            if child['id'] == self._get_active_window_id():
                windows_to_display = child['widget']

        # If a active window is found
        if windows_to_display is not None:
            return windows_to_display
        else:
            return None

    def _set_menubar(self, menubar=None):
        """
        Set the menubar attribute

        :param menubar: A :class:`MenuBar <GLXCurses.MenuBar.MenuBar>` or None
        :type menubar: GLXCurses.MenuBar or None
        """
        if glxc_type(menubar) or menubar is None:
            if self.menubar != menubar:
                self.menubar = menubar
        else:
            raise TypeError(u'>menubar< is not a GLXCurses.MenuBar or None type')

    def _get_menubar(self):
        """
        Return menubar attribute

        :return: A :class:`MenuBar <GLXCurses.MenuBar.MenuBar>`
        :rtype: GLXCurses.MenuBar or None
        """
        return self.menubar

    def _set_messagebar(self, messagebar=None):
        """
        Set the messagebar attribute

        :param messagebar: A :class:`MessageBar <GLXCurses.MessageBar.MessageBar>` or None
        :type messagebar: GLXCurses.MessageBar or None
        """
        if glxc_type(messagebar) or messagebar is None:
            if self.messagebar != messagebar:
                self.messagebar = messagebar
        else:
            raise TypeError(u'>messagebar< is not a GLXCurses.MessageBar or None type')

    def _get_messagebar(self):
        """
        Return messagebar attribute

        :return: A :class:`MessageBar <GLXCurses.MessageBar.MessageBar>`
        :rtype: GLXCurses.MessageBar or None
        """
        return self.messagebar

    def _set_statusbar(self, statusbar=None):
        """
        Set the statusbar attribute

        :param statusbar: A :class:`StatusBar <GLXCurses.StatusBar.StatusBar>` or None
        :type statusbar: GLXCurses.StatusBar or None
        """
        if glxc_type(statusbar) or statusbar is None:
            if self.statusbar != statusbar:
                self.statusbar = statusbar
        else:
            raise TypeError(u'>menubar< is not a GLXCurses.StatusBar or None type')

    def _get_statusbar(self):
        """
        Return statusbar attribute

        :return: A :class:`StatusBar <GLXCurses.StatusBar.StatusBar>`
        :rtype: GLXCurses.StatusBar or None
        """
        return self.statusbar

    def _set_toolbar(self, toolbar=None):
        """
        Set the toolbar attribute

        :param toolbar: A :class:`ToolBar <GLXCurses.ToolBar.ToolBar>` or None
        :type toolbar: GLXCurses.ToolBar or None
        """
        if glxc_type(toolbar) or toolbar is None:
            if self.toolbar != toolbar:
                self.toolbar = toolbar
        else:
            raise TypeError(u'>toolbar< is not a GLXCurses.ToolBar or None type')

    def _get_toolbar(self):
        """
        Return toolbar attribute

        :return: A :class:`ToolBar <GLXCurses.ToolBar.ToolBar>`
        :rtype: GLXCurses.ToolBar or None
        """
        return self.toolbar
