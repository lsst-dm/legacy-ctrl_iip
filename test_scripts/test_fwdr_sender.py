from lsst.ctrl.iip.Consumer import Consumer
from lsst.ctrl.iip.SimplePublisher import SimplePublisher
from lsst.ctrl.iip.iip_base import iip_base

class ForwarderTestCase(): 
    def setUp(self):
        self._cfg_root = iip_base.loadConfigFile('L1SystemCfg_Test.yaml')['ROOT'];
        self._img_id = self._cfg_root['TEST']['IMAGE_ID'];
        self._job_num = self._cfg_root['TEST']['JOB_NUM'];
        self._visit_id  = self._cfg_root['TEST']['VISIT_ID'];
        self._session_id  = self._cfg_root['TEST']['SESSION_ID'];
        self._fwdr = self._cfg_root['AUX_FORWARDERS']['FORWARDER_99']
        self._fwdr_consumeq = self._fwdr['CONSUME_QUEUE']
        self._fwdr_publishq = self._fwdr['PUBLISH_QUEUE']
        self._target_location = self._cfg_root['ARCHIVE']['ARCHIVE_NAME'] + \
            '@' + \
            self._cfg_root['ARCHIVE']['ARCHIVE_IP'] + ':' + \
            self._cfg_root['ARCHIVE']['ARCHIVE_XFER_ROOT'] 

    def tearDown(self):
        pass

    def test_at_fwdr_health_check(self):
        msg = {}
        msg['MSG_TYPE'] = 'AT_FWDR_HEALTH_CHECK'
        msg['REPLY_QUEUE'] = self._fwdr_publishq
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_ACK_TEST'
        sp1.publish_message(self._fwdr_consumeq, msg)

    def test_at_fwdr_xfer_params(self):
        msg = {}
        msg['MSG_TYPE'] = 'AT_FWDR_XFER_PARAMS'
        msg['JOB_NUM'] = self._job_num
        msg['IMAGE_ID'] = self._img_id
        msg['TARGET_LOCATION'] = self._target_location
        msg['SESSION_ID'] = self._session_id
        msg['REPLY_QUEUE'] = self._fwdr_publishq
        msg['DAQ_ADDR'] = 'LOCAL'
        msg['VISIT_ID'] = self._visit_id
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_ACK_TEST'
        # These lists are prepped for sending directly to a forwarder
        msg['XFER_PARAMS'] = {}
        msg['XFER_PARAMS']['AT_FWDR'] = 'FORWARDER_F99'
        msg['XFER_PARAMS']['RAFT_LIST'] = ['ats']
        msg['XFER_PARAMS']['RAFT_CCD_LIST'] = [['11']]
        sp1.publish_message(self._fwdr_consumeq, msg)

    def test_at_fwdr_end_readout(self):
        msg = {}
        msg['MSG_TYPE'] = 'AT_FWDR_END_READOUT'
        msg['IMAGE_ID'] = self._image_id
        msg['JOB_NUM'] = self._job_num
        msg['VISIT_ID'] = self._visit_id
        msg['SESSION_ID'] = self._session_id
        msg['REPLY_QUEUE'] = self._fwdr_publishq
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_ACK_TEST'
        sp1.publish_message(self._fwdr_consumeq, msg)

    def test_at_fwdr_header_ready(self):
        msg = {} 
        msg['MSG_TYPE'] = 'AT_FWDR_HEADER_READY'
        msg['FILENAME'] = self._header_path + '/' + self._image_id + '.header'
        msg['IMAGE_ID'] = self._image_id
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_ACK_TEST'
        msg['REPLY_QUEUE'] = self._fwdr_publishq
        sp1.publish_message(self._fwdr_consumeq, msg) 

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

def main(): 
    auxTest = AuxDeviceTestCase()
    auxTest.run()

if __name__ == '__main__': main()
