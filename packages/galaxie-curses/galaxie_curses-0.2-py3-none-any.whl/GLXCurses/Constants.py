#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

# Inspired by: http://code.activestate.com/recipes/65207-constants-in-python/?in=user-97991


class Constants(object):
    """
    **GLXC.BaselinePosition**

    Whenever a container has some form of natural row it may align children in that row along a common
    typographical baseline. If the amount of vertical space in the row is taller than the total requested
    height of the baseline-aligned children then it can use a GLXC.BaselinePosition to select where
    to put the baseline inside the extra available space.

    Members:
        GLXC.BASELINE_POSITION_TOP: Align the baseline at the top
        GLXC.BASELINE_POSITION_CENTER: Center the baseline
        GLXC.BASELINE_POSITION_BOTTOM: Align the baseline at the bottom
    """

    class ConstError(TypeError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't rebind const(%s)" % name)
        self.__dict__[name] = value

    def __getattr__(self, name):
        if name not in self.__dict__:
            raise self.ConstError("No attribute %s exist" % name)
        return self.__dict__[name]


#############################
# Variables
#############################
GLXC = Constants()

# Inspired by: https://developer.gnome.org/gtk3/stable/gtk3-Standard-Enumerations.html
####################
# BaselinePosition #
####################
# Whenever a container has some form of natural row it may align children in that row along a common
# typographical baseline. If the amount of vertical space in the row is taller than the total requested
# height of the baseline-aligned children then it can use a GLXC.BaselinePosition to select where
# to put the baseline inside the extra available space.

# Align the baseline at the top
GLXC.BASELINE_POSITION_TOP = 'TOP'

# Center the baseline
GLXC.BASELINE_POSITION_CENTER = 'CENTER'

# Align the baseline at the bottom
GLXC.BASELINE_POSITION_BOTTOM = 'BOTTOM'

# Final List
GLXC.BaselinePosition = [
    GLXC.BASELINE_POSITION_TOP,
    GLXC.BASELINE_POSITION_CENTER,
    GLXC.BASELINE_POSITION_BOTTOM
]

##############
# DeleteType #
##############

# Delete characters.
GLXC.DELETE_CHARS = 'CHARS'

# Delete only the portion of the word to the left/right of cursor if we’re in the middle of a word.
GLXC.DELETE_WORD_ENDS = 'WORD_ENDS'

# Delete words.
GLXC.DELETE_WORDS = 'WORDS'

# Delete display-lines. Display-lines refers to the visible lines, with respect to to the current line breaks.
# As opposed to paragraphs, which are defined by line breaks in the input.
GLXC.DELETE_DISPLAY_LINES = 'DISPLAY_LINES'

# Delete only the portion of the display-line to the left/right of cursor.
GLXC.DELETE_DISPLAY_LINE_ENDS = 'DISPLAY_LINE_ENDS'

# Delete to the end of the paragraph. Like C-k in Emacs (or its reverse).
GLXC.DELETE_PARAGRAPH_ENDS = 'PARAGRAPH_ENDS'

# Delete entire line. Like C-k in pico.
GLXC.DELETE_PARAGRAPHS = 'PARAGRAPHS'

# Delete only whitespace. Like M-\ in Emacs.
GLXC.DELETE_WHITESPACE = 'WHITESPACE'

# Final List
GLXC.DeleteType = [
    GLXC.DELETE_CHARS,
    GLXC.DELETE_WORD_ENDS,
    GLXC.DELETE_WORDS,
    GLXC.DELETE_DISPLAY_LINES,
    GLXC.DELETE_DISPLAY_LINE_ENDS,
    GLXC.DELETE_PARAGRAPH_ENDS,
    GLXC.DELETE_PARAGRAPHS,
    GLXC.DELETE_WHITESPACE
]

#################
# DirectionType #
#################
# Focus movement types.

# Move forward.
GLXC.DIR_TAB_FORWARD = 'TAB_FORWARD'

# Move backward.
GLXC.DIR_TAB_BACKWARD = 'TAB_BACKWARD'

# Move up.
GLXC.DIR_UP = 'UP'

# Move down.
GLXC.DIR_DOWN = 'DOWN'

# Move left.
GLXC.DIR_LEFT = 'LEFT'

# Move right.
GLXC.DIR_RIGHT = 'RIGHT'

# Final List
GLXC.DirectionType = [
    GLXC.DIR_TAB_FORWARD,
    GLXC.DIR_TAB_BACKWARD,
    GLXC.DIR_UP,
    GLXC.DIR_DOWN,
    GLXC.DIR_LEFT,
    GLXC.DIR_RIGHT
]

#################
# Justification #
#################
# The text is placed at the left edge of the label.
GLXC.JUSTIFY_LEFT = 'LEFT'

# The text is placed at the right edge of the label.
GLXC.JUSTIFY_RIGHT = 'RIGHT'

# The text is placed in the center of the label.
GLXC.JUSTIFY_CENTER = 'CENTER'

# The text is placed is distributed across the label.
GLXC.JUSTIFY_FILL = 'FILL'

# Set the final list
GLXC.Justification = [
    GLXC.JUSTIFY_LEFT,
    GLXC.JUSTIFY_CENTER,
    GLXC.JUSTIFY_RIGHT,
    GLXC.JUSTIFY_FILL
]

#################
# MovementStep #
#################

# Move forward or back by graphemes
GLXC.MOVEMENT_LOGICAL_POSITIONS = 'LOGICAL_POSITIONS'

# Move left or right by graphemes
GLXC.MOVEMENT_VISUAL_POSITIONS = 'VISUAL_POSITIONS'

# Move forward or back by words
GLXC.MOVEMENT_WORDS = 'WORDS'

# Move up or down lines (wrapped lines)
GLXC.MOVEMENT_DISPLAY_LINES = 'DISPLAY_LINES'

# Move to either end of a line
GLXC.MOVEMENT_DISPLAY_LINE_ENDS = 'DISPLAY_LINE_ENDS'

# Move up or down paragraphs (newline-ended lines)
GLXC.MOVEMENT_PARAGRAPHS = 'PARAGRAPHS'

# Move to either end of a paragraph
GLXC.MOVEMENT_PARAGRAPH_ENDS = 'PARAGRAPH_ENDS'

# Move by pages
GLXC.MOVEMENT_PAGES = 'PAGES'

# Move to ends of the buffer
GLXC.MOVEMENT_BUFFER_ENDS = 'BUFFER_ENDS'

# Move horizontally by pages
GLXC.MOVEMENT_HORIZONTAL_PAGES = 'HORIZONTAL_PAGES'

# Set Final list
GLXC.MovementStep = [
    GLXC.MOVEMENT_LOGICAL_POSITIONS,
    GLXC.MOVEMENT_VISUAL_POSITIONS,
    GLXC.MOVEMENT_WORDS,
    GLXC.MOVEMENT_DISPLAY_LINES,
    GLXC.MOVEMENT_DISPLAY_LINE_ENDS,
    GLXC.MOVEMENT_PARAGRAPHS,
    GLXC.MOVEMENT_PARAGRAPH_ENDS,
    GLXC.MOVEMENT_PAGES,
    GLXC.MOVEMENT_BUFFER_ENDS,
    GLXC.MOVEMENT_HORIZONTAL_PAGES
]

###################
# Orientation     #
###################
# Represents the orientation of widgets and other objects which can be switched between
# horizontal and vertical orientation on the fly, like ToolBar

# The element is in horizontal orientation.
GLXC.ORIENTATION_HORIZONTAL = 'HORIZONTAL'

# The element is in vertical orientation.
GLXC.ORIENTATION_VERTICAL = 'VERTICAL'

# Set the Final list
GLXC.Orientation = [
    GLXC.ORIENTATION_HORIZONTAL,
    GLXC.ORIENTATION_VERTICAL
]

################
# PackType     #
################
# Represents the packing location Box children. (See: VBox, HBox, and ButtonBox).

# The child is packed into the start of the box
GLXC.PACK_START = 'START'

# The child is packed into the end of the box
GLXC.PACK_END = 'END'

# Set the final list
GLXC.PackType = [
    GLXC.PACK_START,
    GLXC.PACK_END
]

#################
#  PositionType #
#################
# Describes which edge of a widget a certain feature is positioned

# The feature is at the left edge.
GLXC.POS_LEFT = 'LEFT'

# The feature is at the right edge.
GLXC.POS_RIGHT = 'RIGHT'

# The feature is at the center.
GLXC.POS_CENTER = 'CENTER'

# The feature is at the top edge.
GLXC.POS_TOP = 'TOP'

# The feature is at the bottom edge.
GLXC.POS_BOTTOM = 'BOTTOM'

# Set the final list
GLXC.PositionType = [
    GLXC.POS_LEFT,
    GLXC.POS_RIGHT,
    GLXC.POS_CENTER,
    GLXC.POS_TOP,
    GLXC.POS_BOTTOM
]

######################
# Relief ReliefStyle #
######################
# Indicated the relief to be drawn around a Button.

# Draw a normal relief.
GLXC.RELIEF_NORMAL = 'NORMAL'

# A half relief.
GLXC.RELIEF_HALF = 'HALF'

# No relief.
GLXC.RELIEF_NONE = 'NONE'

# Set the final list
GLXC.ReliefStyle = [
    GLXC.RELIEF_NORMAL,
    GLXC.RELIEF_HALF,
    GLXC.RELIEF_NONE
]

##############
# ScrollStep #
##############

# Scroll in steps.
GLXC.SCROLL_STEPS = 'STEPS'

# Scroll by pages.
GLXC.SCROLL_PAGES = 'PAGES'

# Scroll to ends.
GLXC.SCROLL_ENDS = 'ENDS'

# Scroll in horizontal steps.
GLXC.SCROLL_HORIZONTAL_STEPS = 'HORIZONTAL_STEPS'

# Scroll by horizontal pages.
GLXC.SCROLL_HORIZONTAL_PAGES = 'HORIZONTAL_PAGES'

# Scroll to the horizontal ends.
GLXC.SCROLL_HORIZONTAL_ENDS = 'HORIZONTAL_ENDS'

# Set the Final List
GLXC.ScrollStep = [
    GLXC.SCROLL_STEPS,
    GLXC.SCROLL_PAGES,
    GLXC.SCROLL_ENDS,
    GLXC.SCROLL_HORIZONTAL_STEPS,
    GLXC.SCROLL_HORIZONTAL_PAGES,
    GLXC.SCROLL_HORIZONTAL_ENDS
]

##############
# ScrollType #
##############
# Scrolling types.

# No scrolling.
GLXC.SCROLL_NONE = 'NONE'

# Jump to new location.
GLXC.SCROLL_JUMP = 'JUMP'

# Step backward.
GLXC.SCROLL_STEP_BACKWARD = 'STEP_BACKWARD'

# Step forward.
GLXC.SCROLL_STEP_FORWARD = 'STEP_FORWARD'

# Page backward.
GLXC.SCROLL_PAGE_BACKWARD = 'PAGE_BACKWARD'

# Page forward.
GLXC.SCROLL_PAGE_FORWARD = 'PAGE_FORWARD'

# Step up.
GLXC.SCROLL_STEP_UP = 'STEP_UP'

# Step down.
GLXC.SCROLL_STEP_DOWN = 'STEP_DOWN'

# Page up.
GLXC.SCROLL_PAGE_UP = 'PAGE_UP'

# Page down.
GLXC.SCROLL_PAGE_DOWN = 'PAGE_DOWN'

# Step to the left.
GLXC.SCROLL_STEP_LEFT = 'STEP_LEFT'

# Step to the right.
GLXC.SCROLL_STEP_RIGHT = 'STEP_RIGHT'

# Page to the left.
GLXC.SCROLL_PAGE_LEFT = 'PAGE_LEFT'

# Page to the right.
GLXC.SCROLL_PAGE_RIGHT = 'PAGE_RIGHT'

# Scroll to start.
GLXC.SCROLL_START = 'START'

# Scroll to end.
GLXC.SCROLL_END = 'END'

# Set the final list
GLXC.ScrollType = [
    GLXC.SCROLL_NONE,
    GLXC.SCROLL_JUMP,
    GLXC.SCROLL_STEP_BACKWARD,
    GLXC.SCROLL_STEP_FORWARD,
    GLXC.SCROLL_PAGE_BACKWARD,
    GLXC.SCROLL_PAGE_FORWARD,
    GLXC.SCROLL_STEP_UP,
    GLXC.SCROLL_STEP_DOWN,
    GLXC.SCROLL_PAGE_UP,
    GLXC.SCROLL_PAGE_DOWN,
    GLXC.SCROLL_STEP_LEFT,
    GLXC.SCROLL_STEP_RIGHT,
    GLXC.SCROLL_PAGE_LEFT,
    GLXC.SCROLL_PAGE_RIGHT,
    GLXC.SCROLL_START,
    GLXC.SCROLL_END
]

#################
# SelectionMode #
#################
# Used to control what selections users are allowed to make.

# No selection is possible.
GLXC.SELECTION_NONE = 'NONE'

# Zero or one element may be selected.
GLXC.SELECTION_SINGLE = 'SINGLE'

# Exactly one element is selected. In some circumstances,
# such as initially or during a search operation, it’s possible for
# no element to be selected with GLXC.SELECTION_BROWSE.
# What is really enforced is that the user can’t deselect a
# currently selected element except by selecting another element.
GLXC.SELECTION_BROWSE = 'BROWSE'

# Any number of elements may be selected. The Ctrl key may
# be used to enlarge the selection, and Shift key to select
# between the focus and the child pointed to. Some widgets
# may also allow Click-drag to select a range of elements.
GLXC.SELECTION_MULTIPLE = 'MULTIPLE'

# Set the final list
GLXC.SelectionMode = [
    GLXC.SELECTION_NONE,
    GLXC.SELECTION_SINGLE,
    GLXC.SELECTION_BROWSE,
    GLXC.SELECTION_MULTIPLE
]

##############
# ShadowType #
##############
# The Shadow Type constants specify the appearance of an outline typically provided by a Frame.

# No outline
GLXC.SHADOW_NONE = 'NONE'
# The outline is beveled inward.
GLXC.SHADOW_IN = 'IN'
# The outline is beveled outward like a button.
GLXC.SHADOW_OUT = 'OUT'
# The outline itself is an inward bevel, but the frame bevels outward
GLXC.SHADOW_ETCHED_IN = 'ETCHED_IN'
# The outline itself is an outward bevel, but the frame bevels inward
GLXC.SHADOW_ETCHED_OUT = 'ETCHED_OUT'
# Set the final list
GLXC.ShadowType = [
    GLXC.SHADOW_NONE,
    GLXC.SHADOW_IN,
    GLXC.SHADOW_OUT,
    GLXC.SHADOW_ETCHED_IN,
    GLXC.SHADOW_ETCHED_OUT
]

##############
# StateFlags #
##############

# State during normal operation.
GLXC.STATE_FLAG_NORMAL = 'NORMAL'

# Widget is active.
GLXC.STATE_FLAG_ACTIVE = 'ACTIVE'

# Widget has a mouse pointer over it.
GLXC.STATE_FLAG_PRELIGHT = 'PRELIGHT'

# Widget is selected.
GLXC.STATE_FLAG_SELECTED = 'SELECTED'

# Widget is insensitive.
GLXC.STATE_FLAG_INSENSITIVE = 'INSENSITIVE'

# Widget is inconsistent.
GLXC.STATE_FLAG_INCONSISTENT = 'INCONSISTENT'

# Widget has the keyboard focus.
GLXC.STATE_FLAG_FOCUSED = 'FOCUSED'

# Widget is in a background top level window.
GLXC.STATE_FLAG_BACKDROP = 'BACKDROP'

# Widget is in left-to-right text direction.
GLXC.STATE_FLAG_DIR_LTR = 'DIR_LTR'

# Widget is in right-to-left text direction.
GLXC.STATE_FLAG_DIR_RTL = 'DIR_RTL'

# Widget is a link.
GLXC.STATE_FLAG_LINK = 'LINK'

# The location the widget points to has already been visited.
GLXC.STATE_FLAG_VISITED = 'VISITED'

# Widget is checked.
GLXC.STATE_FLAG_CHECKED = 'CHECKED'

# Widget is highlighted as a drop target for DND.
GLXC.STATE_FLAG_DROP_ACTIVE = 'DROP_ACTIVE'

# Set the final list
GLXC.StateFlags = [
    GLXC.STATE_FLAG_NORMAL,
    GLXC.STATE_FLAG_ACTIVE,
    GLXC.STATE_FLAG_PRELIGHT,
    GLXC.STATE_FLAG_SELECTED,
    GLXC.STATE_FLAG_INSENSITIVE,
    GLXC.STATE_FLAG_INCONSISTENT,
    GLXC.STATE_FLAG_FOCUSED,
    GLXC.STATE_FLAG_BACKDROP,
    GLXC.STATE_FLAG_DIR_LTR,
    GLXC.STATE_FLAG_DIR_RTL,
    GLXC.STATE_FLAG_LINK,
    GLXC.STATE_FLAG_VISITED,
    GLXC.STATE_FLAG_CHECKED,
    GLXC.STATE_FLAG_DROP_ACTIVE
]

################
# ToolbarStyle #
################
# Used to customize the appearance of a Toolbar. Note that setting the toolbar style overrides the user’s preferences
# for the default toolbar style. Note that if the button has only a label set and GLXC.TOOLBAR_ICONS is used, the label
# will be visible, and vice versa.

# Buttons display only icons in the toolbar.
GLXC.TOOLBAR_ICONS = 'ICONS'

# Buttons display only text labels in the toolbar.
GLXC.TOOLBAR_TEXT = 'TEXT'

# Buttons display text and icons in the toolbar.
GLXC.TOOLBAR_BOTH = 'BOTH'

# Buttons display icons and text alongside each other, rather than vertically stacked
GLXC.TOOLBAR_BOTH_HORIZ = 'BOTH_HORIZ'

# Set the Final list
GLXC.ToolbarStyle = [
    GLXC.TOOLBAR_ICONS,
    GLXC.TOOLBAR_TEXT,
    GLXC.TOOLBAR_BOTH,
    GLXC.TOOLBAR_BOTH_HORIZ
]

############
# SortType #
############
# Determines the direction of a sort.
# Sorting is in ascending order.
GLXC.SORT_ASCENDING = 'ASCENDING'

# Sorting is in descending order.
GLXC.SORT_DESCENDING = 'DESCENDING'

# Set the final list
GLXC.SortType = [
    GLXC.SORT_ASCENDING,
    GLXC.SORT_DESCENDING
]

###########################
# ResizeMode Constants    #
###########################
# Pass resize request to the parent.
GLXC.RESIZE_PARENT = 'RESIZE_PARENT'
# Queue resize on this widget.
GLXC.RESIZE_QUEUE = 'RESIZE_QUEUE'
# Resize immediately.
GLXC.RESIZE_IMMEDIATE = 'RESIZE_IMMEDIATE'

#####################################
# ProgressBar Orientation Constants #
#####################################
# The ProgressBar Orientation constants specify the orientation and growth direction for a visible progress bar.
# A horizontal progress bar growing from left to right.
GLXC.PROGRESS_LEFT_TO_RIGHT = 'PROGRESS_LEFT_TO_RIGHT'
# A horizontal progress bar growing from right to left.
GLXC.PROGRESS_RIGHT_TO_LEFT = 'PROGRESS_RIGHT_TO_LEFT'
# A vertical progress bar growing from bottom to top.
GLXC.PROGRESS_BOTTOM_TO_TOP = 'PROGRESS_BOTTOM_TO_TOP'
# A vertical progress bar growing from top to bottom.
GLXC.PROGRESS_TOP_TO_BOTTOM = 'PROGRESS_TOP_TO_BOTTOM'

############################
# SizeGroup Mode Constants #
############################
# The SizeGroup Mode constants specify the directions in which the size group affects
# the requested sizes of its component widgets.
# The group has no affect
GLXC.SIZE_GROUP_NONE = 'SIZE_GROUP_NONE'
# The group affects horizontal requisition
GLXC.SIZE_GROUP_HORIZONTAL = 'SIZE_GROUP_HORIZONTAL'
# The group affects vertical requisition
GLXC.SIZE_GROUP_VERTICAL = 'SIZE_GROUP_VERTICAL'
# The group affects both horizontal and vertical requisition
GLXC.SIZE_GROUP_BOTH = 'SIZE_GROUP_BOTH'

#############
# Wrap Mode #
#############
# wrap lines at word boundaries.
GLXC.WRAP_WORD = 'WRAP_WORD'
# wrap lines at character boundaries.
GLXC.WRAP_CHAR = 'WRAP_CHAR'
# wrap lines at word boundaries, but fall back to character boundaries if there is not enough space for a full word.
GLXC.WRAP_WORD_CHAR = 'WRAP_WORD_CHAR'

################
# InputPurpose #
################
# Describes primary purpose of the input widget.
# This information is useful for on-screen keyboards and similar input methods
# to decide which keys should be presented to the user.

# Allow any character
GLXC.INPUT_PURPOSE_FREE_FORM = 'INPUT_PURPOSE_FREE_FORM'
# Allow only alphabetic characters
GLXC.INPUT_PURPOSE_ALPHA = 'INPUT_PURPOSE_ALPHA'
# Allow only digits
GLXC.INPUT_PURPOSE_DIGITS = 'INPUT_PURPOSE_DIGITS'
# Edited field expects numbers
GLXC.INPUT_PURPOSE_NUMBER = 'INPUT_PURPOSE_NUMBER'
# Edited field expects phone number
GLXC.INPUT_PURPOSE_PHONE = 'INPUT_PURPOSE_PHONE'
# Edited field expects URL
GLXC.INPUT_PURPOSE_URL = 'INPUT_PURPOSE_URL'
# Edited field expects email address
GLXC.INPUT_PURPOSE_EMAIL = 'INPUT_PURPOSE_EMAIL'
# Edited field expects the name of a person
GLXC.INPUT_PURPOSE_NAME = 'INPUT_PURPOSE_NAME'
# Like INPUT_PURPOSE_FREE_FORM , but characters are hidden
GLXC.INPUT_PURPOSE_PASSWORD = 'INPUT_PURPOSE_PASSWORD'
# Like INPUT_PURPOSE_DIGITS , but characters are hidden
GLXC.INPUT_PURPOSE_PIN = 'INPUT_PURPOSE_PIN'

################
# Border Style #
################
#    **GLXC.BorderStyle**
#
#    Describes how the border of a UI element should be rendered.
#
#    **Members:**
#       GLXC.BORDER_STYLE_NONE      No visible border
#       GLXC.BORDER_STYLE_SOLID     A single line segment
#       GLXC.BORDER_STYLE_INSET     Looks as if the content is sunken into the canvas
#       GLXC.BORDER_STYLE_OUTSET    Looks as if the content is coming out of the canvas
#       GLXC.BORDER_STYLE_HIDDEN    Same as glxc.BORDER_STYLE_NONE
#       GLXC.BORDER_STYLE_DOTTED    A series of round dots
#       GLXC.BORDER_STYLE_DASHED    A series of square-ended dashes
#       GLXC.BORDER_STYLE_DOUBLE    Two parallel lines with some space between them
#       GLXC.BORDER_STYLE_GROOVE    Looks as if it were carved in the canvas
#       GLXC.BORDER_STYLE_RIDGE     Looks as if it were coming out of the canvas
# No visible border
GLXC.BORDER_STYLE_NONE = 'BORDER_STYLE_NONE'

# A single line segment
GLXC.BORDER_STYLE_SOLID = 'BORDER_STYLE_SOLID'

# Looks as if the content is sunken into the canvas
GLXC.BORDER_STYLE_INSET = 'BORDER_STYLE_INSET'

# Looks as if the content is coming out of the canvas
GLXC.BORDER_STYLE_OUTSET = 'BORDER_STYLE_OUTSET'

# Same as BORDER_STYLE_NONE
GLXC.BORDER_STYLE_HIDDEN = 'BORDER_STYLE_HIDDEN'

# A series of round dots
GLXC.BORDER_STYLE_DOTTED = 'BORDER_STYLE_DOTTED'

# A series of square-ended dashes
GLXC.BORDER_STYLE_DASHED = 'BORDER_STYLE_DASHED'

# Two parallel lines with some space between them
GLXC.BORDER_STYLE_DOUBLE = 'BORDER_STYLE_DOUBLE'

# Looks as if it were carved in the canvas
GLXC.BORDER_STYLE_GROOVE = 'BORDER_STYLE_GROOVE'

# Looks as if it were coming out of the canvas
GLXC.BORDER_STYLE_RIDGE = 'BORDER_STYLE_RIDGE'

GLXC.BorderStyle = [
    'BORDER_STYLE_NONE',
    'BORDER_STYLE_SOLID',
    'BORDER_STYLE_INSET',
    'BORDER_STYLE_OUTSET',
    'BORDER_STYLE_HIDDEN',
    'BORDER_STYLE_DOTTED',
    'BORDER_STYLE_DASHED',
    'BORDER_STYLE_DOUBLE',
    'BORDER_STYLE_GROOVE',
    'BORDER_STYLE_RIDGE'
]

###################
# SensitivityType #
###################
# Determines how GTK+ handles the sensitivity of stepper arrows at the end of range widgets.

# The arrow is made insensitive if the thumb is at the end
GLXC.SENSITIVITY_AUTO = 'AUTO'

# The arrow is always sensitive
GLXC.SENSITIVITY_ON = 'ON'

# The arrow is always insensitive
GLXC.SENSITIVITY_OFF = 'OFF'

# Create the Final List
GLXC.SensitivityType = [
    GLXC.SENSITIVITY_AUTO,
    GLXC.SENSITIVITY_ON,
    GLXC.SENSITIVITY_OFF
]

# Container it use children list and not single child list
GLXC.CHILDREN_CONTAINER = [
    'VBox',
    'HBox',
    'Box'
]

# Container it use children list and not single child list
GLXC.CHILD_CONTAINER = [
    'Bin',
    'Frame',
    'Window',
    'Application'
]

# Widget it is Actionable
GLXC.Actionable = [
    'Button',
    'CheckButton',
    'CheckMenuItem',
    'ColorButton',
    'FontButton',
    'ImageMenuItem',
    'LinkButton',
    'ListBoxRow',
    'LockButton',
    'MenuButton',
    'MenuItem',
    'MenuToolButton',
    'ModelButton',
    'RadioButton',
    'RadioMenuItem',
    'RadioToolButton',
    'ScaleButton',
    'SeparatorMenuItem',
    'Switch',
    'TearoffMenuItem',
    'ToggleButton',
    'ToggleToolButton',
    'ToolButton',
    'VolumeButton'
]

# Widget it is Editable
GLXC.Editable = [
    'Entry',
    'SearchEntry',
    'SpinButton'
]

#########################
# ctype-style character #
#########################

# whitespace -- a string containing all ASCII whitespace
whitespace = ' \t\n\r\v\f'

# ascii_lowercase -- a string containing all ASCII lowercase letters
ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'

# ascii_uppercase -- a string containing all ASCII uppercase letters
ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# ascii_letters -- a string containing all ASCII letters
ascii_letters = ascii_lowercase + ascii_uppercase

# digits -- a string containing all ASCII decimal digits
digits = '0123456789'

# hexdigits -- a string containing all ASCII hexadecimal digits
hexdigits = digits + 'abcdef' + 'ABCDEF'

# octdigits -- a string containing all ASCII octal digits
octdigits = '01234567'

# punctuation -- a string containing all ASCII punctuation characters
punctuation = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""

# accent
accent = "éèàùô"

# printable -- a string containing all ASCII characters considered printable
# printable = digits + ascii_letters + accent + punctuation + whitespace
printable = digits + ascii_letters + punctuation + whitespace
GLXC.Printable = printable

# ASCII KEYS
GLXC.KEY_NUL = 0x00  # ^@
GLXC.KEY_SOH = 0x01  # ^A
GLXC.KEY_STX = 0x02  # ^B
GLXC.KEY_ETX = 0x03  # ^C
GLXC.KEY_EOT = 0x04  # ^D
GLXC.KEY_ENQ = 0x05  # ^E
GLXC.KEY_ACK = 0x06  # ^F
GLXC.KEY_BEL = 0x07  # ^G
GLXC.KEY_BS = 0x08   # ^H
GLXC.KEY_TAB = 0x09  # ^I
GLXC.KEY_HT = 0x09   # ^I
GLXC.KEY_LF = 0x0a   # ^J enter
GLXC.KEY_NL = 0x0a   # ^J
GLXC.KEY_VT = 0x0b   # ^K
GLXC.KEY_FF = 0x0c   # ^L
GLXC.KEY_CR = 0x0d   # ^M
GLXC.KEY_SO = 0x0e   # ^N
GLXC.KEY_SI = 0x0f   # ^O
GLXC.KEY_DLE = 0x10  # ^P
GLXC.KEY_DC1 = 0x11  # ^Q
GLXC.KEY_DC2 = 0x12  # ^R
GLXC.KEY_DC3 = 0x13  # ^S
GLXC.KEY_DC4 = 0x14  # ^T
GLXC.KEY_NAK = 0x15  # ^U
GLXC.KEY_SYN = 0x16  # ^V
GLXC.KEY_ETB = 0x17  # ^W
GLXC.KEY_CAN = 0x18  # ^X
GLXC.KEY_EM = 0x19   # ^Y
GLXC.KEY_SUB = 0x1a  # ^Z
GLXC.KEY_ESC = 0x1b  # ^[ escape
GLXC.KEY_FS = 0x1c   # ^\
GLXC.KEY_GS = 0x1d   # ^]
GLXC.KEY_RS = 0x1e   # ^^
GLXC.KEY_US = 0x1f   # ^_
GLXC.KEY_SP = 0x20   # space
GLXC.KEY_DEL = 0x7f  # delete

