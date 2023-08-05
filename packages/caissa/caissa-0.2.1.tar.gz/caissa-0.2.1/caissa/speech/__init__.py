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

import speake3


class Speech:
    """
    Caissa's speech
    """

    def __init__(self, default_lang="en"):
        """
        Constructor
        """
        
        # define engine language options
        self.lang_options = {
            "en": {
                "voice": "english-mb-en1+f4",
                "speed": "100",
                "pitch": "60"
            },
            "nl": {
                "voice": "dutch-mbrola-2+f4",
                "speed": "100"
            }
        }
        
        # instantiate text to speech engines for each language
        self.engines = {lang: speake3.Speake() for lang in self.lang_options}
        
        # set engine options
        for lang in self.lang_options:
            for option, value in self.lang_options[lang].items():
                self.engines[lang].set(option, value)
        
        # store default language
        self.default_lang = default_lang
        
    def say(self, message, lang=None):
        """
        Say the given message
        """
        
        if lang is None:
            lang = self.default_lang
        
        self.engines[lang].say(message)
        self.engines[lang].talkback()


if __name__ == "__main__":
    # TODO: take care of alterations in separate class
    # test the Speech class
    speech = Speech("en")
    speech.say("Hello, my name is Caiissa.")
    speech.say("How are you doing?")
    
    speech = Speech("nl")
    speech.say("Hallo, ik heet Caïissa.")
    speech.say("Hoe gaat het met U?")
