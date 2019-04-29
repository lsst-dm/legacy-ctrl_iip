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


from copy import deepcopy
import yaml
import datetime


class YamlHandler:
    def __init__(self, callback=None):
        self._consumer_callback = callback
        yaml.add_representer(datetime.time, self.dt_representer, Dumper=yaml.SafeDumper)
        yaml.add_constructor('datetime.time', self.dt_constructor, Loader=yaml.SafeLoader)
        self.dateformat = "%Y:%m:%dT%H%M%S.%f"

    def dt_constructor(self, loader, node):
        data = loader.construct_scalar(node)
        return datetime.datetime.strptime(data, self.dateformat)

    def dt_representer(self, dumper, data):
        s = data.strftime(self.dateformat)
        return dumper.represent_scalar('datetime.time', s)

    def yaml_callback(self, ch, method, properties, body):
        """ Decode the message body before consuming
            Setting the consumer callback function
        """
        pydict = self.decode_message(body)
        self._consumer_callback(ch, method, properties, pydict)

    def encode_message(self, dictValue):
        pydict = deepcopy(dictValue)
        yaml_body = yaml.safe_dump(pydict)
        return yaml_body

    def decode_message(self, body):
        tmpdict = yaml.safe_load(body)
        return tmpdict

    def print_yaml(self, body):
        print(str(body))
