# How to run full night NextVisit 

In the ocs/scripts directory, there is a script called emu_NextVisit.sh.  
Run ./emu_NextVisit [Num_visit] [Num_Readouts]  

## Editing the script 
To edit the script, simply update the values starting with ../events/ to whatever event you  
would like to listen to. One example is  
In line 41, change `../events/sacpp_archiver_endReadout_send` to `../events/sacpp_camera_endReadout_send`  

## Assumptions
* The machine this script is running must have OCS sal software installed.  
* It assumes all the events are in `ocs/events` directory. 
