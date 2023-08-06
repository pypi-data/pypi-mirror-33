#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import random
import string
from GLXCurses import MessageBar
from GLXCurses.Utils import glxc_type
from GLXCurses.Utils import is_valid_id


# Unittest
class TestMessageBar(unittest.TestCase):

    # Test
    def test_glxc_type(self):
        """Test StatusBar type"""
        messagebar = MessageBar()
        self.assertTrue(glxc_type(messagebar))

    def test_new(self):
        """Test StatusBar.new()"""
        # create a window instance
        messagebar = MessageBar()
        # get the window id
        messagebar_id_take1 = messagebar.get_widget_id()
        # check if returned value is a valid id
        self.assertTrue(is_valid_id(messagebar_id_take1))
        # use new() method
        messagebar.new()
        # re get the window id
        messagebar_id_take2 = messagebar.get_widget_id()
        # check if returned value is a valid id
        self.assertTrue(is_valid_id(messagebar_id_take2))
        # id's must be different
        self.assertNotEqual(messagebar_id_take1, messagebar_id_take2)

    def test_get_context_id(self):
        """Test MessageBar.get_context_id()"""
        # create a window instance
        messagebar = MessageBar()
        # generate a random string
        context_text = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        # get the window id
        messagebar_context_id_take1 = messagebar.get_context_id(context_description=context_text)
        # check if returned value is a valid id
        self.assertTrue(is_valid_id(messagebar_context_id_take1))
        # test raises
        self.assertRaises(TypeError, messagebar.get_context_id, context_description=int())

    def test_push(self):
        """Test MessageBar.push()"""
        # create a window instance
        messagebar = MessageBar()
        # generate a random string
        text_take1 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        text_take2 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        # get the window id
        context_id = messagebar.get_context_id(context_description=text_take1)
        # get stack size
        stack_len = len(messagebar.messagebar_stack)
        # call StatusBar.push() suppose to return a message id
        message_id = messagebar.push(context_id=context_id, text=text_take2)
        # check if returned value is a valid id
        self.assertTrue(is_valid_id(message_id))
        # compare stack size suppose to grow
        self.assertGreater(len(messagebar.messagebar_stack), stack_len)
        # compare last element
        self.assertEqual(messagebar.messagebar_stack[-1]['context_id'], context_id)
        self.assertEqual(messagebar.messagebar_stack[-1]['message_id'], message_id)
        self.assertEqual(messagebar.messagebar_stack[-1]['text'], text_take2)
        # test raises
        self.assertRaises(TypeError, messagebar.push, context_id=str(), text=text_take2)
        self.assertRaises(TypeError, messagebar.push, context_id=context_id, text=float())

    def test_pop(self):
        """Test StatusBar.pop()"""
        # create a window instance
        messagebar = MessageBar()
        # Preparation push completely a thing and save every value's
        context_description_1 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        text_1 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        context_id_1 = messagebar.get_context_id(context_description=context_description_1)
        message_id_1 = messagebar.push(context_id=context_id_1, text=text_1)

        # compare last element
        self.assertEqual(messagebar.messagebar_stack[-1]['context_id'], context_id_1)
        self.assertEqual(messagebar.messagebar_stack[-1]['message_id'], message_id_1)
        self.assertEqual(messagebar.messagebar_stack[-1]['text'], text_1)

        # Preparation push completely a thing and save every value's
        context_description_2 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        text_2 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        context_id_2 = messagebar.get_context_id(context_description=context_description_2)
        message_id_2 = messagebar.push(context_id=context_id_2, text=text_2)

        # compare last element
        self.assertEqual(messagebar.messagebar_stack[-1]['context_id'], context_id_2)
        self.assertEqual(messagebar.messagebar_stack[-1]['message_id'], message_id_2)
        self.assertEqual(messagebar.messagebar_stack[-1]['text'], text_2)

        # POP
        messagebar.pop(context_id=context_id_2)

        # check if are back to previous element
        self.assertEqual(messagebar.messagebar_stack[-1]['context_id'], context_id_1)
        self.assertEqual(messagebar.messagebar_stack[-1]['message_id'], message_id_1)
        self.assertEqual(messagebar.messagebar_stack[-1]['text'], text_1)

        # test raise
        self.assertRaises(TypeError, messagebar.pop, context_id=int())
        self.assertRaises(TypeError, messagebar.pop, )

    def test_remove(self):
        """Test StatusBar.remove()"""
        # create a window instance
        messagebar = MessageBar()

        # get stack size
        stack_len = len(messagebar.messagebar_stack)

        # Preparation push completely a thing and save every value's
        context_description_1 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        text_1 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        context_id_1 = messagebar.get_context_id(context_description=context_description_1)
        message_id_1 = messagebar.push(context_id=context_id_1, text=text_1)

        # compare last element
        self.assertEqual(messagebar.messagebar_stack[-1]['context_id'], context_id_1)
        self.assertEqual(messagebar.messagebar_stack[-1]['message_id'], message_id_1)
        self.assertEqual(messagebar.messagebar_stack[-1]['text'], text_1)

        # compare stack size suppose to grow
        self.assertGreater(len(messagebar.messagebar_stack), stack_len)

        # remove
        messagebar.remove(context_id=context_id_1, message_id=message_id_1)

        # compare stack size suppose to grow
        self.assertEqual(len(messagebar.messagebar_stack), stack_len)

        # test raises
        self.assertRaises(TypeError, messagebar.remove, context_id=int(), message_id=message_id_1)
        self.assertRaises(TypeError, messagebar.remove, context_id=context_id_1, message_id=float())
        self.assertRaises(TypeError, messagebar.remove, context_id=context_id_1)
        self.assertRaises(TypeError, messagebar.remove, message_id=message_id_1)

    def test_remove_all(self):
        """Test StatusBar.remove_all()"""
        # create a window instance
        messagebar = MessageBar()

        # get stack size
        stack_len_1 = len(messagebar.messagebar_stack)

        # prepare a context_id
        context_description_1 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        context_id_1 = messagebar.get_context_id(context_description=context_description_1)

        # Preparation push completely a thing and save every value's
        text_1 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        messagebar.push(context_id=context_id_1, text=text_1)

        # compare stack size suppose to grow
        self.assertGreater(len(messagebar.messagebar_stack), stack_len_1)

        # get stack size
        stack_len_2 = len(messagebar.messagebar_stack)

        # Preparation push completely a thing and save every value's
        text_2 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        messagebar.push(context_id=context_id_1, text=text_2)

        # compare stack size suppose to grow
        self.assertGreater(len(messagebar.messagebar_stack), stack_len_2)

        # remove_all
        messagebar.remove_all(context_id=context_id_1)

        # compare stack size suppose to grow
        self.assertGreater(len(messagebar.messagebar_stack), stack_len_1)

        # test raises
        self.assertRaises(TypeError, messagebar.remove_all, context_id=int())
