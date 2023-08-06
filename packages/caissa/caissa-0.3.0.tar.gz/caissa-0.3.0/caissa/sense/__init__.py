# -*- coding: utf-8 -*-
"""
Caissa voice-controlled personal assistant
Copyright © 2018  Dieter Dobbelaere

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from ..brain.events import InfraredInputEvent, TextInputEvent

import lirc
import logging
import threading


class Sense:
    """
    Caissa's sense
    """
    
    def __init__(self, args):
        """
        Constructor
        """
        
        # initialize event queue reference
        self.event_queue = None
        
        # initialize threads
        self.stdin_thread = threading.Thread(target=self.stdin_listener_thread,
                                             daemon=True)
        
        self.lirc_thread = threading.Thread(target=self.lirc_listener_thread,
                                            daemon=True)
        
        # initialize logger
        self.logger = logging.getLogger(__name__)
        
        # behavior on end-of-file
        self.exit_after_eof = not args.daemon
    
    def start(self, event_queue):
        """
        Start sensing
        """
        
        # store reference to event queue
        self.event_queue = event_queue
        
        # start the threads
        self.stdin_thread.start()
        self.lirc_thread.start()
    
    def stdin_listener_thread(self):
        """
        Listen to input
        """
        
        while True:
            try:
                s = input()
            except EOFError:
                if self.exit_after_eof:
                    # exit on end-of-file
                    self.event_queue.put(TextInputEvent("exit"))
                
                # stop listening after end-of-file
                return
            
            # add input event to queue
            self.event_queue.put(TextInputEvent(s))
    
    def lirc_listener_thread(self):
        """
        Listen to infrared commands
        """
        
        try:
            lirc.init("caissa", blocking=False)
        except lirc.InitError:
            self.logger.warning("Exception occurred while trying to "
                                "initialize infrared listener thread")
        else:
            import time
            
            while True:
                code_list = lirc.nextcode()
                
                for code in code_list:
                    key_name = code.split(",")[0].strip()
                
                    # add input event to queue
                    self.event_queue.put(InfraredInputEvent(key_name))
                
                time.sleep(0.05)
