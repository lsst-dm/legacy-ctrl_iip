if [ "$1" != "" ]; then
    IMG_ID=$1
    FILENAME=$2

    ./emulator atcamera startIntegration seq1 0 $IMG_ID 0
    echo "Sending startIntegration ..." 
    sleep 1

    ./emulator atcamera endReadout seq1 0 $IMG_ID 0
    echo "Sending endReadout ..." 
    sleep 1

    ./emulator efd atHeaderService $FILENAME $IMG_ID
    echo "Sending header ready ..." 
    sleep 1
else
    echo "./sendEvents IMG_ID FILENAME" 
fi
