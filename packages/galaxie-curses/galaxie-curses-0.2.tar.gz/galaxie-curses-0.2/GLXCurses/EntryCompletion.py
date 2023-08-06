#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

# Inspired by: https://developer.gnome.org/gtk3/stable/GtkEntryCompletion.html

from GLXCurses import Object
from GLXCurses import GLXC
from GLXCurses.Utils import new_id


class EntryCompletion(Object):
    """
    EntryCompletion — Completion functionality for :func:`GLXCurses.Entry <GLXCurses.Entry.Entry>`
    """

    def __init__(self):
        """
        **Properties**

        .. py:attribute:: inline_completion

           WDetermines whether the common prefix of the possible completions should be inserted automatically in the
           entry. Note that this requires text-column to be set, even if you are using a custom match function.

              :Type: bool
              :Flags: Read / Write
              :Default value: False

        .. py:attribute:: inline_selection

           Determines whether the possible completions on the popup will appear in the entry as you navigate
           through them.

              :Type: bool
              :Flags: Read / Write
              :Default value: False

        .. py:attribute:: minimum_key_length

           Minimum length of the search key in order to look up matches.

              :Type: bool
              :Flags: Read / Write
              :Allowed values: >= 0
              :Default value: 1

        .. py:attribute:: model

           The model to find matches in.

              :Type: TreeModel
              :Flags: Read / Write

        .. py:attribute:: popup_completion

           Determines whether the possible completions should be shown in a popup window.

              :Type: bool
              :Flags: Read / Write
              :Default value: True

        .. py:attribute:: popup_single_match

           Determines whether the completions popup window will shown for a single possible completion.
           You probably want to set this to False if you are using inline completion.

              :Type: bool
              :Flags: Read / Write
              :Default value: True

        .. py:attribute:: text_column

           The column of the model containing the strings. Note that the strings must be UTF-8.

              :Type: int
              :Flags: Read / Write
              :Allowed values: >= -1
              :Default value: -1

        """
        # Load heritage
        Object.__init__(self)

        # It's a GLXCurse Type
        self.glxc_type = 'GLXCurses.EntryCompletion'

        # Widgets can be named, which allows you to refer to them from a GLXCStyle
        self.name = 'EntryCompletion'

        # Unique ID it permit to individually identify a widget by example for get_focus get_default
        self.id = new_id()

        # Widget Setting
        self.set_flags(self.get_default_flags())

        # Property
        self.cell_area = None
        self.inline_completion = False
        self.inline_selection = False
        self.minimum_key_length = 1
        self.model = None
        self.popup_completion = True
        self.popup_set_width = True
        self.popup_single_match = True
        self.text_column = -1

    def new(self):
        """
        Creates a new EntryCompletion.

        :return: A new GLXCurse Entry Completion
        :rtype: GLXCurse.EntryCompletion
        """
        self.__init__()
        return self


