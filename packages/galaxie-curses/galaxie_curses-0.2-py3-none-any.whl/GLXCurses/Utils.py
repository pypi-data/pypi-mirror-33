#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

import random
import re


def glxc_type(thing_to_test=None):
    """
    Internal method for check if object pass as argument is GLXCurses Type Object

    :param thing_to_test = A object to test
    :type thing_to_test: object
    :return: True or False
    :rtype: bool
    """
    if hasattr(thing_to_test, 'glxc_type') and (thing_to_test.glxc_type == str(
            'GLXCurses.' + thing_to_test.__class__.__name__)):
        return True
    else:
        return False


def resize_text_wrap_char(text='', max_width=0):
    """
    Resize the text , and return a new text

    example: return '123' for '123456789' where max_width = 3

    :param text: the original text to resize
    :type text: str
    :param max_width: the size of the text
    :type max_width: int
    :return: a resize text
    :rtype: str
    """
    # Try to quit as soon of possible
    if type(text) != str:
        raise TypeError('"text" must be a str type')
    if type(max_width) != int:
        raise TypeError('"max_width" must be a int type')

    # just if it have something to resize
    if max_width < len(text):
        return text[:max_width]
    else:
        return text


def resize_text(text='', max_width=0, separator='~'):
    """
    Resize the text , and return a new text

    example: return '123~789' for '123456789' where max_width = 7 or 8

    :param text: the original text to resize
    :type text: str
    :param max_width: the size of the text
    :type max_width: int
    :param separator: a separator a in middle of the resize text
    :type separator: str
    :return: a resize text
    :rtype: str
    """
    # Try to quit as soon of possible
    if type(text) != str:
        raise TypeError('"text" must be a str type')
    if type(max_width) != int:
        raise TypeError('"max_width" must be a int type')
    if type(separator) != str:
        raise TypeError('"separator" must be a str type')

    # If we are here we haven't quit
    if max_width < len(text):
        if max_width <= 0:
            return str('')
        elif max_width == 1:
            return str(text[:1])
        elif max_width == 2:
            return str(text[:1] + text[-1:])
        elif max_width == 3:
            return str(text[:1] + separator[:1] + text[-1:])
        else:
            max_width -= len(separator[:1])
            max_div = int(max_width / 2)
            return str(text[:max_div] + separator[:1] + text[-max_div:])
    else:
        return str(text)


def clamp_to_zero(value=None):
    """
    Convert any value to positive integer

    :param value: a integer
    :type value: int
    :return: a integer
    :rtype: int
    """
    if type(value) != int and value is not None:
        raise TypeError(u'>value< must be a int or None type')

    if value is None:
        return 0

    if value <= 0:
        return 0
    else:
        return value


def clamp(value=None, smallest=None, largest=None):
    """
    Back ``value`` inside ``smallest`` and ``largest`` value range.

    :param value: The value it have to be clamped
    :param smallest: The lower value
    :param largest: The upper value
    :type value: int or float
    :type value: int or float
    :return: The clamped value it depend of parameters value type, int or float will be preserve.
    :rtype: int or float
    """
    # Try to exit as soon of possible
    if type(value) != int and type(value) != float:
        raise TypeError(u'>value< must be a int or float type')

    if type(smallest) != int and type(smallest) != float:
        raise TypeError(u'>smallest< must be a int or float type')

    if type(largest) != int and type(largest) != float:
        raise TypeError(u'>largest< must be a int or float type')

    # make the job
    if type(value) == int:
        if value < smallest:
            value = smallest
        elif value > largest:
            value = largest
        return int(value)
    elif type(value) == float:
        if value < smallest:
            value = smallest
        elif value > largest:
            value = largest
        return float(value)


def new_id():
    """
    Generate a GLXCurses ID like 'E59E8457', two chars by two chars it's a random HEX

    **Default size:** 8
    **Default chars:** 'ABCDEF0123456789'

    **Benchmark**
       +----------------+---------------+----------------------------------------------+
       | **Iteration**  | **Duration**  | **CPU Information**                          |
       +----------------+---------------+----------------------------------------------+
       | 10000000       | 99.114s       | Intel(R) Core(TM) i7-2860QM CPU @ 2.50GHz    |
       +----------------+---------------+----------------------------------------------+
       | 1000000        | 9.920s        | Intel(R) Core(TM) i7-2860QM CPU @ 2.50GHz    |
       +----------------+---------------+----------------------------------------------+
       | 100000         | 0.998s        | Intel(R) Core(TM) i7-2860QM CPU @ 2.50GHz    |
       +----------------+---------------+----------------------------------------------+
       | 10000          | 0.108s        | Intel(R) Core(TM) i7-2860QM CPU @ 2.50GHz    |
       +----------------+---------------+----------------------------------------------+

    :return: a string it represent a unique ID
    :rtype: str
    """
    return '%02x%02x%02x%02x'.upper() % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )


def is_valid_id(value):
    """
    Check if it's a valid id

    :param value: a id to verify
    :return: bool
    """
    allowed = re.compile(r"""
                         (
                             ^([0-9A-F]{8})$
                         )
                         """,
                         re.VERBOSE | re.IGNORECASE)
    try:
        if allowed.match(value) is None:
            return False
        else:
            return True
    except TypeError:
        return False


def merge_dicts(*dict_args):
    """
    A merge dict fully compatible Python 2 and 3

    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result
