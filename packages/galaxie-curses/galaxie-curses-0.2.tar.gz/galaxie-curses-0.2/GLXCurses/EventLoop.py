#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

import logging
from GLXCurses.Utils import new_id


class MyEventBus(object):
    def __init__(self):
        self.event_buffer = list()
        # Signal
        self.signal_handlers = dict()
        self.blocked_handler = list()
        self.blocked_function = list()
        self.data = dict()

    def get_data(self, key):
        """
        The get_data() method returns the Python object associated with the specified key or
        None if there is no data associated with the key or if there is no key associated with the object.

        :param key: a string used as the keyname
        :return: object associated with the specified key or None
        :rtype: Python object or None
        """
        if key not in self._get_data_dict():
            return None
        elif not len(self._get_data_dict()[key]):
            return None
        else:
            return self._get_data_dict()[key]

    def set_data(self, key, data):
        """
        The set_data() method associates the specified Python object (data) with key.

        :param key: a string used as the key
        :param data: a Python object that is the value to be associated with the key
        """
        self._get_data_dict()[key] = data

    def connect(self, detailed_signal, handler, *args):
        """
        The connect() method adds a function or method (handler)to the end of the list of signal handlers
        for the named detailed_signal but before the default class signal handler.

        An optional set of parameters may be specified after the handler parameter.
        These will all be passed to the signal handler when invoked.

        :param detailed_signal: a string containing the signal name
        :param handler: a handler
        :param args: additional parameters arg1, arg2
        :return: a unique integer handler identifier
        :rtype: ID
        """
        if detailed_signal not in self._get_signal_handlers_dict():
            self._get_signal_handlers_dict()[detailed_signal] = {}

        subscription = {
            'handler': handler,
            'argvs': args
        }
        handler_id = new_id()
        self._get_signal_handlers_dict()[detailed_signal][handler_id] = subscription
        return handler_id

    def disconnect(self, handler_id):
        """
        The disconnect() method removes the signal handler with the specified handler_id
        from the list of signal handlers for the object.

        :param handler_id: an integer handler identifier
        :type handler_id: GLXCurses ID
        """
        for detailed_signal, infos in self._get_signal_handlers_dict().iteritems():
            for id, infos2 in infos.iteritems():
                if id == handler_id:
                    del self._get_signal_handlers_dict()[detailed_signal][handler_id]
                    break

    def handler_disconnect(self, handler_id):
        """
        The handler_disconnect() method removes the signal handler with the specified handler_id
        from the list of signal handlers for the object.

        :param handler_id: an integer handler identifier
        :type handler_id: GLXCurses ID
        """
        self.disconnect(handler_id)

    # The handler_is_connected() method returns True
    # if the signal handler with the specified handler_id is connected to the object.
    def handler_is_connected(self, handler_id):
        for detailed_signal, infos in self._get_signal_handlers_dict().iteritems():
            for id, infos in infos.iteritems():
                if id == handler_id:
                    return True
        return False

    # The handler_block() method blocks the signal handler with the specified handler_id
    # from being invoked until it is unblocked.
    # handler_id: an integer handler identifier
    def handler_block(self, handler_id):
        if handler_id not in self.blocked_handler:
            self._get_blocked_handler().append(handler_id)
        else:
            pass

    # handler_id: an integer handler identifier
    def handler_unblock(self, handler_id):
        # noinspection PyBroadException
        try:
            self._get_blocked_handler().pop(self._get_blocked_handler().index(handler_id))
        except:
            pass

    # The handler_block_by_func() method blocks
    # the all signal handler connected to a specific callable from being invoked until the callable is unblocked.
    # callable : a callable python object
    def handler_block_by_func(self, callable):
        if callable not in self.blocked_handler:
            self._get_blocked_function().append(callable)
        else:
            pass

    # The handler_unblock_by_func() method unblocks all signal handler connected to a specified callable there
    # by allowing it to be invoked when the associated signals are emitted.
    # callback : a callable python object
    def handler_unblock_by_func(self, callback):
        # noinspection PyBroadException
        try:
            self._get_blocked_function().pop(self._get_blocked_function().index(callback))
        except:
            pass

    def pop_last_event(self):
        # noinspection PyBroadException
        try:
            if len(self.event_buffer) > 0:
                return self.event_buffer.pop()
        except:
            pass

    # detailed_signal: a string containing the signal name
    # *args: additional parameters arg1, arg2
    def emit(self, detailed_signal, args=None):
        if args is None:
            args = list()
        logging.debug('MyEventBus:emit ' + str(detailed_signal) + ' - ' + str(args))
        self.event_buffer.insert(0, [detailed_signal, args])

    def dispatch(self, event_signal, event_args):
        for subscription, infos in self._get_signal_handlers_dict().iteritems():
            if subscription == event_signal:
                for id, infos in infos.iteritems():
                    if id not in self._get_blocked_handler():
                        if self._get_signal_handlers_dict()[subscription][id]['handler'] not \
                                in self._get_blocked_function():
                            if len(event_args):
                                self._get_signal_handlers_dict()[subscription][id]['handler'](event_args)
                            else:
                                self._get_signal_handlers_dict()[subscription][id]['handler']()

    # Internal Function
    def _reset(self):
        # All subscribers will be cleared.
        self.signal_handlers = dict()
        self.blocked_handler = list()
        self.blocked_function = list()
        self.data = dict()

    def _get_signal_handlers_dict(self):
        return self.signal_handlers

    def _get_data_dict(self):
        return self.data

    def _get_blocked_handler(self):
        return self.blocked_handler

    def _get_blocked_function(self):
        return self.blocked_function
