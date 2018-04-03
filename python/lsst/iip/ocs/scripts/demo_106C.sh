GREEN='\033[0;32m'
NOCOL='\033[0m'
BOLD='\033[1m'
# startup sequence 
#../commands/sacpp_archiver_enterControl_commander 0
#sleep 3

#../commands/sacpp_archiver_start_commander Normal
#sleep 3 

../commands/sacpp_atArchiver_standby_commander 0
sleep 1
echo -e "[${GREEN}${BOLD}OK${NOCOL}] STANDBY COMPLETE." 

../commands/sacpp_atArchiver_disable_commander 0
sleep 1
echo -e "[${GREEN}${BOLD}OK${NOCOL}] DISABLE COMPLETE." 

../commands/sacpp_atArchiver_enable_commander 0
sleep 1
echo -e "[${GREEN}${BOLD}OK${NOCOL}] ENABLE COMPLETE." 

# startIntegration
../events/sacpp_atcamera_startIntegration_send seq_123 1 IMG_100 1 0 0 0 
sleep 3
echo -e "[${GREEN}${BOLD}OK${NOCOL}] START_INTEGRATION sent."

# efd
#../events/sacpp_efd_LargeFileObjectAvailable_send 0 a AT a dmills@141.142.238.176:/tmp/cam.header 0 IMG_100 0 
#sleep 1
#echo -e "[${GREEN}${BOLD}OK${NOCOL}] HEADER_READY sent."

# endReadout
../events/sacpp_atcamera_endReadout_send seq_123 1 LSSTTEST-1 1 0 0 0
sleep 1
echo -e "[${GREEN}${BOLD}OK${NOCOL}] END_READOUT sent."

#../events/sacpp_atcamera_startIntegration_send seq_123 2 IMG_101 2 0 0 0 
#sleep 1
#echo "[x] START_INTEGRATION sent."

# efd
#../events/sacpp_efd_LargeFileObjectAvailable_send 0 a AT a dmills@141.142.238.176:/tmp/cam.header 0 IMG_101 0 
#sleep 1
#echo "[x] HEADER_READY sent."

# endReadout
#../events/sacpp_atcamera_endReadout_send seq_123 2 IMG_101 2 0 0 0
#echo "[x] END_READOUT sent."
