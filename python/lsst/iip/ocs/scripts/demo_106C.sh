# startup sequence 
#../commands/sacpp_archiver_enterControl_commander 0
#sleep 3

#../commands/sacpp_archiver_start_commander Normal
#sleep 3 

../commands/sacpp_archiver_standby_commander 0
sleep 1
echo "[OK] STANDBY COMPLETE." 

../commands/sacpp_archiver_disable_commander 0
sleep 1
echo "[OK] DISABLE COMPLETE." 

../commands/sacpp_archiver_enable_commander 0
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
