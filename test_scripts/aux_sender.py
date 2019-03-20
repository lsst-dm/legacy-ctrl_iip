import sys
sys.path.append('../python/lsst/iip')
from SimplePublisher import SimplePublisher
from Consumer import Consumer
from AuxDevice import AuxDevice
import toolsmod

# TODO: gonna be lsst unitTest
class AuxDeviceTestCase():
    self.FWDR_ACK_QUEUE = 'at_foreman_ack_publish'
    self.DMCS_PUBLISH_QUEUE = 'at_foreman_consume'
    self.ARCHIVE_PUBLISH_QUEUE = 'archive_ctrl_publish'
    self.CFG_FILE = '../etc/config/L1SystemCfg_Test.yaml'
    self.FORWARDER = 'FORWARDER_99'
    
    def setUp(self):
        self.__cfg_root = toolsmod.intake_yaml_file(self.CFG_FILE)['ROOT']
        self.__fwdr_cfg = self.__cfg_root['AUX_FORWARDERS'][self.FORWARDER]
        self.__fwdr_amqp = 'amqp://' + \
                self.__fwdr_cfg['NAME'] + ':' + \
                self.__fwdr_cfg['NAME'] + '@' + \
                self.__cfg_root['BASE_BROKER_ADDR']
        self.__fwdr_publisher = SimplePublisher(self.__fwdr_amqp, 'YAML')

        self.__dmcs_amqp = 'amqp://' + \
                self.__cfg_root['DMCS_BROKER_PUB_NAME'] + ':' + \
                self.__cfg_root['DMCS_BROKER_PUB_PASSWD'] + '@' + \
                self.__cfg_root['BASE_BROKER_ADDR']
        self.__dmcs_publisher = SimplePublisher(self.__dmcs_amqp, 'YAML')

        self.__at_ctrl_amqp = 'amqp://' + \
                self.__cfg_root['ARCHIVE_BROKER_PUB_NAME'] + ':' + \
                self.__cfg_root['ARCHIVE_BROKER_PUB_PASSWD'] + '@' + \
                self.__cfg_root['BASE_BROKER_ADDR']
        self.__at_ctrl_publisher = SimplePublisher(self.__at_ctrl_amqp, 'YAML')

    def tearDown(self):
        pass 

    def test_at_start_integration(self): 
        pass

    def test_at_new_session(self): 
        pass

    def test_at_fwdr_health_check_ack(self): 
        msg = {}
        msg['MSG_TYPE'] = 'AT_FWDR_HEALTH_CHECK_ACK'
        msg['ACK_BOOL'] = 'True'
        msg['COMPONENT'] = self.FORWARDER
        msg['ACK_ID'] = 'AT_FWDR_HEALTH_CHECK_ACK_100'
        self.__fwdr_publisher.publish_message(self.FWDR_ACK_QUEUE, msg)

    def test_at_fwdr_xfer_params_ack(self):
        pass

    def test_at_fwdr_end_readout_ack(self):
        pass

    def test_at_items_xferd_ack(self):
        pass

    def test_at_header_ready(self):
        msg = {} 
        msg['MSG_TYPE'] = 'AT_HEADER_READY'
        msg['IMAGE_ID'] = 'IMG_100'
        msg['FILENAME'] = 'http://141.142.238.177:8000/AT_O_20190312_000007.header'
        msg['ACK_ID'] = 'AT_HEADER_READY_ACK_100'
        msg['REPLY_QUEUE'] = 'at_foreman_ack_publish'
        self.__dmcs_publisher.publish_message(self.DMCS_PUBLISH_QUEUE, msg)

    def test_at_fwdr_header_ready_ack(self):
        msg = {} 
        msg['MSG_TYPE'] = 'AT_FWDR_HEADER_READY_ACK'
        msg['COMPONENT'] = self.FORWARDER
        msg['ACK_ID'] = 'AT_FWDR_HEADER_READY_ACK_100'
        msg['ACK_BOOL'] = 'True'
        self.__fwdr_publisher.publish_message(self.FWDR_ACK_QUEUE, msg)

    def test_new_archive_item_ack(self):
        # don't think this is used 
        pass

    def test_new_ar_archive_item_ack(self):
        # don't think this is used 
        pass

    def test_new_at_archive_item_ack(self):
        msg = {}
        msg['MSG_TYPE'] = 'NEW_AT_ARCHIVE_ITEM_ACK'
        msg['COMPONENT'] = 'ARCHIVE_CTRL'
        msg['ACK_ID'] = 'ack_100'
        msg['TARGET_DIR'] = '/tmp/source'
        msg['ACK_BOOL'] = True
        msg['JOB_NUM'] = 'job_100'
        msg['IMAGE_ID'] = 'IMG_100'
        self.__at_ctrl_publisher.publish_message(self.ARCHIVE_PUBLISH_QUEUE, msg)

    def test_at_end_readout(self):
        pass

