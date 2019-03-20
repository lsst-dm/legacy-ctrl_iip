import sys
sys.path.append('../python/lsst/iip')
import toolsmod
import time
from SimplePublisher import SimplePublisher
from Consumer import Consumer
from AuxDevice import AuxDevice

# TODO: gonna be lsst unitTest
class AuxDeviceTestCase():
    AUX_ACK_QUEUE = 'at_foreman_ack_publish'
    DMCS_PUBLISH_QUEUE = 'at_foreman_consume'
    DMCS_ACK_QUEUE = 'dmcs_ack_consume'
    ARCHIVE_PUBLISH_QUEUE = 'archive_ctrl_publish'
    CFG_FILE = '../etc/config/L1SystemCfg_Test.yaml'
    FORWARDER = 'FORWARDER_99'
    ARCHIVE_CTRL = 'ARCHIVE_CTRL'
    JOB_NUM = 'job_100'
    SESSION_ID = 'session_100'
    IMAGE_ID = 'IMG_100'
    IMAGE_INDEX = 0
    IMAGE_SEQUENCE_NAME = 'seq_1000'
    IMAGES_IN_SEQUENCE = 1
    
    def setUp(self):
        # read CFG file 
        self.__cfg_root = toolsmod.intake_yaml_file(self.CFG_FILE)['ROOT']

        # setup forwarder publisher 
        self.__fwdr_cfg = self.__cfg_root['XFER_COMPONENTS']['AUX_FORWARDERS'][self.FORWARDER]
        self.__fwdr_amqp = 'amqp://' + \
                self.__fwdr_cfg['NAME'] + ':' + \
                self.__fwdr_cfg['NAME'] + '@' + \
                self.__cfg_root['BASE_BROKER_ADDR']
        self.__fwdr_publisher = SimplePublisher(self.__fwdr_amqp, 'YAML')

        # setup dmcs publisher
        self.__dmcs_amqp = 'amqp://' + \
                self.__cfg_root['DMCS_BROKER_PUB_NAME'] + ':' + \
                self.__cfg_root['DMCS_BROKER_PUB_PASSWD'] + '@' + \
                self.__cfg_root['BASE_BROKER_ADDR']
        self.__dmcs_publisher = SimplePublisher(self.__dmcs_amqp, 'YAML')

        # setup archiveController publisher
        self.__at_ctrl_amqp = 'amqp://' + \
                self.__cfg_root['ARCHIVE_BROKER_PUB_NAME'] + ':' + \
                self.__cfg_root['ARCHIVE_BROKER_PUB_PASSWD'] + '@' + \
                self.__cfg_root['BASE_BROKER_ADDR']
        self.__at_ctrl_publisher = SimplePublisher(self.__at_ctrl_amqp, 'YAML')

    def tearDown(self):
        pass 

    def test_at_start_integration(self): 
        msg = {}
        msg['MSG_TYPE'] = 'AT_START_INTEGRATION'
        msg['JOB_NUM'] = 'job_6'
        msg['SESSION_ID'] = self.SESSION_ID
        msg['IMAGE_ID'] = 'IMG_100'
        msg['IMAGE_INDEX'] = 0
        msg['IMAGE_SEQUENCE_NAME'] = 'seq_1'
        msg['IMAGES_IN_SEQUENCE'] = 1
        msg['RAFT_LIST'] = ['ats']
        msg['RAFT_CCD_LIST'] = [['wfs_ccd']]
        msg['REPLY_QUEUE'] = self.DMCS_ACK_QUEUE
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_100'
        self.__dmcs_publisher.publish_message(self.DMCS_PUBLISH_QUEUE, msg)

    def test_at_new_session(self): 
        msg = {} 
        msg['MSG_TYPE'] = 'AT_NEW_SESSION'
        msg['SESSION_ID'] = self.SESSION_ID
        msg['REPLY_QUEUE'] = self.DMCS_ACK_QUEUE
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_100'
        self.__dmcs_publisher.publish_message(self.DMCS_PUBLISH_QUEUE, msg)

    def test_at_fwdr_health_check_ack(self): 
        msg = {}
        msg['MSG_TYPE'] = 'AT_FWDR_HEALTH_CHECK_ACK'
        msg['ACK_BOOL'] = 'True'
        msg['COMPONENT'] = self.FORWARDER
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_100'
        self.__fwdr_publisher.publish_message(self.AUX_ACK_QUEUE, msg)

    def test_at_fwdr_xfer_params_ack(self):
        msg = {}
        msg['MSG_TYPE'] = 'AT_FWDR_XFER_PARAMS_ACK'
        msg['COMPONENT'] = self.FORWARDER
        msg['ACK_BOOL'] = "true"
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_100'
        self.__fwdr_publisher.publish_message(self.AUX_ACK_QUEUE, msg)

    def test_at_fwdr_end_readout_ack(self):
        # Currently not used
        msg = {} 
        msg['MSG_TYPE'] = 'AT_FWDR_END_READOUT_ACK'
        msg['COMPONENT'] = self.FORWARDER
        msg['JOB_NUM'] = self.JOB_NUM
        msg['SESSION_ID'] = self.SESSION_ID
        msg['IMAGE_ID'] = self.IMAGE_ID
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_101'
        msg['ACK_BOOL'] = 'True'
        result_set = {} 
        result_set['FILENAME_LIST'] = 'xxx'
        result_set['CHECKSUM_LIST'] = 'csum1lk123lkj'
        msg['RESULT_SET'] = result_set
        self.__fwdr_publisher.publish_message(self.AUX_ACK_QUEUE, msg)


    def test_at_items_xferd_ack(self):
        # Currently not used
        msg['MSG_TYPE'] = 'AT_ITEMS_XFERD_ACK'
        msg['COMPONENT'] = self.ARCHIVE_CTRL
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_100'
        msg['ACK_BOOL'] = True
        msg['REPLY_QUEUE'] = self.AUX_ACK_QUEUE
        result_set = {} 
        result_set['RECEIPT_LIST'] = ['receipt1']
        result_set['FILENAME_LIST'] = ['file1']
        msg['RESULT_SET'] = result_set
        self.__at_ctrl_publisher.publish_message(self.AUX_ACK_QUEUE, msg)

    def test_at_header_ready(self):
        msg = {} 
        msg['MSG_TYPE'] = 'AT_HEADER_READY'
        msg['IMAGE_ID'] = 'IMG_100'
        msg['FILENAME'] = 'http://141.142.238.177:8000/AT_O_20190312_000007.header'
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_100'
        msg['REPLY_QUEUE'] = 'at_foreman_ack_publish'
        self.__dmcs_publisher.publish_message(self.DMCS_PUBLISH_QUEUE, msg)

    def test_at_fwdr_header_ready_ack(self):
        msg = {} 
        msg['MSG_TYPE'] = 'AT_FWDR_HEADER_READY_ACK'
        msg['COMPONENT'] = self.FORWARDER
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_100'
        msg['ACK_BOOL'] = 'True'
        self.__fwdr_publisher.publish_message(self.AUX_ACK_QUEUE, msg)

    def test_new_archive_item_ack(self):
        # don't think this is used 
        pass

    def test_new_ar_archive_item_ack(self):
        # don't think this is used 
        pass

    def test_new_at_archive_item_ack(self):
        msg = {}
        msg['MSG_TYPE'] = 'NEW_AT_ARCHIVE_ITEM_ACK'
        msg['COMPONENT'] = self.ARCHIVE_CTRL
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_100'
        msg['TARGET_DIR'] = '/tmp/source'
        msg['ACK_BOOL'] = True
        msg['JOB_NUM'] = 'job_100'
        msg['IMAGE_ID'] = 'IMG_100'
        self.__at_ctrl_publisher.publish_message(self.ARCHIVE_PUBLISH_QUEUE, msg)

    def test_at_end_readout(self):
        msg = {} 
        msg['MSG_TYPE'] = 'AT_END_READOUT'
        msg['JOB_NUM'] = self.JOB_NUM
        msg['IMAGE_ID'] = self.IMAGE_ID
        msg['IMAGE_INDEX'] = self.IMAGE_INDEX
        msg['IMAGE_SEQUENCE_NAME'] = self.IMAGE_SEQUENCE_NAME
        msg['IMAGES_IN_SEQUENCE'] = self.IMAGES_IN_SEQUENCE
        msg['SESSION_ID'] = self.SESSION_ID
        msg['REPLY_QUEUE'] = self.DMCS_ACK_QUEUE
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_100'
        self.__dmcs_publisher.publish_message(self.DMCS_PUBLISH_QUEUE, msg)

    def run(self): 
        self.setUp()
        time.sleep(5)
        print('[x] Finished setting up publishers.')

        self.test_at_new_session() 
        time.sleep(5)
        print('[x] Finished setting up new session. Ready to receive params')
    
        print('[x] DMCS sending start integration to Aux')
        self.test_at_start_integration() 
        time.sleep(5)

        print('[x] Aux: Checking if there are healthy forwarders')
        self.test_at_fwdr_health_check_ack()
        time.sleep(5)
        print('[x] Received one healthy ack from forwarder')

        print('[x] Aux: Sending items to archive to ArchiveController')
        self.test_new_at_archive_item_ack()
        time.sleep(5)
        print('[x] Received ack from ArchiveController')
        
        print('[x] Aux: Sending parameters for file transfer to Forwarder')
        self.test_at_fwdr_xfer_params_ack()
        time.sleep(5)
        print('[x] Received transfer param ack from Forwarder')

        print('[x] DMCS sending header ready msg to Aux')
        self.test_at_header_ready()
        time.sleep(5)

        print('[x] Aux: Sending header ready message to Forwarder')
        self.test_at_fwdr_header_ready_ack()
        time.sleep(5)
        print('[x] Received header ready ack from Forwarder')

        print('[x] DMCS sending end readout to Aux') 
        self.test_at_end_readout()
        time.sleep(5)
        print('[DONE] Sender testing complete')

        self.tearDown()

def main(): 
    auxTest = AuxDeviceTestCase()
    auxTest.run()

if __name__ == '__main__': main()
