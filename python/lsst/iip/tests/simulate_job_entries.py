from toolsmod import get_epoch_timestamp
from ForwarderScoreboard import ForwarderScoreboard
from JobScoreboard import JobScoreboard
from AckScoreboard import AckScoreboard

class SimJobs:

    def __init__(self, scoreboard):

        fscbd = ForwarderScoreboard()
        jscbd = JobScoreboard()
        ascbd = AckScoreboard()
