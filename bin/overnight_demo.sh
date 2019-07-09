#!/bin/sh

# startup sequence 
function startup() {

  python36 command.py -D ATArchiver enterControl
  sleep 3
  
  python36 command.py -D ATArchiver start --settings Normal
  sleep 3 
  
  python36 command.py -D ATArchiver standby
  sleep 1
  
  python36 command.py -D ATArchiver disable
  sleep 1
  
  python36 command.py -D ATArchiver enable
  sleep 1
  echo "[OK] ENABLE COMPLETE." 
  echo "System UP and running."
  echo " "
}

#shutdown sequence
function shutdown() {

  python36 command.py -D ATArchiver disable
  sleep 1
  
  python36 command.py -D ATArchiver standby
  sleep 1
  
  python36 command.py -D ATArchiver exitControl
  sleep 3
  
}


# MAIN EXPOSURE LOOP:
#LOOP EVERY 30 SECONDS FOR A TOTAL OF 100 TIMES
DEX=0          #Image index
SEQ=0          #Image Sequence name
NAM=200
IMG=0          #Number part of Image_ID
NAPTIME=0
SLEEPYTIME=0
TSTAMP=4.0     #Timestamp
ET=1.0         #Exposure Time
PRI=1          #Priority


for V in 1 2 3 4 5 6 7 8 9  #Num times entire script runs
do

for W in 1 2 3 4 5   #Num times system is brought up and shut dowm
do
startup

for Y in 1 2 3 4 5 6 7 8 9 10   #This loop and next (Z) loop insures 100 readouts...
do

for Z in 1 2 3 4 5 6 7 8 9 10
do

SEQ=$(($SEQ + 1))
NAM=$(($NAM + 1))

#SELECT_IMAGE_ID BY RAND - MODULO 20, AND generate IMAGE_ID
IMG=$(($RANDOM%20))

NAPTIME=$((($RANDOM%5) +1))
SLEEPYTIME=$((($RANDOM%25) + 3))

/opt/sal/ts_sal/test/atcamera/cpp/src/sacpp_atcamera_startIntegration_send "$SEQ" 1 "on-$IMG" $DEX $TSTAMP $ET $PRI
sleep $NAPTIME

/opt/sal/ts_sal/test/atcamera/cpp/src/sacpp_atcamera_endReadout_send "$SEQ" 1 "on-$IMG" 1 4.0 1.0 1
sleep $NAPTIME

/opt/sal/ts_sal/test/efd/cpp/src/sacpp_efd_LargeFileObjectAvailable_send 1 1 "AT" 1 "http://tmp/source/header/on-$IMG/on-$IMG.header" 1.0 "on-$IMG" 1
sleep $NAPTIME

sleep 10
sleep $SLEEPYTIME
done

SLEEPYTIME=$((($RANDOM%15)+ 3))
sleep $SLEEPYTIME
done

#THEN SHUTDOWN AND START AGAIN
shutdown

done
SLEEPYTIME=$((($RANDOM%35)+ 3))
sleep $SLEEPYTIME

done


