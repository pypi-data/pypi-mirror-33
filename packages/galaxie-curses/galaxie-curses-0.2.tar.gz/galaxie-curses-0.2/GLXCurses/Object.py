#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import EventBusClient


# Ref Doc: https://developer.gnome.org/gobject/stable/gobject-The-Base-Object-Type.html#GObject-struct
class Object(EventBusClient):
    """
    :Description:

    Object is the fundamental type providing the common attributes and methods for all object types in GLXCurses.

    The Object class provides methods for object construction and destruction, property access methods, and signal
    support.

    Signals are described in detail here.

    """
    def __init__(self):
        EventBusClient.__init__(self)
        self.glxc_type = 'GLXCurses.Object'

        # Signal
        # self.signal_handlers = dict()
        # self.blocked_handler = list()
        # self.blocked_function = list()
        # self.data = dict()
        self.children = list()
        # init
        self.flags = self.get_default_flags()

    def set_flags(self, flags):
        """
        Set the ``flags`` attribute, it consist to a dictionary with keys if have special name.

        see: Object.get_default_flags() for get a default flags.

        :param flags: a Dictionary with Galaxie Curses Object Flags format
        :type flags: dict
        """
        valid_flags = ['IN_DESTRUCTION',
                       'FLOATING',
                       'TOPLEVEL',
                       'NO_WINDOW',
                       'REALIZED',
                       'MAPPED',
                       'VISIBLE',
                       'SENSITIVE',
                       'PARENT_SENSITIVE',
                       'CAN_FOCUS',
                       'HAS_FOCUS',
                       'CAN_DEFAULT',
                       'HAS_DEFAULT',
                       'HAS_GRAB',
                       'RC_STYLE',
                       'COMPOSITE_CHILD',
                       'NO_REPARENT',
                       'APP_PAINTABLE',
                       'RECEIVES_DEFAULT',
                       'DOUBLE_BUFFERED'
                       ]

        # Try to found a way to not be execute
        # Check first level dictionary
        if type(flags) == dict:
            # For each key's
            for key in valid_flags:
                # Check key in the dictionary
                try:
                    flags[key]
                except KeyError:
                    raise KeyError(u'>flags< is not a Galaxie Curses Object flags')
        else:
            raise TypeError(u'>flags< is not a Galaxie Curses Object flags')

        # If it haven't quit that ok
        if flags != self.get_flags():
            self.flags = flags

    def get_flags(self):
        """
        Return the ``flags`` attribute, it consist to a dictionary it store keys with have special name.

        :return: a Dictionary with Galaxie Curses Object Flags format
        :rtype: dict
        """
        return self.flags

    @staticmethod
    def get_default_flags():
        flags = dict()

        # The object is currently being destroyed.
        flags['IN_DESTRUCTION'] = False

        # The object is orphaned.
        flags['FLOATING'] = True

        # Widget flags
        # widgets without a real parent (e.g. Window and Menu) have this flag set throughout their lifetime.
        flags['TOPLEVEL'] = False

        # A widget that does not provide its own Window.
        # Visible action (e.g. drawing) is performed on the parent's Window.
        flags['NO_WINDOW'] = True

        # The widget has an associated Window.
        flags['REALIZED'] = False

        # The widget can be displayed on the screen.
        flags['MAPPED'] = False

        # The widget will be mapped as soon as its parent is mapped.
        flags['VISIBLE'] = True

        # The sensitivity of a widget determines whether it will receive certain events (e.g. button or key presses).
        # One requirement for the widget's sensitivity is to have this flag set.
        flags['SENSITIVE'] = True

        # This is the second requirement for the widget's sensitivity.
        # Once a widget has SENSITIVE and PARENT_SENSITIVE set, its state is effectively sensitive.
        flags['PARENT_SENSITIVE'] = True

        # The widget is able to handle focus grabs.
        flags['CAN_FOCUS'] = True

        # The widget has the focus - assumes that CAN_FOCUS is set
        flags['HAS_FOCUS'] = True

        # The widget is allowed to receive the default action.
        flags['CAN_DEFAULT'] = True

        # The widget currently will receive the default action.
        flags['HAS_DEFAULT'] = False

        # The widget is in the grab_widgets stack, and will be the preferred one for receiving events.
        flags['HAS_GRAB'] = False

        # The widgets style has been looked up through the RC mechanism.
        # It does not imply that the widget actually had a style defined through the RC mechanism.
        flags['RC_STYLE'] = 'Default.yml'

        # The widget is a composite child of its parent.
        flags['COMPOSITE_CHILD'] = False

        # unused
        flags['NO_REPARENT'] = 'unused'

        # Set on widgets whose window the application directly draws on,
        # in order to keep GLXCurse from overwriting the drawn stuff.
        flags['APP_PAINTABLE'] = False

        # The widget when focused will receive the default action and have HAS_DEFAULT set
        # even if there is a different widget set as default.
        flags['RECEIVES_DEFAULT'] = False

        # Exposes done on the widget should be double-buffered.
        flags['DOUBLE_BUFFERED'] = False

        return flags

    def unset_flags(self):
        """
        Back to default flags by call Object.get_default_flags()

        """
        self.set_flags(self.get_default_flags())

    def destroy(self):
        """Destroy the object"""
        self.get_flags()['IN_DESTRUCTION'] = True


