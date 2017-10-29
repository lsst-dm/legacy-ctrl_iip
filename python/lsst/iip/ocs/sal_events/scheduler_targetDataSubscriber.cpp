
/*
 * This file contains the implementation for the 'scheduler_targetSubscriber' executable.
 *
 ***/


#include <string>
#include <sstream>
#include <iostream>
#include "SAL_scheduler.h"
#include "ccpp_sal_scheduler.h"
#include "os.h"
#include <stdlib.h>

#include "example_main.h"
#include "SimplePublisher.h" 

using namespace DDS;
using namespace scheduler;

/* entry point exported and demangled so symbol can be found in shared library */
extern "C"
{
  OS_API_EXPORT
  int SALTelemetrySubscriber(int argc, char *argv[]);
}


int SALTelemetrySubscriber(char *topic_name)
{
  os_time delay_10ms = { 0, 10000000 };
  scheduler_targetC SALInstance;


#ifdef SAL_SUBSYSTEM_ID_IS_KEYED
  int schedulerID = 1;
  if (getenv("LSST_scheduler_ID") != NULL) {
     sscanf(getenv("LSST_scheduler_ID"),"%d",&schedulerID);
  } 
  SAL_scheduler mgr = SAL_scheduler(schedulerID);
#else
  SAL_scheduler mgr = SAL_scheduler();
#endif

  mgr.salTelemetrySub(topic_name);

  cout << "=== [Subscriber] Ready ..." << endl;

  ReturnCode_t status =  - 1;
  int count = 0;
  SimplePublisher *publisher = new SimplePublisher("amqp://TARGET:TARGET@141.142.208.209/%2fbunny"); 
  while (1)
  {
    status = mgr.getNextSample_target(&SALInstance);
    if (status == SAL__OK) {
// INSERT_SAL_SUBC
    cout << "    targetId : " << SALInstance.targetId << endl;
    cout << "    fieldId : " << SALInstance.fieldId << endl;
    cout << "    groupId : " << SALInstance.groupId << endl;
    cout << "    filter : " << SALInstance.filter << endl;
    cout << "    request_time : " << SALInstance.request_time << endl;
    cout << "    request_mjd : " << SALInstance.request_mjd << endl;
    cout << "    ra : " << SALInstance.ra << endl;
    cout << "    decl : " << SALInstance.decl << endl;
    cout << "    angle : " << SALInstance.angle << endl;
    cout << "    num_exposures : " << SALInstance.num_exposures << endl;
       cout << "    exposure_times : " << SALInstance.exposure_times[0] << endl;
    cout << "    airmass : " << SALInstance.airmass << endl;
    cout << "    sky_brightness : " << SALInstance.sky_brightness << endl;
    cout << "    cloud : " << SALInstance.cloud << endl;
    cout << "    seeing : " << SALInstance.seeing << endl;
    cout << "    slew_time : " << SALInstance.slew_time << endl;
    cout << "    cost : " << SALInstance.cost << endl;
    cout << "    prop_boost : " << SALInstance.prop_boost << endl;
    cout << "    rank : " << SALInstance.rank << endl;
    cout << "    num_proposals : " << SALInstance.num_proposals << endl;
       cout << "    proposal_Ids : " << SALInstance.proposal_Ids[0] << endl;
       cout << "    proposal_values : " << SALInstance.proposal_values[0] << endl;
       cout << "    proposal_needs : " << SALInstance.proposal_needs[0] << endl;
       cout << "    proposal_bonuses : " << SALInstance.proposal_bonuses[0] << endl;
       cout << "    proposal_boosts : " << SALInstance.proposal_boosts[0] << endl;
    cout << "    moon_ra : " << SALInstance.moon_ra << endl;
    cout << "    moon_dec : " << SALInstance.moon_dec << endl;
    cout << "    moon_alt : " << SALInstance.moon_alt << endl;
    cout << "    moon_az : " << SALInstance.moon_az << endl;
    cout << "    moon_phase : " << SALInstance.moon_phase << endl;
    cout << "    moon_distance : " << SALInstance.moon_distance << endl;
    cout << "    sun_alt : " << SALInstance.sun_alt << endl;
    cout << "    sun_az : " << SALInstance.sun_az << endl;
    cout << "    sun_ra : " << SALInstance.sun_ra << endl;
    cout << "    sun_dec : " << SALInstance.sun_dec << endl;
    cout << "    solar_elong : " << SALInstance.solar_elong << endl;

    ostringstream msg; 
    msg << "{ MSG_TYPE: SEQ_TARGET_VISIT" 
        << ", TARGET_ID : " << SALInstance.targetId
        << ", FIELD_ID : " << SALInstance.fieldId
        << ", GROUP_ID : " << SALInstance.groupId
        << ", FILTER : " << SALInstance.filter
        << ", REQUEST_TIME : " << SALInstance.request_time
        << ", REQUEST_MJD : " << SALInstance.request_mjd
        << ", RA: " << SALInstance.ra
        << ", DECL: " << SALInstance.decl
        << ", ANGLE: " << SALInstance.angle
        << ", NUM_EXPOSURES: " << SALInstance.num_exposures
        << ", EXPOSURE_TIMES: " << SALInstance.exposure_times[0] << "}"; 
       
    publisher->publish_message("ocs_dmcs_consume", msg.str());
    }
    os_nanoSleep(delay_10ms);
    ++count;
  }

  //cleanup
  mgr.salShutdown();

  return 0;
}

int OSPL_MAIN (int argc, char *argv[])
{
  return SALTelemetrySubscriber("scheduler_target");
}


