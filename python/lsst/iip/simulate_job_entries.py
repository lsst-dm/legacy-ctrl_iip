from .toolsmod import get_epoch_timestamp
from .JobScoreboard import JobScoreboard
from time import sleep

class SimJobs:

    def __init__(self):

        self.jscbd = JobScoreboard()

        self.fill_job_scoreboard()



    def fill_job_scoreboard(self):
#S1
        self.jscbd.set_session("SU_7004")
        sleep(0.1)

#V1
        self.jscbd.set_visit("V_1001")
        sleep(0.2)

#J1
        self.jscbd.add_job("PP_14006", "IM4109", 161)
        sleep(0.4)

        self.jscbd.set_job_params("PP_14006", {'STATE':'BASE_RESOURCES_QUERY'})
        sleep(0.1)

        self.jscbd.set_job_params("PP_14006", {'STATE':'NCSA_RESOURCES_QUERY'})
        sleep(0.2)

        self.jscbd.set_job_params("PP_14006", {'STATE':'BASE_EVENT_PARAMS_SENT'})
        sleep(0.2)

        self.jscbd.set_job_params("PP_14006", {'STATE':'READY_FOR_EVENT'})
        sleep(0.1)

        self.jscbd.set_job_params("PP_14006", {'STATE':'READOUT'})
        sleep(0.1)

        self.jscbd.set_job_params("PP_14006", {'STATE':'READOUT_COMPLETE'})
        sleep(1.1)

        self.jscbd.set_job_params("PP_14006", {'STATE':'DELIVERY_COMPLETE'})
        sleep(2.1)

        self.jscbd.set_job_params("PP_14006", {'STATE':'_COMPLETE'})
        sleep(0.1)

        self.jscbd.set_job_status("PP_14006", 'COMPLETE')

#V2
        self.jscbd.set_visit("V_1002")
        sleep(0.2)

#J2
        self.jscbd.add_job("PP_14007", "IM_4110", 189)
        sleep(0.4)

        self.jscbd.set_job_params("PP_14007", {'STATE':'BASE_RESOURCES_QUERY'})
        sleep(0.1)

        self.jscbd.set_job_params("PP_14007", {'STATE':'NCSA_RESOURCES_QUERY'})
        sleep(0.1)

        self.jscbd.set_job_params("PP_14007", {'STATE':'BASE_EVENT_PARAMS_SENT'})
        sleep(0.3)

        self.jscbd.set_job_params("PP_14007", {'STATE':'READY_FOR_EVENT'})
        sleep(0.1)

        self.jscbd.set_job_params("PP_14007", {'STATE':'READOUT'})
        sleep(2.1)

        self.jscbd.set_job_params("PP_14007", {'STATE':'READOUT_COMPLETE'})
        sleep(3.4)

        self.jscbd.set_job_params("PP_14007", {'STATE':'DELIVERY_COMPLETE'})
        sleep(0.1)

        self.jscbd.set_job_params("PP_14007", {'STATE':'_COMPLETE'})
        sleep(0.1)

        self.jscbd.set_job_status("PP_14007", 'COMPLETE')

#J3
        self.jscbd.add_job("PP_14008", "IM_4111", 189)
        sleep(0.4)

        self.jscbd.set_job_params("PP_14008", {'STATE':'BASE_RESOURCES_QUERY'})
        sleep(0.1)

        self.jscbd.set_job_params("PP_14008", {'STATE':'NCSA_RESOURCES_QUERY'})
        sleep(0.1)
        

        self.jscbd.set_job_params("PP_14008", {'STATE':'SCRUBBED'})

        self.jscbd.set_job_status("PP_14008", 'TERMINATED')




#S2
        self.jscbd.set_session("SU_7005")
        sleep(0.1)

#V3
        self.jscbd.set_visit("V_1003")
        sleep(0.2)


        self.jscbd.add_job("PP_14009", "IM_4112", 161)
        sleep(0.4)

        self.jscbd.set_job_params("PP_14009", {'STATE':'BASE_RESOURCES_QUERY'})
        sleep(0.3)

        self.jscbd.set_job_params("PP_14009", {'STATE':'NCSA_RESOURCES_QUERY'})
        sleep(0.4)

        self.jscbd.set_job_params("PP_14009", {'STATE':'BASE_EVENT_PARAMS_SENT'})
        sleep(0.2)

        self.jscbd.set_job_params("PP_14009", {'STATE':'READY_FOR_EVENT'})
        sleep(0.1)

        self.jscbd.set_job_params("PP_14009", {'STATE':'READOUT'})
        sleep(1.1)

        self.jscbd.set_job_params("PP_14009", {'STATE':'READOUT_COMPLETE'})
        sleep(4.1)

        self.jscbd.set_job_params("PP_14009", {'STATE':'DELIVERY_COMPLETE'})
        sleep(2.8)

        self.jscbd.set_job_params("PP_14009", {'STATE':'_COMPLETE'})

        self.jscbd.set_job_status("PP_14009", 'COMPLETE')
        print("Job SCBD Load done")



def main():
    print("Starting SimJobs...")
    sj = SimJobs()
    print("SimJobs done loading job scoreboard")

if __name__ == "__main__": main()


