# startup sequence 
#../commands/sacpp_archiver_enterControl_commander 0
#sleep 3

#../commands/sacpp_archiver_start_commander Normal
#sleep 3 

#../commands/sacpp_archiver_standby_commander 0
#sleep 1
#echo "[OK] STANDBY COMPLETE." 

#../commands/sacpp_archiver_disable_commander 0
#sleep 1
#echo "[OK] DISABLE COMPLETE." 

#../commands/sacpp_archiver_enable_commander 0
#sleep 1
#echo "[OK] ENABLE COMPLETE." 

#../events/tcsTarget 1 1 1 1 1 1 1 1 1 1 1 
#sleep 10
#echo "[OK] TARGET COMPLETE." 

#/opt/sal/ts_sal/test/atcamera/cpp/src/sacpp_atcamera_startIntegration_send "seq123" 3 "on-11" 1 0 0 0
#sleep 10 
#echo "[OK] START_INTEGRATION COMPLETE." 

#/opt/sal/ts_sal/test/atcamera/cpp/src/sacpp_atcamera_endReadout_send "seq123" 3 "on-11" 1 0 0 0
#sleep 10 
#echo "[OK] START_INTEGRATION COMPLETE." 

/opt/sal/ts_sal/test/efd/cpp/src/sacpp_efd_LargeFileObjectAvailable_send 0 "0" "AT" "0" "felipe@141.142.238.177:/mnt/lfa/DMHS_filerepo/visitJune-26.header" 0 "visitJune-26" 0 
sleep 3
echo "[OK] HEADER_READY"

#./emu_NextVisit.sh 1 1
#sleep 20
#echo "[OK] NEXT_VISIT SEQUENCE COMPLETE." 

#./emu_NextVisit.sh 1 5
#sleep 20 
#echo "[OK] NEXT_VISIT SEQUENCE COMPLETE." 
