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


from const import *
from copy import deepcopy
from toolsmod import get_timestamp
import yaml
import sys


class YamlHandler:
    def __init__(self, callback=None):
        self._consumer_callback = callback

    
    def yaml_callback(self, ch, method, properties, body): 
        """ Decode the message body before consuming
            Setting the consumer callback function
        """
        pydict = self.decode_message(body)
        self._consumer_callback(ch, method, properties, pydict)


    def encode_message(self, dictValue):
        pydict = deepcopy(dictValue)
        yaml_body = yaml.dump(dictValue)
        return yaml_body


    def decode_message(self, body):
        tmpdict = yaml.load(body) 
        return tmpdict


    def print_yaml(self, body):
        print(str(body))
