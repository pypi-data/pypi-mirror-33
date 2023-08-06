#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

from GLXCurses import GLXC
import GLXCurses
import curses
import logging
from GLXCurses.Editable import Editable


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


# https://developer.gnome.org/glib/stable/glib-The-Main-Event-Loop.html
class MainLoop(object):
    """
    :Description:

    The MainLoop is something close to a infinity loop with a start() and stop() method
     . Refresh the Application for the first time
     . Start the Loop
     . Wait for a Curses events then dispatch events and signals over Application Children's
     . Refresh the Application if a event or a signal have been detect
     . If MainLoop is stop the Application will close and should be follow by a sys.exit()

    Attributes:
        event_buffer       -- A List, Default Value: list()
        started            -- A Boolean, Default Value: False

    Methods:
        get_event_buffer() -- get the event_buffer attribute
        get_started()      -- get the started attribute
        start()            -- start the mainloop
        stop()             -- stop the mainloop
        emit()             -- emit a signal

    .. warning:: you have to start the mainloop from you application via MainLoop().start()
    """
    __metaclass__ = Singleton

    def __init__(self):
        """
        Creates a new MainLoop structure.
        """
        self.event_buffer = list()
        self._is_running = False

        # Merdouille
        # context_list
        self.context_list = list()
        self.default_context = None

    def get_event_buffer(self):
        """
        Return the event_buffer list attribute, it lis can be edited or modify as you need

        :return: event buffer
        :rtype: list()
        """
        return self.event_buffer

    def is_running(self):
        """
        Checks to see if the MainLoop is currently being run via run().

        :return: TRUE if the mainloop is currently being run.
        :rtype: Boolean
        """
        return self._is_running

    def get_context(self):
        """
        Returns the MainContext of loop .

        :return: the MainContext of loop .
        """
        raise NotImplementedError

    def context_new(self):
        """
        Creates a new MainContext structure.

        :return: the new MainContext
        """
        raise NotImplementedError

    def context_ref(self):
        """
        Increases the reference count on a MainContext object by one.

        :return: the context that was passed in
        """
        raise NotImplementedError

    def context_unref(self):
        """
        Decreases the reference count on a MainContext object by one.
        If the result is zero, free the context and free all associated memory.
        """
        raise NotImplementedError

    def context_default(self):
        """
        Returns the global default main context. This is the main context used for main loop functions when a main loop
        is not explicitly specified, and corresponds to the "main" main loop.

        .. seealso:: context_get_thread_default().

        :return: the global default main context.
        :rtype: Context
        """
        raise NotImplementedError

    def context_iteration(self, may_block):
        """
        Runs a single iteration for the given main loop. This involves checking to see if any event sources are ready
        to be processed, then if no events sources are ready and **may_block** is TRUE, waiting for a source to become
        ready, then dispatching the highest priority events sources that are ready. Otherwise, if **may_block** is FALSE
        sources are not waited to become ready, only those highest priority events sources will be dispatched (if any),
        that are ready at this given moment without further waiting.

        Note that even when **may_block** is TRUE, it is still possible for context_iteration() to return FALSE,
        since the wait may be interrupted for other reasons than an event source becoming ready.

        :param may_block: whether the call may block.
        :return: TRUE if events were dispatched.
        :rtype: bool
        """
        raise NotImplementedError

    def context_pending(self, context=None):
        if context is None:
            context = self.get_default_context()
        raise NotImplementedError

    def run(self):
        """
        Runs a MainLoop until quit() is called on the loop. If this is called for the thread of the loop's
        , it will process events from the loop, otherwise it will simply wait.
        """
        self._set_is_running(True)
        logging.info('Starting ' + self.__class__.__name__)
        self._run()

    def quit(self):
        """
        Stops a MainLoop from running. Any calls to run() for the loop will return.

        Note that sources that have already been dispatched when quit() is called will still be executed.

        .. :warning: A MainLoop quit() call will certainly cause the end of you programme
        """
        self._set_is_running(False)
        logging.info('Stopping ' + self.__class__.__name__)

    def emit(self, signal, args=None):
        """
        Emit a signal, it consist to add the signal structure inside a global event list

        .. code-block:: python

           args = dict(
               'uuid': Widget().get_widget_id()
               'key1': value1
               'key2': value2
           )
           structure = list(
               detailed_signal,
               args
           )

        :param signal: a string containing the signal name
        :param args: additional parameters arg1, arg2
        """
        if args is None:
            args = dict()

        logging.info(signal + ' ' + str(args))

        self.get_event_buffer().insert(0, [signal, args])

        GLXCurses.application.refresh()

    # Internal Method's
    def _set_is_running(self, boolean):
        """
        Set the is_running attribute

        :param boolean: 0 or True
        :type boolean: Boolean
        """
        self._is_running = bool(boolean)

    def _pop_last_event(self):
        # noinspection PyBroadException
        try:
            if len(self.get_event_buffer()) > 0:
                return self.get_event_buffer().pop()

        except Exception as the_error:
            logging.debug(self.__class__.__name__ + ": Error %s" % str(the_error))

    def _handle_curses_input(self, input_event):
        width, height = GLXCurses.application.get_size()
        if input_event == curses.KEY_MOUSE:
            self.emit('MOUSE_EVENT', curses.getmouse())
        elif input_event == curses.KEY_RESIZE:
            if [width, height] != GLXCurses.application.get_size():
                width, height = GLXCurses.application.get_size()
                instance = {
                    'class': GLXCurses.application.__class__.__name__,
                    'type': 'Resize',
                    'id': GLXCurses.application.id,
                    'width': width,
                    'height': height,
                }

                self.emit('RESIZE', instance)
        else:
            self.emit('CURSES', input_event)

    def _handle_event(self):
        try:
            event = self._pop_last_event()
            while event:
                # If it have event dispatch it
                GLXCurses.application.events_dispatch(event[0], event[1])
                # Delete the last event inside teh event list
                event = self._pop_last_event()

        except Exception as the_error:
            logging.debug(self.__class__.__name__ + ": Error %s" % str(the_error))

    def _run(self):
        if self.is_running():
            # A bit light for notify about we are up and runing, but we are really inside the main while(1) loop
            logging.debug(self.__class__.__name__ + ': Started')

            # That normally the first refresh of the application, it can be considered as the first screen display.
            # Something is display before the first event
            GLXCurses.application.refresh()

        # The loop
        while self.is_running():
            try:
                # Wait for a event
                input_event = GLXCurses.application.getch()
                # logging.debug(self.event_buffer)

                # Wait for a event
                if input_event != -1:
                    self._handle_curses_input(input_event)

                # Do something with event
                self._handle_event()

                # In case it was a graphic event we refresh the screen, ncurse have a optimization mechanism for refresh
                # only character's it need.
                GLXCurses.application.refresh()

            except KeyboardInterrupt:
                # Check is the focus widget is a Editable
                if isinstance(GLXCurses.application.get_is_focus()['widget'], Editable):
                    # Consider as Ctrl + c
                    self.emit('CURSES', 3)
                else:
                    self._set_is_running(False)

        # Here self.get_started() == False , then the GLXCurse.Mainloop() should be close
        GLXCurses.application.close()
