import toolsmod
import yaml
import logging
import pprint

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename='logs/MessageAuthority.log', level=logging.DEBUG, format=LOG_FORMAT)



class MessageAuthority:

    MSG_DICT = None

    def __init__(self, filename=None):
       self.prp = pprint.PrettyPrinter(indent=4) 
       self._message_dictionary_file = '/home/FM/src/git/ctrl_iip/python/lsst/iip/messages.yaml'
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
            raise Exception(e + "\n" + emsg)

        return self.dicts_shape_is_equal(msg, sovereign_msg)


    def get_dict_shape(self, d):
        if isinstance(d, dict):
            return {k:self.get_dict_shape(d[k]) for k in d}
        else:
            return None


    def dicts_shape_is_equal(self, d1, d2):
        print("============================")
        print("In MessageAuthority...printing d1 and d2")
        print("Here is d1...")
        self.prp.pprint(d1)
        print("Now here is d2...")
        self.prp.pprint(d2)
        print("============================")
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
