import time
from Sender import Sender

class ForwarderSender(Sender):
    def __init__(self, filename):
        Sender.__init__(self, filename)
        self._aux_publisher = self.get_publisher(
                'AUX_PUB',
                'AUX_PUB')

    def send_health_check(self, fwdr):
        msg = {}
        msg['MSG_TYPE'] = 'AT_FWDR_HEALTH_CHECK'
        msg['REPLY_QUEUE'] = fwdr['PUBLISH_QUEUE']
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_ACK_test'
        self._aux_publisher.publish_message(fwdr['CONSUME_QUEUE'], msg)

    def send_xfer_params(self, target_location, fwdr, image, raft_list, ccd_list): 
        msg = {}
        msg['MSG_TYPE'] = 'AT_FWDR_XFER_PARAMS'
        msg['SESSION_ID'] = self._session_id
        msg['VISIT_ID'] = self._visit_id
        msg['JOB_NUM'] = self._job_num
        msg['IMAGE_ID'] = image['IMAGE_ID']
        msg['TARGET_LOCATION'] = target_location
        msg['REPLY_QUEUE'] = fwdr['PUBLISH_QUEUE']
        msg['DAQ_ADDR'] = 'LOCAL'
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_ACK_test'

        msg['XFER_PARAMS'] = {}
        msg['XFER_PARAMS']['AT_FWDR'] = fwdr['NAME']
        msg['XFER_PARAMS']['RAFT_LIST'] = raft_list
        msg['XFER_PARAMS']['RAFT_CCD_LIST'] = ccd_list
        self._aux_publisher.publish_message(fwdr['CONSUME_QUEUE'], msg)

    def send_end_readout(self, fwdr, image):
        msg = {}
        msg['MSG_TYPE'] = 'AT_FWDR_END_READOUT'
        msg['SESSION_ID'] = self._session_id
        msg['VISIT_ID'] = self._visit_id
        msg['JOB_NUM'] = self._job_num
        msg['IMAGE_ID'] = image['IMAGE_ID']
        msg['REPLY_QUEUE'] = fwdr['PUBLISH_QUEUE']
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_ACK_test'
        self._aux_publisher.publish_message(fwdr['CONSUME_QUEUE'], msg)

    def send_header_ready(self, fwdr, image):
        msg = {} 
        msg['MSG_TYPE'] = 'AT_FWDR_HEADER_READY'
        msg['FILENAME'] = self.get_header_file()
        msg['IMAGE_ID'] = image['IMAGE_ID']
        msg['ACK_ID'] = msg['MSG_TYPE'] + '_ACK_test'
        msg['REPLY_QUEUE'] = fwdr['PUBLISH_QUEUE']
        self._aux_publisher.publish_message(fwdr['CONSUME_QUEUE'], msg) 

    def run_sequence(self, target_location, fwdr, image, raft, ccd):
        self.send_health_check(fwdr)
        print('[x] Sending Health check message to ' + fwdr['NAME'])
        time.sleep(4)

        self.send_xfer_params(target_location, fwdr, image, raft, ccd)
        print('[x] Sending transfer params message to ' + fwdr['NAME'])
        time.sleep(4)

        self.send_end_readout(fwdr, image)
        print('[x] Sending end readout message to ' + fwdr['NAME'])
        time.sleep(4)

        self.send_header_ready(fwdr, image)
        print('[x] Sending header_ready message to ' + fwdr['NAME'])
        time.sleep(4)

        print('[DONE] Sending sequence complete for ' + fwdr['NAME'])

    def run_oneFwdr_oneImage(self, device):
        fwdr = self.get_single_forwarder()
        raft_list, ccd_list = self.get_partition(device)
        image = self.get_single_image()
        target_location = self.get_target_location(device)
        self.run_sequence(target_location, fwdr, image, raft_list, ccd_list)
        
    def run_oneFwdr_manyImages(self):
        pass

    def run_manyFwdrs_manyImages(self):
        pass

def main():
    sender = ForwarderSender('TestStandNCSA.yaml')     
    sender.run_oneFwdr_oneImage('AT')

if __name__ == '__main__':  main()
