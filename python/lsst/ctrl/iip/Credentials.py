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
import os.path
import stat
import sys
import yaml
from lsst.ctrl.iip.ThreadManager import ThreadManager

class Credentials:

    def __init__(self, filename):
        self.cred = self.loadSecureFile(filename)
    
    def getUser(self, user_alias):
        return self.cred['rabbitmq_users'][user_alias]

    def getPasswd(self, passwd_alias):
        return self.cred['rabbitmq_users'][passwd_alias]

    def loadSecureFile(self, cred_file):
        """load a secure YAML file"""

        home = os.environ["HOME"]
        config_dir = os.path.join(home,".lsst")
        # check for the existence of the configuration directory
        if os.path.isdir(config_dir):
            stat_info = os.stat(config_dir)
            mode = stat_info.st_mode
            
            # check that the permissions are set to rwx for only the user
            if (mode & (stat.S_IWOTH | stat.S_IWGRP | stat.S_IROTH | stat.S_IRGRP)):
                print("directory '%s' is unsecure.  Run 'chmod 700 %s' to fix this." % (config_dir, config_dir))
                os._exit(100)
            filename = os.path.join(config_dir, cred_file)
            # check that the credential file exists
            if os.path.isfile(filename):
                stat_info = os.stat(filename)
                mode = stat_info.st_mode
                # check that the credential file is set to rw for only the user
                if (mode & (stat.S_IWOTH | stat.S_IWGRP | stat.S_IROTH | stat.S_IRGRP)):
                    print("file '%s' is unsecure.  Run 'chmod 600 %s' to fix this." % (filename, filename))
                else:
                    # after all that checking, load the YAML file containing the secure file
                    return self.loadYamlFile(filename)
            else:
                print("can not find creditials file '%s'." % filename)
            os._exit(100)
        else:
            path = os.path.join(config_dir, cred_file)
            print("can not read creditials file '%s'." % path)
        os._exit(100)

    def loadYamlFile(self, config_file):
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
