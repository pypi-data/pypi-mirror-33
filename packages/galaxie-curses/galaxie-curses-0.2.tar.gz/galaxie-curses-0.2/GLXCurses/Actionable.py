#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved


class Actionable(object):
    """
    Actionable — An interface for widgets that can be associated with actions

    **Known Implementations**
        Actionable is implemented by GLXC.Actionable and contain a list of widget
           Button,
           CheckButton,
           CheckMenuItem,
           ColorButton,
           FontButton,
           ImageMenuItem,
           LinkButton,
           ListBoxRow,
           LockButton,
           MenuButton,
           MenuItem,
           MenuToolButton,
           ModelButton,
           RadioButton,
           RadioMenuItem,
           RadioToolButton,
           ScaleButton,
           SeparatorMenuItem,
           Switch,
           TearoffMenuItem,
           ToggleButton,
           ToggleToolButton,
           ToolButton,
           VolumeButton.
    """

    def __init__(self):
        """
        :Attributes Details:

        .. py:attribute:: action_name

          The name of the associated action, like 'app.quit'.

             +---------------+-------------------------------+
             | Type          | :py:data:`action_name`        |
             +---------------+-------------------------------+
             | Flags         | Read / Write                  |
             +---------------+-------------------------------+
             | Default value | None                          |
             +---------------+-------------------------------+

        .. py:attribute:: action_target

          The parameter for action invocations.

             +---------------+-------------------------------+
             | Type          | :py:data:`action_name`        |
             +---------------+-------------------------------+
             | Flags         | Read / Write                  |
             +---------------+-------------------------------+
             | Default value | None                          |
             +---------------+-------------------------------+

        """
        self.action_name = None
        self.action_target = None

    def get_action_name(self):
        """
        Gets the action name for ``actionable`` .

        See set_action_name() for more information.

        :return: the action name, or None if unset.
        :rtype: str or None
        """
        return self.action_name

    def set_action_name(self, action_name=None):
        """

        :param action_name: an action name, or None.
        :type action_name: str or None
        :raise TypeError: if ``action_name`` is not a str type or None
        """
        if action_name is not None and type(action_name) != str:
            raise TypeError("'action_name' must be a str type or None")

        if self.action_name != action_name:
            self.action_name = action_name

