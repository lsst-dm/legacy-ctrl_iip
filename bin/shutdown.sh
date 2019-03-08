# Shutdown sequence 
# Command Sequence is DISABLE > STANDBY > EXIT_CONTROL 

/opt/sal/ts_sal/test/atArchiver/cpp/src/sacpp_atArchiver_disable_commander 0
echo "[OK] DISABLE COMPLETE." 
sleep 4

/opt/sal/ts_sal/test/atArchiver/cpp/src/sacpp_atArchiver_standby_commander 0
echo "[OK] STANDBY COMPLETE." 
sleep 4 

/opt/sal/ts_sal/test/atArchiver/cpp/src/sacpp_atArchiver_exitControl_commander 0
echo "[OK] EXIT_CONTROL  COMPLETE." 
sleep 4
