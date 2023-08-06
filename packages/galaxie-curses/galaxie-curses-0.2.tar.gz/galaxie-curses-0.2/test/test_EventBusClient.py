#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import sys
import os

from GLXCurses.Utils import glxc_type
import GLXCurses

# Require when you haven't GLXCurses as default Package
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))


# Unittest
class TestEventBusClient(unittest.TestCase):

    # Test
    def test_glxc_type(self):
        """Test EventBus Type"""
        event_bus = GLXCurses.EventBusClient()
        self.assertFalse(glxc_type(event_bus))



