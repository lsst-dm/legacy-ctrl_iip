INC	 = -I$(ARCHIVE) -I$(ARCHIVE)/src -I$(CARCHIVE) -I$(CARCHIVE)/src -I$(PCLUSTER) -I$(PCLUSTER)/src\
-I/opt/sal/ts_sal-master/lsstsal/include\
-I$(SALPATH)/include/dcps/C++/SACPP
SALPATH	 = /opt/sal/ts_opensplice-master/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux
LIBSAL	 = /opt/sal/ts_sal-master/lsstsal/lib
CC	 = g++
SOPATH   = /opt/sal/ts_sal-master/test/archiver/cpp/src/.obj
LDFLAGS  = -L$(SALPATH)/lib -L$(LIBSAL) -L/usr/lib/python2.7/config -L/usr/local/lib -L/opt/sal/test/dm/cpp
LDLIBS   = -lsacpp_archiver_types -lsacpp_catchuparchiver_types -lsacpp_processingcluster_types -l"dcpssacpp" -l"dcpsgapi" -l"ddsuser" \
-l"ddskernel" -l"ddsserialization" -l"ddsconfparser" -l"ddsconf" -l"ddsdatabase" \
-l"ddsutil" -l"ddsos" -ldl $(subst lib,-l,$(sort $(basename $(notdir $(wildcard /usr/lib/librt.so /lib/librt.so))))) \
-lpthread -lpython2.7 -lSimpleAmqpClient -lyaml-cpp
ARCHIVE  = /opt/sal/ts_sal-master/test/archiver/cpp
CARCHIVE = /opt/sal/ts_sal-master/test/catchuparchiver/cpp
PCLUSTER = /opt/sal/ts_sal-master/test/processingcluster/cpp
CFLAGS   = -g -Wall -c 

all: CommandListener AckSubscriber SimplePublisher Consumer

OCS_Bridge: OCS_Bridge.cpp SimplePublisher
	$(CC) -std=c++11 -I.. -L/usr/local/lib -lSimpleAmqpClient -lyaml-cpp SimplePublisher.o -c -o OCS_Bridge.o OCS_Bridge.cpp

CommandListener: CommandListener.cpp OCS_Bridge
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o $(ARCHIVE)/src/.obj/CheckStatus.o OCS_Bridge.o SimplePublisher.o -Wall -o CommandListener CommandListener.cpp $(LDLIBS) 

EventListener: EventListener.cpp OCS_Bridge
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o $(ARCHIVE)/src/.obj/CheckStatus.o OCS_Bridge.o SimplePublisher.o -Wall -o EventListener EventListener.cpp $(LDLIBS) 

AckSubscriber: AckSubscriber.cpp Consumer SimplePublisher OCS_Bridge
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o $(ARCHIVE)/src/.obj/CheckStatus.o OCS_Bridge.o Consumer.o SimplePublisher.o -Wall -o AckSubscriber AckSubscriber.cpp $(LDLIBS) 

SimplePublisher: SimplePublisher.cpp
	$(CC) -L/usr/local/lib -lSimpleAmqpClient -c -o SimplePublisher.o SimplePublisher.cpp

Consumer: Consumer.cpp 
	$(CC) -L/usr/local/lib -lSimpleAmqpClient -c -o Consumer.o Consumer.cpp

clean:
	rm -i *.o CommandListener EventListener AckSubscriber
