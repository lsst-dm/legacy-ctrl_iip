from subprocess import Popen, PIPE
import logging 
from logging.handlers import RotatingFileHandler 
from logging import Formatter

logger = logging.getLogger(__name__)
handler = RotatingFileHandler("../../logs/DAQForwarder.log", maxBytes=200000, backupCount=10)
logger.addHandler(handler)

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
formatter = Formatter(LOG_FORMAT)
handler.setFormatter(formatter) 

logger.setLevel(logging.DEBUG)

process = Popen(['./DAQForwarder'], stdout=PIPE, stderr=PIPE)
for c in iter(process.stdout.readline, ''): 
    logger.debug(c)
