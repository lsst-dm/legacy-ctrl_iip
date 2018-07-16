# startup sequence 
/opt/sal/ts_sal/test/atArchiver/cpp/src/sacpp_atArchiver_enterControl_commander 0
sleep 3
echo "[OK] ENTER_CONTROL COMPLETE." 

/opt/sal/ts_sal/test/atArchiver/cpp/src/sacpp_atArchiver_start_commander Normal
sleep 3 
echo "[OK] START COMPLETE." 

/opt/sal/ts_sal/test/atArchiver/cpp/src/sacpp_atArchiver_standby_commander 0
sleep 1
echo "[OK] STANDBY COMPLETE." 

/opt/sal/ts_sal/test/atArchiver/cpp/src/sacpp_atArchiver_disable_commander 0
sleep 1
echo "[OK] DISABLE COMPLETE." 

/opt/sal/ts_sal/test/atArchiver/cpp/src/sacpp_atArchiver_enable_commander 0
sleep 1
echo "[OK] ENABLE COMPLETE." 

#../events/tcsTarget 1 1 1 1 1 1 1 1 1 1 1 
#sleep 10
#echo "[OK] TARGET COMPLETE." 

#/opt/sal/ts_sal/test/dmHeaderService/cpp/src/sacpp_dmHeaderService_LargeFileObjectAvailable_send 1 1 1 1 "felipe@141.142.237.177:/tmp/header/test23.header" 1 1
#sleep 3
#echo "[OK] HEADER_READY"

#/opt/sal/ts_sal/test/camera/cpp/src/sacpp_camera_startIntegration_send test23 0
#sleep 10 
#echo "[OK] END READOUT COMPLETE." 

#./emu_NextVisit.sh 1 1
#sleep 20
#echo "[OK] NEXT_VISIT SEQUENCE COMPLETE." 

#./emu_NextVisit.sh 1 5
#sleep 20 
#echo "[OK] NEXT_VISIT SEQUENCE COMPLETE." 
