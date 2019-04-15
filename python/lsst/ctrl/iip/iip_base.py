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
import threading
import yaml
from lsst.ctrl.iip.const import *
from lsst.ctrl.iip.Credentials import Credentials
from lsst.ctrl.iip.ThreadManager import ThreadManager

LOGGER = logging.getLogger(__name__)

class iip_base:
    """Base class"""

    def __init__(self, filename):
        self.cred = Credentials('iip_cred.yaml')
        self.thread_manager = self.setup_thread_manager()

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

    def setupLogging(self, log_dir_location, filename):
        """Setup writing to a log. If the IIP_LOG_DIR environment variable
        is set, use that.  Otherwise, use log_dir_location if it was
        specified. If it wasn't, default to /tmp.
        Params
        ------
        log_dir_location:  the directory to write the log file to
        """

        log_dir = None

        if "IIP_LOG_DIR" in os.environ:
            log_dir = os.environ["IIP_LOG_DIR"]
        else:
            if log_dir_location is not None:
                log_dir = log_dir_location
            else:
                log_dir = "/tmp"

        log_file = os.path.join(log_dir, filename)

        LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s')
        LOGGER = logging.getLogger(__name__)
        LOGGER.setLevel(logging.DEBUG)
        handler = RotatingFileHandler(log_file, maxBytes=2000000, backupCount = 10)
        handler.setFormatter(LOG_FORMAT)
        LOGGER.addHandler(handler)

        logging.basicConfig(filename=log_file, level=logging.INFO, format=LOG_FORMAT)


        return log_file
    
    def setup_thread_manager(self):
        self.shutdown_event = threading.Event()
        self.shutdown_event.clear()
        thread_manager = ThreadManager('thread-manager', self.shutdown_event)
        thread_manager.start()
        return thread_manager

    def add_thread_groups(self, kws):
        self.thread_manager.add_thread_groups(kws)

    def setup_unpaired_publisher(self, url, name):
        self.thread_manager.add_unpaired_publisher_thread(url, name)

    #def get_publisher_paired_with(self, consumer_name):
    #    return self.thread_manager.get_publisher_paired_with(consumer_name)

    def publish_message(self, route_key, msg):
        # we have to get the publisher each time because we can't guarantee that the publisher
        # that was first created hasn't died and been replaced
        consumer_name = threading.currentThread().getName()

        pub = self.thread_manager.get_publisher_paired_with(consumer_name)
        pub.publish_message(route_key, msg)

    def shutdown(self):
        LOGGER.info("Shutting down threads.")
        self.shutdown_event.set()
        self.thread_manager.shutdown_threads()
        LOGGER.info("Thread Manager shut down complete.")

    def register_SIGINT_handler(self):
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        LOGGER.info("shutdown signal received")
        self.shutdown()
