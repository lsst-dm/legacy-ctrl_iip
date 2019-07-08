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
import os.path
import signal
import sys
import time
import yaml
from lsst.ctrl.iip.const import ROOT
from lsst.ctrl.iip.Credentials import Credentials

LOGGER = logging.getLogger(__name__)


class base:
    """Base class"""

    def __init__(self, filename, log_filename):
        self._config = self.loadConfigFile(filename)
        self.setupLogging(log_filename)
        self._cred = Credentials('iip_cred.yaml')

    def loadConfigFile(self, filename):
        """Load configuration file from configuration directory.  The
        default location is $CTRL_IIP_DIR/etc/config.  If the environment
        variable $IIP_CONFIG_DIR exists, files are loaded from that location
        instead.
        """

        config_file = filename

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

    def getCredentials(self):
        return self._cred

    def getConfiguration(self):
        return self._config

    def setupLogging(self, filename):
        """Setup writing to a log. If the IIP_LOG_DIR environment variable
        is set, use that.  Otherwise, use log_dir_location if it was
        specified. If it wasn't, default to /tmp.
        Params
        ------
        filename:  the log file to write to
        """

        log_dir_location = self._config[ROOT].get('LOGGING_DIR', None)

        log_dir = None

        if "IIP_LOG_DIR" in os.environ:
            log_dir = os.environ["IIP_LOG_DIR"]
        else:
            if log_dir_location is not None:
                log_dir = log_dir_location
            else:
                log_dir = "/tmp"

        log_file = os.path.join(log_dir, filename)

        FORMAT = ('%(levelname) -10s %(asctime)s.%(msecs)06dZ %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s')
        LOGGER = logging.getLogger(__name__)
        logging.Formatter.converter = time.gmtime
        LOGGER.setLevel(logging.DEBUG)
        handler = RotatingFileHandler(log_file, maxBytes=2000000, backupCount=10)
        LOGGER.addHandler(handler)
        logging.basicConfig(filename=log_file, level=logging.INFO, format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S")


        return log_file

    def shutdown(self):
        pass

    def register_SIGINT_handler(self):
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        LOGGER.info("shutdown signal received")
        print("shutdown signal received")
        self.shutdown()
