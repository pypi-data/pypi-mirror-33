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
import os
import psutil
import subprocess
import threading
import time
import oyaml as yaml

from caissa.brain.events import *
from caissa.brain.skills import Skill


class Radio(Skill):
    """
    Internet radio player
    """
    
    CONFIG_FNAME = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "stations.yml")
    
    def __init__(self, params=None):
        """
        Constructor
        """
        
        # initialize logger
        self.logger = logging.getLogger(__name__)
        
        # load configuration file
        self.config = yaml.load(open(self.CONFIG_FNAME))
        
        self.logger.debug("Found {} radio stations in \"{}\"".format(
            len(self.config["stations"]), self.CONFIG_FNAME))
        
        self.stations = list(self.config["stations"].items())
        
        # initialize other variables
        self.proc = None
        self.current_id = 0
        
        if params.play_radio:
            self.play()
    
    def __del__(self):
        """
        Destructor
        """
        
        self.stop_playing()
    
    def handle_event(self, e):
        """
        Handle the given event
        """
        
        if type(e) is TextInputEvent:
            if e.text == "start radio":
                self.play()
            elif e.text == "prev":
                self.play_prev()
            elif e.text == "next":
                self.play_next()
            elif e.text == "stop radio":
                self.stop_playing()
        elif type(e) is InfraredInputEvent:
            if e.cmd == "KEY_PLAY":
                self.play()
            elif e.cmd == "KEY_PREVIOUS":
                self.play_prev()
            elif e.cmd == "KEY_NEXT":
                self.play_next()
    
    @property
    def is_playing(self):
        """
        Check if the radio is currently playing
        """
        
        return self.proc is not None
    
    def stop_playing(self):
        """
        Stop playing
        """
        
        # terminate a possibly active player process
        if self.is_playing:
            process = psutil.Process(self.proc.pid)
            
            for child_process in process.children(recursive=True):
                child_process.kill()
            
            process.kill()
            
            self.proc = None
    
    def play(self, radio_station_id=None):
        """
        Play the given radio station
        """
        
        if radio_station_id == None:
            radio_station_id = self.current_id
        
        station_label, station_params = self.stations[radio_station_id]
        
        self.logger.debug("Playing radio station \"{}\"".format(
            station_label))
        
        # first stop playing
        self.stop_playing()
        
        cmd = "while true; do mpg123 '{}'; sleep 1; done".format(
            station_params["url"])
        self.proc = subprocess.Popen(cmd,
                                     shell=True,
                                     stdin=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     stdout=subprocess.PIPE)
    
    def play_prev(self):
        """
        Play the previous station
        """
        
        if self.is_playing:
            # increment radio station is
            self.current_id = (self.current_id - 1) % len(self.stations)
        
        self.play(self.current_id)
    
    def play_next(self):
        """
        Play the next station
        """
        
        if self.is_playing:
            # increment radio station is
            self.current_id = (self.current_id + 1) % len(self.stations)
        
        self.play(self.current_id)
