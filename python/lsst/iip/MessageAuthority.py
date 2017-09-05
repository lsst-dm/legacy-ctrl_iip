import toolsmod
import yaml
import logging

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename='logs/MessageAuthority.log', level=logging.DEBUG, format=LOG_FORMAT)



class MessageAuthority:

    MSG_DICT = None

    def __init__(self, filename=None):
       self._message_dictionary_file = 'messages.yaml'
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


    def get_message_keys(self, msg_type):
        keez = []
        try:
            keez = list(self.MSG_DICT['ROOT'][msg_type].keys())
        except KeyError as e:
            LOGGER.critical("Could not find message dictionary entry for %s message type" % msg_type)

        return keez

