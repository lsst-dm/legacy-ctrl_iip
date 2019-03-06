#!/bin/bash
# This script launches a SAL DDS publisher and counts 
# the threads used in the short time it runs.
# USAGE: ./thread_counter.sh ./sacpp_archiver_enable_commander X
# where X is something to send...any type of data...'1', 'A', etc.
#
echo "Checking thread count for $1 command"
$1 $2 &
PD=$!
for i in 1 2 3 4 5 6 7 8 9
do
  LN=`cat /proc/$PD/status |grep Threads`
  echo $LN
  sleep 1
done
echo "End..."
kill -9 $PD

