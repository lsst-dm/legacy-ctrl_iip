import pika
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from const import *
from toolsmod import *
import thread
import logging


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class ArchiveController:

    ARCHIVE_PUBLISH = "archive_publish"
    ARCHIVE_CONSUME = "archive_consume"
    ACK_PUBLISH = "ack_publish"
    YAML = 'YAML'



    def __init__(self, filename=None):
        self._session_id = None
        self._name = "ARCHIVE_CONTROLLER"
        self._config_file = 'ForemanCfg.yaml'
        if filename != None:
            self._config_file = filename

        cdm = self.intake_yaml_file(self._config_file)

        try:
            self._archive_name = cdm[ROOT][ARCHIVE_BROKER_NAME]  # Message broker user/passwd for component
            self._archive_passwd = cdm[ROOT][ARCHIVE_BROKER_PASSWD]
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
        except KeyError as e:
            print "Yaml config dictionary error, %s" % e
            raise L1Error


        self._base_msg_format = self.YAML

        if 'BASE_MSG_FORMAT' in cdm[ROOT]:
            self._base_msg_format = cdm[ROOT][BASE_MSG_FORMAT]

        self._base_broker_url = "amqp://" + self._archive_name + ":" + self._archive_passwd + "@" + 
                                 str(self._base_broker_addr)

        LOGGER.info('Building _base_broker_url connection string for Archive Controller. Result is %s', 
                     self._base_broker_url)

        self._msg_actions = { 'ARCHIVE_HEALTH_CHECK': self.process_health_check,
                              'NEW_ARCHIVE_ITEM': self.process_new_archive_item,
                              'ARCHIVE_ITEM_TRANFER_COMPLETE': self.process_transfer_complete }

        self.setup_consumer()
        self.setup_publishers()


    def setup_consumer(self):
        LOGGER.info('Setting up archive consumers on %s', self._base_broker_url)
        LOGGER.info('Running start_new_thread for archive consumer')

        self._archive_consumer = Consumer(self._base_broker_url, self.ARCHIVE_CONSUME, self._base_msg_format)
        try:
            thread.start_new_thread( self.run_archive_consumer, ("thread-archive-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start Archive consumer thread, exiting...')
            raise L1Error

    def run_archive_consumer(self, threadname, delay):
        self._archive_consumer.run(self.on_archive_message)



    def setup_publisher(self):
        LOGGER.info('Setting up Archive publisher on %s using %s', self._base_broker_url, self._base_msg_format)
        self._archive_publisher = SimplePublisher(self._base_broker_url, self._base_msg_format)
        self._audit_publisher = SimplePublisher(self._base_broker_url, self._base_msg_format)


    def on_archive_message(self, ch, method, properties, msg_dict):
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
        self.send_audit_message("received_")
        target_dir = self.construct_send_target_dir(params)


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
        self._publisher.publish_message(self.ACK_PUBLISH, msg_params)


    def send_audit_message(self, prefix):
        audit_params = {}
        audit_params['SUB_TYPE'] = str(prefix) + str(params['MSG_TYPE']) + "_msg"
        audit_params['DATA_TYPE'] = self._name
        audit_params['TIME'] = get_epoch_timestamp()
        self._publisher(self.AUDIT_CONSUME, audit_params)



    def construct_send_target_dir_ack(self, params):
        mtype = "NEW_ARCHIVE_ITEM_ACK"
        image_type = params['IMAGE_TYPE']
        session = params['SESSION_ID']
        visit = params['VISIT_ID']
        image = params['IMAGE_ID']
        ack_id = params['ACK_ID']
        target_dir = self._target_dir_prefix + "_" + 
                     str(image_type) + "_" + 
                     str(session) + "_" + 
                     str(visit) + "_" + 
                     str(image)
        os.mkdir(target_dir, 0766)

        ack_params = {}
        ack_params['MSG_TYPE'] = mtype
        ack_params['COMPONENT_NAME'] = self._name
        ack_params['ACK_ID'] = ack_id
        ack_params['ACK_BOOL'] = True
        ack_params['TARGET'] = target_dir
        ack_params['SESSION_ID'] = image
        ack_params['VISIT_ID'] = image
        ack_params['IMAGE_ID'] = image
        ack_params['IMAGE_TYPE'] = image_type
        
        LOGGER.info('%s sent for ACK ID: %s', mtype, ack_id)
        self._publisher.publish_message(self.ACK_PUBLISH, ack_params)

        return target_dir


    def process_transfer_complete(self, params):
        pass


