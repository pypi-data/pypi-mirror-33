#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import Container


class Bin(Container):
    """
    The :class:`Bin <GLXCurses.Bin.Bin>` widget is a container with just one child. It is not very useful itself,
    but it is useful for deriving subclasses, since it provides common code needed for handling a single child widget.

    Many GLXCurses widgets are subclasses of :class:`Bin <GLXCurses.Bin.Bin>`, including
     * :class:`Window <GLXCurses.Window.Window>`
     * :class:`Button <GLXCurses.Button.Button>`
     * :class:`Frame <GLXCurses.Frame.Frame>`
     * :class:`HandleBox <GLXCurses.HandleBox.HandleBox>`
     * :class:`ScrolledWindow <GLXCurses.ScrolledWindow.ScrolledWindow>`

    """

    def check_resize(self):
        pass

    def __init__(self):
        # Load heritage
        Container.__init__(self)

        # It's a GLXCurse Type
        self.glxc_type = 'GLXCurses.Bin'

        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.set_name(self.__class__.__name__)

        # Make a Widget Style heritage attribute as local attribute
        if self.get_style().get_attribute_states():
            self.set_attribute_states(self.get_style().get_attribute_states())

    def get_child(self):
        """
        Get the child of the :class:`Bin <GLXCurses.Bin.Bin>`, or :py:obj:`None` if the
        :class:`Bin <GLXCurses.Bin.Bin>` contains no child widget.

        The returned widget does not have a reference added, so you do not need to unref it.

        :return: child widget of the :class:`Bin <GLXCurses.Bin.Bin>`
        :rtype: a GLXCurses object or None
        """
        if bool(self.child):
            return self.child['widget']
        else:
            return None

