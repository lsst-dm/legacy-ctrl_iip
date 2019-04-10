from lsst.ctrl.iip.Consumer import Consumer
from lsst.ctrl.iip.SimplePublisher import SimplePublisher
from lsst.ctrl.iip.iip_base import iip_base

class Sender(iip_base):
    def __init__(self, filename):
        self._config_file = self.loadConfigFile(filename)
        self._credentials = self.loadConfigFile('credentials.yaml')

        self._session_id = self._config_file['SESSION_ID']
        self._visit_id = self._config_file['VISIT_ID']
        self._job_num = self._config_file['JOB_NUM']

    def get_timer(self):
        return self._config_file['SLEEP_TIMER']

    def get_amqp_url(self, username, password):
        amqp_url = 'amqp://' + \
                self._credentials[username] + ':' + \
                self._credentials[password] + '@' + \
                self._config_file['BASE_BROKER_ADDR'] + '/%2f' + \
                self._config_file['VHOST']
        return amqp_url

    def get_single_forwarder(self): 
        return self._config_file['FORWARDERS'][0]

    def get_many_forwarders(self):
        return self._config_file['FORWARDERS']

    def get_single_image(self):
        return self._config_file['IMAGES'][0]

    def get_many_images(self):
        return self._config_file['IMAGES']

    def get_target_location(self, device):
        archive = self._config_file['ARCHIVE'][device]
        target_location = archive['NAME'] + '@' +\
                archive['IP'] + ':' + \
                archive['XFER_ROOT']
        return target_location

    def get_partition(self, device):
        return (self._config_file['PARTITION'][device]['RAFT'], 
            self._config_file['PARTITION'][device]['CCD'])

    def get_header_file(self):
        return self._config_file['HEADER_FILE']

    def get_publisher(self, username, password):
        url = self.get_amqp_url(username, password)
        return SimplePublisher(url, 'YAML')

