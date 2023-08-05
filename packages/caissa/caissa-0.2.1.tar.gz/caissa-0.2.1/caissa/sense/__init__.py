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

import threading


class Sense:
    """
    Caissa's sense
    """
    
    def __init__(self):
        """
        Constructor
        """
        
        # initialize threads
        key_thread = threading.Thread(target=self.keypress_listener_thread,
                                      daemon=True)
        
        # start the threads
        key_thread.start()
        
        # join the threads
        key_thread.join()
        
        # the listener thread has stopped,
        # hence the user hit CTRL+D or CTRL+Z, exit
        import sys
        sys.exit(0)
    
    def keypress_listener_thread(self):
        """
        Listen to keystrokes.
        """
        
        # initialize get keystroke class
        from .getch import _Getch
        getkey = _Getch()
        
        while True:
            k = getkey()
            
            if k in ['\x04', '\x1A']:
                # the user hit CTRL+D or CTRL+Z, stop thread
                return
                
            print("{:X}".format(ord(k)), flush=True)
