######################################################################################
# NOTE: This script is HIGHLY temprary. Its purpose is simple:
# It calls the ims_list DAQ example application, which dumps all of the current 
# images in the catalog and all ancillary info.
# It then separates column 7 (the actual name of the image) into a list,
# and checks this list for the incoming image name argument - then
# returns an exit code for either success (0) or failure.
# The way it is currently built, it is hardcoded to look strictly for
# raft partition 'ats'
#
# It is called by the Forwarder at runtime.


/srv/nfs/lsst-daq/daq-sdk/R2-V1.14/x86/bin/ims_list ats |awk -F " " '{print $NF}'|grep $1
#echo "Result is: $?"
if [ $? = 1 ]
  then
    exit 1
  else
    exit 0
fi
#echo $?

