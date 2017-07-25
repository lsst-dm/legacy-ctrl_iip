import pika
import os.path
import hashlib
import yaml
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from const import *
import toolsmod  # here so reader knows where intake yaml method resides
from toolsmod import *
import _thread
import logging


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class ArchiveController:

    ARCHIVE_CTRL_PUBLISH = "archive_ctrl_publish"
    ARCHIVE_CTRL_CONSUME = "archive_ctrl_consume"
    ACK_PUBLISH = "ar_foreman_ack_publish"
    AUDIT_CONSUME = "audit_consume"
    YAML = 'YAML'
    RECEIPT_FILE = "/var/archive/archive_controller_receipt"



    def __init__(self, filename=None):
        self._session_id = None
        self._name = "ARCHIVE_CTRL"
        self._config_file = 'L1SystemCfg.yaml'
        if filename != None:
            self._config_file = filename

        cdm = toolsmod.intake_yaml_file(self._config_file)

        try:
            self._archive_name = cdm[ROOT]['ARCHIVE_BROKER_NAME']  # Message broker user/passwd for component
            self._archive_passwd = cdm[ROOT]['ARCHIVE_BROKER_PASSWD']
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            self._archive_xfer_root = cdm[ROOT]['ARCHIVE']['ARCHIVE_XFER_ROOT']
            if cdm[ROOT]['ARCHIVE']['CHECKSUM_ENABLED'] == 'yes':
                self.CHECKSUM_ENABLED = True
            else:
                self.CHECKSUM_ENABLED = False
        except KeyError as e:
            raise L1Error(e)


        self._base_msg_format = self.YAML

        if 'BASE_MSG_FORMAT' in cdm[ROOT]:
            self._base_msg_format = cdm[ROOT][BASE_MSG_FORMAT]

        self._base_broker_url = "amqp://" + self._archive_name + ":" + self._archive_passwd + "@" + str(self._base_broker_addr)

        LOGGER.info('Building _base_broker_url connection string for Archive Controller. Result is %s', 
                     self._base_broker_url)

        self._msg_actions = { 'ARCHIVE_HEALTH_CHECK': self.process_health_check,
                              'NEW_ARCHIVE_ITEM': self.process_new_archive_item,
                              'AR_ITEMS_XFERD': self.process_transfer_complete }

        self.setup_consumer()
        self.setup_publisher()


    def setup_consumer(self):
        LOGGER.info('Setting up archive consumers on %s', self._base_broker_url)
        LOGGER.info('Running start_new_thread for archive consumer')

        self._archive_consumer = Consumer(self._base_broker_url, self.ARCHIVE_CTRL_CONSUME, self._base_msg_format)
        try:
            _thread.start_new_thread( self.run_archive_consumer, ("thread-archive-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start Archive consumer thread, exiting...')
            raise L1Error

    def run_archive_consumer(self, threadname, delay):
        self._archive_consumer.run(self.on_archive_message)



    def setup_publisher(self):
        LOGGER.info('Setting up Archive publisher on %s using %s', self._base_broker_url, self._base_msg_format)
        self._archive_publisher = SimplePublisher(self._base_broker_url, self._base_msg_format)
        #self._audit_publisher = SimplePublisher(self._base_broker_url, self._base_msg_format)



    def on_archive_message(self, ch, method, properties, msg_dict):
        print("INCOMING On_archive_message, msg is:\n%s" % msg_dict)
        LOGGER.info('Message from Archive callback message body is: %s', str(msg_dict))
        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)


    def process_health_check(self, params):
        """Input 'params' for this method is a dict made up of:
           :param str 'MESSAGE_TYPE' value  is 'ARCHIVE_HEALTH_CHECK'
           :param str 'ACK_ID' value  is an alphanumeric string, with 
               the numeric part a momotonically increasing sequence. 
               This value is passed back to the foreman and used to keep 
               track of acknowledgement time.
           :param str 'SESSION_ID' Might be useful for the controller to 
               generate a target location for new items to be archived?
        """
        self.send_audit_message("received_")
        self.send_health_ack_response("ARCHIVE_HEALTH_CHECK_ACK", params)
        

    def process_new_archive_item(self, params):
        print("Incoming archive ctrl new archive item msg is:\n%s" % params)
        self.send_audit_message("received_", params)
        target_dir = self.construct_send_target_dir(params)
        self.send_new_item_ack(target_dir, params)


    def process_transfer_complete(self, params):
        print("Incoming process transfer msg is:\n%s" % params)
        print("\n\n") 
        transfer_results = {}
        ccd_list = params['CCD_LIST']
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("The CCD_LIST is %s" % ccd_list)
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        ccds = list(ccd_list.keys())
        print("The ccds are %s" % ccds)
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        for ccd in ccds:
            pathway = ccd_list[ccd]['FILENAME']
            csum = ccd_list[ccd]['CHECKSUM']
            transfer_results[ccd] = self.check_transferred_file(pathway, csum)
        self.send_transfer_complete_ack(transfer_results, params)


    def check_transferred_file(self, pathway, csum):
        if not os.path.isfile(pathway):
            return (-1)

        if self.CHECKSUM_ENABLED:
            with open(pathway) as file_to_calc:
                data = file_to_calc.read()
                resulting_md5 = hashlib.md5(data).hexdigest()

                if resulting_md5 != csum:
                    return (0)

        return self.next_receipt_number()


    def next_receipt_number(self):
        last_receipt = toolsmod.intake_yaml_file(self.RECEIPT_FILE)
        current_receipt = int(last_receipt['RECEIPT_ID']) + 1
        session_dict = {}
        session_dict['RECEIPT_ID'] = current_receipt
        toolsmod.export_yaml_file(self.RECEIPT_FILE, session_dict)
        return current_receipt


    def send_health_ack_response(self, type, params):
        try:
            ack_id = params.get("ACK_ID")
            self._current_session_id = params.get("SESSION_ID")
        except:
            if ack_id == None:
                LOGGER.info('%s failed, missing ACK_ID field', type)
                raise L1MessageError("Missing ACK_ID message param needed for send_ack_response")
            else:
                LOGGER.info('%s failed, missing SESSION_ID field', type)
                raise L1MessageError("Missing SESSION_ID param needed for send_ack_response")

        msg_params = {}
        msg_params[MSG_TYPE] = type
        msg_params[COMPONENT_NAME] = self._name
        msg_params[ACK_BOOL] = "TRUE"
        msg_params['ACK_ID'] = ack_id
        LOGGER.info('%s sent for ACK ID: %s', type, timed_ack)
        self._archive_publisher.publish_message(self.ACK_PUBLISH, msg_params)


    def send_audit_message(self, prefix, params):
        audit_params = {}
        audit_params['SUB_TYPE'] = str(prefix) + str(params['MSG_TYPE']) + "_msg"
        audit_params['DATA_TYPE'] = self._name
        audit_params['TIME'] = get_epoch_timestamp()
        self._archive_publisher.publish_message(self.AUDIT_CONSUME, audit_params)



    def construct_send_target_dir(self, params):
        #session = params['SESSION_ID']
        visit = params['VISIT_ID']
        image = params['IMAGE_ID']
        ack_id = params['ACK_ID']
        #target_dir = self._archive_xfer_root + "_" + str(image_type) + "_" + str(session) + "_" + str(visit) + "_" + str(image)
        target_dir_visit = self._archive_xfer_root + visit + "/"
        target_dir_image = self._archive_xfer_root + visit + "/" + str(image) + "/"

        if os.path.isdir(target_dir_visit):
            pass
        else:
            os.mkdir(target_dir_visit, 0o766)

        if os.path.isdir(target_dir_image):
            pass
        else:
            os.mkdir(target_dir_image, 0o766)

        return target_dir_image


    def send_new_item_ack(self, target_dir, params):
        ack_params = {}
        ack_params[MSG_TYPE] = 'NEW_ARCHIVE_ITEM_ACK'
        ack_params['TARGET_DIR'] = target_dir
        ack_params['ACK_ID'] = params['ACK_ID']
        ack_params['JOB_NUM'] = params['JOB_NUM']
        ack_params['IMAGE_ID'] = params['IMAGE_ID']
        ack_params['COMPONENT_NAME'] = self._name
        ack_params['ACK_BOOL'] = True
        print("Outgoing new archive item ack is:\n%s" % ack_params)
        self._archive_publisher.publish_message(self.ACK_PUBLISH, ack_params)


    def send_transfer_complete_ack(self, transfer_results, params):
        ack_params = {}
        keez = list(params.keys())
        for kee in keez:
            if kee == 'MSG_TYPE' or kee == 'CCD_LIST':
                continue
            ### XXX FIXME Dump loop and just pull the correct values from the input params
            ack_params[kee] = params[kee]

        
        ack_params['MSG_TYPE'] = 'AR_ITEMS_XFERD_ACK'
        ack_params['COMPONENT_NAME'] = self._name
        ack_params['ACK_ID'] = params['ACK_ID']
        ack_params['ACK_BOOL'] = True
        ack_params['RESULTS'] = transfer_results

        self._archive_publisher.publish_message(self.ACK_PUBLISH, ack_params)




def main():
    logging.basicConfig(filename='logs/BaseForeman.log', level=logging.INFO, format=LOG_FORMAT)
    a_c = ArchiveController()
    print("Beginning ArchiveController event loop...")
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print("")
    print("Archive Controller Done.")



if __name__ == "__main__": main()
