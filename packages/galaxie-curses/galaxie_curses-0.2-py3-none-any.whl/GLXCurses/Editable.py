#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses.Utils import clamp_to_zero
from GLXCurses.Utils import glxc_type

import pyperclip


class Editable(object):
    def __init__(self):
        self.position = 0
        self.start_pos = None
        self.end_pos = None
        self.is_editable = True

    def select_region(self, editable=None, start_pos=None, end_pos=None):
        """
        Selects a region of text. The characters that are selected are those characters at positions from start_pos
        up to, but not including end_pos . If end_pos is negative, then the characters selected are those characters
        from start_pos to the end of the text.

        Note that positions are specified in characters, not bytes.

        :param editable: a GLXC.Editable
        :type editable: GLXC.Editable or None
        :param start_pos: start of region
        :type start_pos: int or None
        :param end_pos: end of region
        :type end_pos: int or None
        :raise TypeError: if ``start_pos`` is not a int type or None.
        :raise TypeError: if ``end_pos`` is not a int type or None.
        :raise TypeError: if ``editable`` is not a valid GLXCurses type.
        :raise TypeError: if ``editable`` is not a instance of GLXCurses.Editable.
        """
        if editable is None:
            editable = self

        # Try to exit as soon of possible
        if not glxc_type(editable):
            raise TypeError("'editable' must be a GLXCurses type")
        if not isinstance(editable, Editable):
            raise TypeError("'editable' must be an instance of GLXCurses.Editable")
        if type(start_pos) != int and start_pos is not None:
            raise TypeError("'start_pos' must be a int type or None")
        if type(end_pos) != int and end_pos is not None:
            raise TypeError("'end_pos' must be a int type or None")

        if editable.is_editable:
            # care about negative end_pos
            if end_pos is not None:
                if end_pos < 0:
                    end_pos = editable.get_buffer().get_length()

            if start_pos is not None and end_pos is None:
                if editable.start_pos != start_pos:
                    editable.start_pos = start_pos
            elif end_pos is not None and start_pos is None:
                if editable.end_pos != end_pos:
                    editable.end_pos = end_pos
            elif end_pos is not None and start_pos is not None:
                if editable.end_pos != end_pos:
                    editable.end_pos = end_pos
                if editable.start_pos != start_pos:
                    editable.start_pos = start_pos
            else:
                if editable.end_pos is not None:
                    editable.end_pos = None
                if editable.start_pos is not None:
                    editable.start_pos = None

    def get_selection_bounds(self, editable=None):
        """
        Retrieves the selection bound of the editable. start_pos will be filled with the start of the selection and
        end_pos with end. If no text was selected both will be identical and FALSE will be returned.

        Note that positions are specified in characters, not bytes.

        :param editable: a GLXC.Editable
        :type editable: GLXC.Editable or None
        :return: True if an area is selected, False otherwise
        :rtype: bool
        :raise TypeError: if ``editable`` is not a valid GLXCurses type.
        :raise TypeError: if ``editable`` is not a instance of GLXCurses.Editable.
        """
        if editable is None:
            editable = self

        # Try to exit as soon of possible
        if not glxc_type(editable):
            raise TypeError("'editable' must be a GLXCurses type")
        if not isinstance(editable, Editable):
            raise TypeError("'editable' must be an instance of GLXCurses.Editable")

        if editable.start_pos is not None and editable.end_pos is not None:
            return True
        else:
            return False

    def insert_text(self, editable=None, new_text=None, new_text_length=-1, position=None):
        """
        Inserts new_text_length bytes of new_text into the contents of the widget, at position position .

        Note that the position is in characters, not in bytes.

        The function updates position to point after the newly inserted text.

        :param editable: a GLXC.Editable
        :type editable: GLXC.Editable or None
        :param new_text: the text to append
        :type new_text: str
        :param new_text_length: the length of the text in bytes, or -1
        :type new_text_length: int
        :param position: location of the position text will be inserted at. None for insert at actual position.
        :type position: int or None
        :raise TypeError: if ``editable`` is not a valid GLXCurses type.
        :raise TypeError: if ``editable`` is not a instance of GLXCurses.Editable.
        :raise TypeError: if ``new_text`` is not a str or None.
        :raise TypeError: if ``new_text_length`` is not a int or None.
        :raise TypeError: if ``position`` is not a int or None.
        """
        if editable is None:
            editable = self

        # Try to exit as soon of possible
        # check editable
        if not glxc_type(editable):
            raise TypeError("'editable' must be a GLXCurses type")
        if not isinstance(editable, Editable):
            raise TypeError("'editable' must be an instance of GLXCurses.Editable")
        # check new_text
        if type(new_text) != str:
            raise TypeError("'new_text' must be an str type or None")
        # check new_text_length
        if type(new_text_length) != int and new_text_length is not None:
            raise TypeError("'new_text_length' must be an str type or None")
        # check position
        if type(position) != int and position is not None:
            raise TypeError("'position' must be an int type or None")

        if editable.is_editable:
            # delete the selection just because that is like that !!!
            if editable.get_selection_bounds():
                editable.delete_selection()

            if position is not None:
                if editable.get_position() > editable.get_buffer().get_length():
                    if position != editable.get_buffer().get_length():
                        position = editable.get_buffer().get_length()
            else:
                if position != editable.get_position():
                    position = editable.get_position()

            if new_text_length is None or new_text_length < 0:
                if new_text_length != len(new_text):
                    new_text_length = len(new_text)

            editable.get_buffer().insert_text(
                position=position,
                chars=new_text,
                n_chars=new_text_length
            )
            editable.set_position(
                position=position + len(new_text)
            )

    def delete_text(self, editable=None, start_pos=None, end_pos=None):
        """
        Deletes a sequence of characters.
        The characters that are deleted are those characters at positions from start_pos up to,
        but not including end_pos .

        If end_pos is negative, then the characters deleted are those from start_pos to the end of the text.

        :param editable: a GLXC.Editable
        :type editable: GLXC.Editable or None
        :param start_pos: start position
        :type start_pos: int or None
        :param end_pos: end position
        :type end_pos: int or None
        :raise TypeError: if ``editable`` is not a valid GLXCurses type.
        :raise TypeError: if ``editable`` is not a instance of GLXCurses.Editable.
        :raise TypeError: if ``start_pos`` is not a int type or None.
        :raise TypeError: if ``end_pos`` is not a int type or None.
        """
        if editable is None:
            editable = self

        # Try to exit as soon of possible
        if not glxc_type(editable):
            raise TypeError("'editable' must be a GLXCurses type")
        if not isinstance(editable, Editable):
            raise TypeError("'editable' must be an instance of GLXCurses.Editable")
        if type(start_pos) != int and start_pos is not None:
            raise TypeError("'start_pos' must be a int type or None")
        if type(end_pos) != int and end_pos is not None:
            raise TypeError("'end_pos' must be a int type or None")

        if editable.is_editable:
            if start_pos is None:
                if editable.start_pos is None:
                    start_pos = editable.position
                else:
                    start_pos = editable.start_pos

            if end_pos is None:
                end_pos = start_pos

            if end_pos < 0:
                end_pos = editable.get_buffer().get_length()

            if start_pos <= end_pos:
                editable.get_buffer().delete_text(
                    position=start_pos,
                    n_chars=end_pos + 1 - start_pos
                )
            else:
                editable.get_buffer().delete_text(
                    position=end_pos,
                    n_chars=(start_pos - end_pos)
                )

    def get_chars(self, editable=None, start_pos=None, end_pos=None):
        """
        Retrieves a sequence of characters.
        The characters that are retrieved are those characters at positions from start_pos up to, but n
        ot including end_pos .

        If end_pos is negative, then the characters retrieved are those characters
        from start_pos to the end of the text.

        Note that positions are specified in characters, not bytes.

        :param editable: a GLXC.Editable
        :type editable: GLXC.Editable or None
        :param start_pos: start of text
        :type start_pos: int
        :param end_pos: end of text
        :type end_pos: int
        :return: a pointer to the contents of the widget as a string. This string is allocated by the GLXC.Editable \
        implementation and should be freed by the caller.
        :raise TypeError: if ``editable`` is not a valid GLXCurses type.
        :raise ImportError: if ``editable`` is not a instance of GLXCurses.Editable.
        :raise TypeError: if ``start_pos`` is not a int type or None.
        :raise TypeError: if ``end_pos`` is not a int type or None.
        """
        if editable is None:
            editable = self

        # Try to exit as soon of possible
        if not glxc_type(editable):
            raise TypeError("'editable' must be a GLXCurses type")
        if not isinstance(editable, Editable):
            raise ImportError("'editable' must be an instance of GLXCurses.Editable")
        if type(start_pos) != int and start_pos is not None:
            raise TypeError("'start_pos' must be a int type or None")
        if type(end_pos) != int and end_pos is not None:
            raise TypeError("'end_pos' must be a int type or None")

        if start_pos is None:
            start_pos = editable.start_pos
        if end_pos is None:
            end_pos = editable.end_pos

        string_to_return = ""

        if start_pos < end_pos:
            mini = start_pos
            maxi = end_pos
        else:
            mini = end_pos
            maxi = start_pos

        for letter in range(mini, maxi + 1, 1):
            if letter < editable.get_buffer().get_length():
                string_to_return += editable.get_buffer().get_text()[letter]

        # protect password
        if hasattr(editable, 'visibility') and (editable.visibility is False):
            if hasattr(editable, 'invisible_char') and type(editable.invisible_char) == str:
                return editable.invisible_char * len(string_to_return)
            else:
                return '*' * len(string_to_return)
        else:
            return string_to_return

    def cut_clipboard(self, editable=None):
        """
        Removes the contents of the currently selected content in the editable and puts it on the clipboard.

        :param editable: a instance of GLXCurses.Editable.
        :type editable: Editable or None
        :raise TypeError: if ``editable`` is not a valid GLXCurses type.
        :raise TypeError: if ``editable`` is not a instance of GLXCurses.Editable.
        """
        if editable is None:
            editable = self

        # Try to exit as soon of possible
        if not glxc_type(editable):
            raise TypeError("'editable' must be a GLXCurses type")
        if not isinstance(editable, Editable):
            raise ImportError("'editable' must be an instance of GLXCurses.Editable")

        # make the job
        if editable.is_editable:
            if editable.start_pos < editable.end_pos:
                mini = editable.start_pos
                maxi = editable.end_pos
            else:
                mini = editable.end_pos
                maxi = editable.start_pos

            if editable.get_selection_bounds():
                pyperclip.copy(
                    str(
                        editable.get_chars(
                            start_pos=mini,
                            end_pos=maxi
                        )
                    )
                )
                editable.delete_text(
                    start_pos=mini,
                    end_pos=maxi
                )
                editable.select_region()
                # reset the position after the cut
                if editable.get_buffer().get_length() < editable.get_position():
                    editable.set_position(
                        position=editable.get_buffer().get_length()
                    )

    def copy_clipboard(self, editable=None):
        """
        Copies the contents of the currently selected content in the editable and puts it on the clipboard.

        :param editable: a GLXC.Editable
        :type editable: Editable or None
        :raise TypeError: if ``editable`` is not a valid GLXCurses type.
        :raise TypeError: if ``editable`` is not a instance of Editable.
        """
        if editable is None:
            editable = self

        # Try to exit as soon of possible
        if not glxc_type(editable):
            raise TypeError("'editable' must be a GLXCurses type")
        if not isinstance(editable, Editable):
            raise ImportError("'editable' must be an instance of GLXCurses.Editable")

        if editable.get_selection_bounds():

            if editable.start_pos < editable.end_pos:
                mini = editable.start_pos
                maxi = editable.end_pos
            else:
                mini = editable.end_pos
                maxi = editable.start_pos

            pyperclip.copy(
                str(
                    editable.get_chars(
                        start_pos=mini,
                        end_pos=maxi
                    )
                )
            )

    def paste_clipboard(self, editable=None):
        """
        Pastes the content of the clipboard to the current position of the cursor in the editable.

        :param editable: a GLXC.Editable
        :type editable: GLXC.Editable or None
        :raise TypeError: if ``editable`` is not a valid GLXCurses type.
        :raise TypeError: if ``editable`` is not a instance of GLXCurses.Editable.
        """
        if editable is None:
            editable = self

        # Try to exit as soon of possible
        if not glxc_type(editable):
            raise TypeError("'editable' must be a GLXCurses type")
        if not isinstance(editable, Editable):
            raise ImportError("'editable' must be an instance of GLXCurses.Editable")

        if editable.is_editable:
            if editable.get_selection_bounds():
                editable.delete_selection()

            text_from_clipboard = str(pyperclip.paste())

            editable.get_buffer().insert_text(
                position=editable.get_position(),
                chars=text_from_clipboard
            )
            editable.set_position(
                position=editable.get_position() + len(text_from_clipboard)
            )

    def delete_selection(self, editable=None):
        """
        Deletes the currently selected text of the editable.
        This call doesnt do anything if there is no selected text.

        :param editable: a Class Name contain on the list GLXC.Editable
        :type editable: GLXC.Editable
        :raise TypeError: if ``editable`` is not a valid GLXCurses type.
        :raise TypeError: if ``editable`` is not a instance of GLXCurses.Editable.
        """
        if editable is None:
            editable = self

        # Try to exit as soon of possible
        if not glxc_type(editable):
            raise TypeError("'editable' must be a GLXCurses type")
        if not isinstance(editable, Editable):
            raise ImportError("'editable' must be an instance of GLXCurses.Editable")

        if editable.is_editable:
            if editable.get_selection_bounds():

                if editable.start_pos <= editable.end_pos:
                    editable.get_buffer().delete_text(
                        position=editable.start_pos,
                        n_chars=editable.end_pos + 1 - editable.start_pos
                    )
                    editable.set_position(
                        position=editable.start_pos
                    )
                else:
                    editable.get_buffer().delete_text(
                        position=editable.end_pos,
                        n_chars=(editable.start_pos - editable.end_pos)
                    )

                    editable.set_position(
                        position=editable.end_pos
                    )
                editable.select_region()

    def set_position(self, editable=None, position=-1):
        """
        Sets the cursor position in the editable to the given value.

        The cursor is displayed before the character with the given (base 0) index in the contents of the editable.
        The value must be less than or equal to the number of characters in the editable.

        A value of -1 indicates that the position should be set after the last character of the editable.

        Note that position is in characters, not in bytes.

        :param editable: a Class Name contain on the list GLXC.Editable
        :type editable: GLXC.Editable
        :param position: the position of the cursor
        :type position: int
        :raise TypeError: if ``editable`` is not a valid GLXCurses type.
        :raise TypeError: if ``editable`` is not a instance of GLXCurses.Editable.
        :raise TypeError: if ``position`` is not a int type.
        """
        if editable is None:
            editable = self

        # Try to exit as soon of possible
        if not glxc_type(editable):
            raise TypeError("'editable' must be a GLXCurses type")
        if not isinstance(editable, Editable):
            raise TypeError("'editable' must be an instance of GLXCurses.Editable")
        if type(position) != int:
            raise TypeError("'position' must be a int type")

        # make the job
        if editable.is_editable:
            if position == 0:
                estimate_position = 0
            elif position == -1 or position > editable.get_buffer().get_length():
                estimate_position = editable.get_buffer().get_length()
            # elif position > editable.get_buffer().get_length():
            #     estimate_position = editable.get_buffer().get_length()
            # # Normal situation
            else:
                estimate_position = clamp_to_zero(position)

            # in case it have something to do
            if editable.position != estimate_position:
                editable.position = estimate_position

    def get_position(self, editable=None):
        """
        Retrieves the current position of the cursor relative to the start of the content of the editable.

        Note that this position is in characters, not in bytes.

        :param editable: a Class Name contain on the list GLXC.Editable
        :type editable: GLXC.Editable
        :return: the cursor position
        :rtype: int
        :raise TypeError: if ``editable`` is not a valid GLXCurses type.
        :raise TypeError: if ``editable`` is not a instance of GLXCurses.Editable.
        """
        if editable is None:
            editable = self

        # Try to exit as soon of possible
        if not glxc_type(editable):
            raise TypeError("'editable' must be a GLXCurses type")
        if not isinstance(editable, Editable):
            raise ImportError("'editable' must be an instance of GLXCurses.Editable")

        return editable.position

    def set_editable(self, editable=None, is_editable=True):
        """
        Determines if the user can edit the text in the editable widget or not.

        :param editable: a Class Name contain on the list GLXC.Editable
        :type editable: GLXC.Editable
        :param is_editable: True if the user is allowed to edit the text in the widget
        :type is_editable: bool
        :raise TypeError: if ``is_editable`` is not a int type.
        :raise TypeError: if ``editable`` is not a valid GLXCurses type.
        :raise TypeError: if ``editable`` is not a instance of GLXCurses.Editable.
        """
        if editable is None:
            editable = self

        # Try to exit as soon of possible
        if not glxc_type(editable):
            raise TypeError("'editable' must be a GLXCurses type")
        if not isinstance(editable, Editable):
            raise ImportError("'editable' must be an instance of GLXCurses.Editable")
        if type(is_editable) != bool:
            raise TypeError("'is_editable' must be a bool type")

        if editable.is_editable != is_editable:
            editable.is_editable = is_editable

    def get_editable(self, editable=None):
        """
        Retrieves whether editable is editable.

        See GLXCurses.Editable.set_editable().

        :param editable: a Class Name contain on the list GLXC.Editable
        :type editable: GLXC.Editable
        :return: True if editable is editable.
        :raise TypeError: if ``editable`` is not a valid GLXCurses type.
        :raise TypeError: if ``editable`` is not a instance of GLXCurses.Editable.
        """
        if editable is None:
            editable = self

        # Try to exit as soon of possible
        if not glxc_type(editable):
            raise TypeError("'editable' must be a GLXCurses type")
        if not isinstance(editable, Editable):
            raise ImportError("'editable' must be an instance of GLXCurses.Editable")

        return editable.is_editable
