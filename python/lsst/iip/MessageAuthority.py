###############################################################################
###############################################################################
## Copyright 2000-2018 The Board of Trustees of the University of Illinois.
## All rights reserved.
##
## Developed by:
##
##   LSST Image Ingest and Distribution Team
##   National Center for Supercomputing Applications
##   University of Illinois
##   http://www.ncsa.illinois.edu/enabling/data/lsst
##
## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal with the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:
##
##   Redistributions of source code must retain the above copyright
##   notice, this list of conditions and the following disclaimers.
##
##   Redistributions in binary form must reproduce the above copyright
##   notice, this list of conditions and the following disclaimers in the
##   documentation and/or other materials provided with the distribution.
##
##   Neither the names of the National Center for Supercomputing
##   Applications, the University of Illinois, nor the names of its
##   contributors may be used to endorse or promote products derived from
##   this Software without specific prior written permission.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
## IN NO EVENT SHALL THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR
## ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
## CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
## WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE SOFTWARE.



import toolsmod
import yaml
import logging
import pprint
import traceback

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename='logs/MessageAuthority.log', level=logging.DEBUG, format=LOG_FORMAT)



class MessageAuthority:

    MSG_DICT = None

    def __init__(self, filename=None):
       self.prp = pprint.PrettyPrinter(indent=4) 
       self._message_dictionary_file = './messages.yaml'
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
