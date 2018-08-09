DEX=0          #Image index
SEQ=0          #Image Sequence name
NAM=200
#IMG="jgt_test5"          #Number part of Image_ID
IMG="Image_000001651d5f8936"          #Number part of Image_ID
NAPTIME=5
SLEEPYTIME=0
TSTAMP=4.0     #Timestamp
ET=1.0         #Exposure Time
PRI=1          #Priority

#/opt/sal/ts_sal/test/atcamera/cpp/src/sacpp_atcamera_startIntegration_send "$SEQ" 1 "on-$IMG" $DEX $TSTAMP $ET $PRI
/opt/sal/ts_sal/test/atcamera/cpp/src/sacpp_atcamera_startIntegration_send "$SEQ" 1 "$IMG" $DEX $TSTAMP $ET $PRI
sleep $NAPTIME

/opt/sal/ts_sal/test/atcamera/cpp/src/sacpp_atcamera_endReadout_send "$SEQ" 1 "$IMG" 1 4.0 1.0 1
sleep $NAPTIME

/opt/sal/ts_sal/test/efd/cpp/src/sacpp_efd_LargeFileObjectAvailable_send 1 1 "atHeaderService" 1 "http://140.252.32.129:8000/$IMG.header" 1.0 "$IMG" 1
