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

import os
from const import *
import yaml

class iip_base:
    """Base class"""

    def loadConfigFile(self, filename=None):
        """Load configuration file from configuration directory.  The
        default location is $CTRL_IIP_DIR/etc/config.  If the environment
        variable $IIP_CONFIG_DIR exists, files are loaded from that location
        instead.
        """

        config_file = None
        if filename != None:
            config_file = filename
        else:
            # this presumes we load from the $CTRL_IIP_DIR; this may need
            # to be changed if we install in a central location for config
            # files that can be editted.
            if "IIP_CONFIG_DIR" in os.environ:
                config_dir = os.environ["IIP_CONFIG_DIR"]
                config_file = os.path.join(config_dir, DEFAULT_CONFIG_FILE)
            else:
                if "CTRL_IIP_DIR" in os.environ:
                    config_dir = os.environ["CTRL_IIP_DIR"]
                    config_dir = os.path.join(config_dir, "etc", "config")
                    config_file = os.path.join(config_dir, DEFAULT_CONFIG_FILE)
                else:
                    raise Exception("environment variable CTRL_IIP_DIR not defined")
        try:
            f = open(config_file)
        except:
            raise L1Error("Can't open %s" % config_file)

        config = None
        try:
            config = yaml.safe_load(f)
        except:
            raise L1Error("Error reading %s" % config_file)
        finally:
            f.close()
        return config
