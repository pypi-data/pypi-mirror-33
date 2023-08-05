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

import time


class Brain:
    """
    The brain of Caissa
    
        - interacts with senses
        - holds skills
        - controls the interactions between skills and senses
    """
    
    def __init__(self, hearing, sense, speech):
        # store references to senses
        self.hearing = hearing
        self.sense = sense
        self.speech = speech
        
        # initialize all skills
        self._init_skills()
    
    def _init_skills(self):
        """
        Initialize all skills
        """
        
        pass
    
    def think_forever(self):
        """
        Think forever
        """
        
        while True:
            #self.speech.say("Hello, my name is Caiissa.")
            time.sleep(1)
