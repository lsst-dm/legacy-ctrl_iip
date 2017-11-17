

# Replace this with the path to the DAQ release
#RELEASE=../..
RELEASE=/home/lsst-daq/daq-sdk/current

###  Parsons additions
g++ -o Fetch.o -c -std=gnu++0x -g -Wall -DSINGLE_TASK -I${RELEASE}/include -I../include Fetch.cpp
g++ -o Fetch -Wl,-rpath=${RELEASE}/x86/lib Fetch.o -L${RELEASE}/x86/lib -ldaq -lims -ldsi -losa -ldss -lnet
