# This file is part of ctrl_iip
# 
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import yaml
from lsst.ctrl.iip.const import *

class iip_base:
    """Base class"""

    def loadConfigFile(self, filename=None):
        """Load configuration file from configuration directory.  The
        default location is $CTRL_IIP_DIR/etc/config.  If the environment
        variable $IIP_CONFIG_DIR exists, files are loaded from that location
        instead.
        """


        if filename == None:
            config_file = DEFAULT_CONFIG_FILE
        else:
            config_file = filename

        # this presumes we load from the $CTRL_IIP_DIR; this may need
        # to be changed if we install in a central location for config
        # files that can be editted.
        if "IIP_CONFIG_DIR" in os.environ:
            config_dir = os.environ["IIP_CONFIG_DIR"]
            config_file = os.path.join(config_dir, config_file)
        else:
            if "CTRL_IIP_DIR" in os.environ:
                config_dir = os.environ["CTRL_IIP_DIR"]
                config_dir = os.path.join(config_dir, "etc", "config")
                config_file = os.path.join(config_dir, config_file)
            else:
                raise Exception("environment variable CTRL_IIP_DIR not defined")

        try:
            f = open(config_file)
        except Exception:
            print("Can't open %s" % config_file)
            sys.exit(10)

        config = None
        try:
            config = yaml.safe_load(f)
        except Exception:
            print("Error reading %s" % config_file)
        finally:
            f.close()
        return config

    def setupLogging(self, filename):

        log_dir = self.getLogDirectory()
        log_file = os.path.join(log_dir, filename)

        LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s')
        LOGGER = logging.getLogger(__name__)
        LOGGER.setLevel(logging.DEBUG)
        handler = RotatingFileHandler(log_file, maxBytes=2000000, backupCount = 10)
        handler.setFormatter(LOG_FORMAT)
        LOGGER.addHandler(handler)

        logging.basicConfig(filename=log_file, level=logging.INFO, format=LOG_FORMAT)


        return log_file
    

    def getLogDirectory(self):
        log_dir = "/tmp"
        if "IIP_LOG_DIR" in os.environ:
            log_dir = os.environ["IIP_LOG_DIR"]
        return log_dir
