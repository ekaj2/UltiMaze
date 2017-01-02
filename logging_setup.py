# Copyright 2017 Integrity Software and Games, LLC
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of UltiMaze.
#
# UltiMaze is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UltiMaze is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with UltiMaze.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

import logging
import os


def setup_logger(name):
    # ensure access to the folder where the logs are kept
    folder = os.path.join(os.path.dirname(__file__), "logs")
    if not os.path.exists(folder):
        os.makedirs(folder)

    # setup the format for the logger
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # makes a logger with the passed name (most likely a module name)
    logger = logging.getLogger(name)

    # setup the handler (this sends the logs to the file with the given formatter)
    handler = logging.FileHandler(os.path.join(folder, name + ".log"))
    handler.setFormatter(formatter)

    # finalize the logger by adding the handler and setting the logging level
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
