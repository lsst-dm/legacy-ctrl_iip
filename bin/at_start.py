from SALPY_ATArchiver import *


class Commander:
    def __init__(self):
        self.mgr = SAL_ATArchiver()
        self.timeout = 10
        

    def start(self, withState):
        data = ATArchiver_command_startC();
        self.mgr.salCommand("ATArchiver_command_start")
        data.device = ""
        data.property = ""
        data.action = ""
        data.settingsToApply = withState

        cmdId = self.mgr.issueCommand_start(data)
        status = self.mgr.waitForCompletion_start(cmdId, self.timeout)

        print(f"status = {status}")

if __name__ == "__main__":
    cmdr = Commander()
    cmdr.start("Normal")
    cmdr.mgr.salShutdown()

    
