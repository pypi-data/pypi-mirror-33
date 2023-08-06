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

import logging


class Event:
    """
    An event that has happened in Caissa
    """
    
    def __init__(self):
        logger = logging.getLogger(__name__)
        logger.debug("Constructed new event.")


class InfraredInputEvent(Event):
    """
    An text input event
    """
    
    def __init__(self, cmd):
        logger = logging.getLogger(__name__)
        logger.debug("Constructed new infrared input event \"{}\"".format(cmd))
        
        self._cmd = cmd
    
    @property
    def cmd(self):
        return self._cmd


class TextInputEvent(Event):
    """
    An text input event
    """
    
    def __init__(self, text):
        logger = logging.getLogger(__name__)
        logger.debug("Constructed new text input event \"{}\"".format(text))
        
        self._text = text
    
    @property
    def text(self):
        return self._text
