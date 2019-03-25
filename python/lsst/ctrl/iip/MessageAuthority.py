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


import yaml
import logging
import pprint
import traceback
import lsst.ctrl.iip.toolsmod

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename='logs/MessageAuthority.log', level=logging.DEBUG, format=LOG_FORMAT)



class MessageAuthority:

    MSG_DICT = None

    def __init__(self, filename=None):
       self.prp = pprint.PrettyPrinter(indent=4) 
       self._message_dictionary_file = '../config/messages.yaml'
       if filename != None:
           self._message_dictionary_file = filename


       LOGGER.info('Reading YAML message dictionary file %s' % self._message_dictionary_file)

       try:
           self.MSG_DICT = toolsmod.intake_yaml_file(self._message_dictionary_file)
       except IOError as e:
           trace = traceback.print_exc()
           emsg = "Unable to find Message Dictionary Yaml file %s\n" % self._message_dictionary_file
           LOGGER.critical(emsg + trace)
           sys.exit(101)


    def check_message_shape(self, msg):
        try:
            msg_type = msg['MSG_TYPE']
            sovereign_msg = self.MSG_DICT['ROOT'][msg_type]
        except KeyError as e:
            emsg = "MSG_TYPE %s is not found in the Message Authority. Msg body is %s\n" % (msg_type, msg)
            raise Exception(str(e) + "\n" + emsg)

        return self.dicts_shape_is_equal(msg, sovereign_msg)


    def get_dict_shape(self, d):
        if isinstance(d, dict):
            return {k:self.get_dict_shape(d[k]) for k in d}
        else:
            return None


    def dicts_shape_is_equal(self, d1, d2):
        return self.get_dict_shape(d1) == self.get_dict_shape(d2)


    def get_message_keys(self, msg_type):
        keez = []
        try:
            keez = list(self.MSG_DICT['ROOT'][msg_type].keys())
        except KeyError as e:
            LOGGER.critical("Could not find message dictionary entry for %s message type" % msg_type)

        return keez


def main():
    ma = MessageAuthority()
    print("Beginning MessageAuthority event loop...")
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print("")
    print("MessageAuthority Done.")


if __name__ == "__main__": main()
