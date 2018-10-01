/srv/nfs/lsst-daq/daq-sdk/R2-V1.14/x86/bin/ims_list ats |awk -F " " '{print $NF}'|grep $1
#echo "Result is: $?"
if [ $? = 1 ]
  then
    exit 1
  else
    exit 0
fi
#echo $?


#/srv/nfs/lsst-daq/daq-sdk/R2-V1.14/x86/bin/ims_list ats |grep $1
#X=$(/srv/nfs/lsst-daq/daq-sdk/R2-V1.14/x86/bin/ims_list ats |awk -F " " '{print $NF}'|grep $1)
#X=$(/srv/nfs/lsst-daq/daq-sdk/R2-V1.14/x86/bin/ims_list ats |grep $1)
#X=$(ims ats |awk -F " " '{print $NF}' |grep $1)
