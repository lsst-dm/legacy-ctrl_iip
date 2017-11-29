#! /bin/bash

# take in command line arguments
if [ $# -lt 2 ]
then
    echo "Missing parameters"
    echo "Usage: ./emu_NextVisit [Num_Visit] [Num_img]" 
    exit 1
fi

NUM_VISITS=$1
NUM_IMGS=$2

for (( i=0; i<$NUM_VISITS; i++ )) 
do
    # target visit 
    ../events/tcsTarget 1 1 1 "no_filter" 0.0 1.0 1.0 1.0 2 2 1.0
    echo "[x] TARGET_VISIT sent." 
    
    # target accept
    ../events/sacpp_archiver_targetVisitAccept_send 0
    echo "[x] TARGET_VISIT_ACCEPT sent." 
    sleep 20  

    # target visit done
    ../events/sacpp_archiver_targetVisitDone_send 0
    echo "[x] TARGET_VISIT_DONE sent." 
    sleep 4 

    # takeImages
    ../events/takeImages $NUM_IMGS 1.0 1 1 0 0 "v3456" 
    echo "[x] TAKE_IMAGE sent." 
    sleep 2 

    for (( j=0; j<$NUM_IMGS; j++ ))
    do
        sleep 2
        
        # endReadout
        ../events/endReadout 0
        echo "[x] END_READOUT sent."
    done 
    
    # takeImage done
    ../events/sacpp_archiver_takeImageDone_send 0
    echo "[x] TAKE_IMAGE_DONE sent." 
    echo "[O] Visit Complete." 
    echo "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
done
