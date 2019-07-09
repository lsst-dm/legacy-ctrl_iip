# startup sequence 
python3 command.py -D ATArchiver enterControl
sleep 4
echo "[OK] ENTER_CONTROL COMPLETE." 

python3 command.py -D ATArchiver start --settings Normal
sleep 4 
echo "[OK] START COMPLETE." 

#python3 command.py -D ATArchiver standby
#sleep 4
#echo "[OK] STANDBY COMPLETE." 

#python3 command.py -D ATArchiver disable
#sleep 4
#echo "[OK] DISABLE COMPLETE." 

python3 command.py -D ATArchiver enable
sleep 4
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
