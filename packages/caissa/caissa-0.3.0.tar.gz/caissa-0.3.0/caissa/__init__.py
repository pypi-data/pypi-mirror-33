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

from .brain import Brain
from .sense import Sense
from .speech import Speech
from .hearing import *


class Caissa:
    """
    Caissa voice-controlled personal assistant
    """
    
    def __init__(self, args):
        """
        Construct and connect Caissa's vital organs
        """
        
        # initialize senses
        sense = Sense(args=args)
        speech = Speech()
        
        # initialize brain
        self.brain = Brain(args=args, hearing=None, sense=sense, speech=speech)
    
    def live_forever(self):
        """
        Bring Caissa to life
        """
        
        self.brain.think_forever()


"""
@startuml

skinparam ArrowColor DarkSlateGray
skinparam defaultFontName Purisa
skinparam handwritten true

skinparam NodeSep 5
skinparam RankSep 10

skinparam frame {
    BackgroundColor LightGreen
    BorderColor DarkSlateGray
    FontSize 25
    FontStyle bold
}

skinparam rectangle {
    BackgroundColor AliceBlue
    BorderColor DarkSlateGray
    RoundCorner 20
    FontStyle italic
}

actor User

frame " Caissa " {
    rectangle Senses {
        () Hearing
        () Sense
        () Speech
    }
    
    rectangle Brain {
        queue "Event Queue" as EventQueue
        
        rectangle Skills {
            file Chess
            file Radio
            file Weather
        }
    }
}

User <-down(0)--------..> Senses
Senses -up-..> EventQueue
Skills ..-up-> EventQueue

@enduml
"""
