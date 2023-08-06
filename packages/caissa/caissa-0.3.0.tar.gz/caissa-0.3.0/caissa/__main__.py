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


def main(args=None):
    """
    Bring Caissa to life
    """
    
    from . import Caissa
    
    import argparse
    import logging
    
    # parse arguments
    parser = argparse.ArgumentParser(description="Caissa voice-controlled personal assistant")
    parser.add_argument("--daemon", action="store_true", help="run as daemon (do not exit after end-of-file)")
    parser.add_argument("--debug", action="store_true", help="enable debug output")
    parser.add_argument("--play-radio", action="store_true", help="play radio on startup")
    args = parser.parse_args(args)
    
    # set up logging
    logging_level = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(level=logging_level)
    
    logger = logging.getLogger(__name__)
    logger.debug("Bringing Caissa to life")
    
    caissa = Caissa(args)
    caissa.live_forever()


if __name__ == "__main__":
    main()
