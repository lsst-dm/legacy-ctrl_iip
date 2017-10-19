INC	 = -I$(ARCHIVE) -I$(ARCHIVE)/src -I$(CARCHIVE) -I$(CARCHIVE)/src -I$(PCLUSTER) -I$(PCLUSTER)/src\
-I$(CAMERA) -I$(CAMERA)/src\
-I$(TCS) -I$(TCS)/src\
-I/opt/sal/ts_sal/lsstsal/include\
-I$(SALPATH)/include/dcps/C++/SACPP
SALPATH	 = /opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux
LIBSAL	 = /opt/sal/ts_sal/lsstsal/lib
CC	 = g++
LDFLAGS  = -L$(SALPATH)/lib -L$(LIBSAL) -L/usr/lib/python2.7/config -L/usr/local/lib -L/opt/sal/test/dm/cpp
LDLIBS	 = -lsacpp_archiver_types -lsacpp_catchuparchiver_types -lsacpp_processingcluster_types \
-lsacpp_camera_types -lsacpp_tcs_types \
-l"dcpssacpp" -l"dcpsgapi" -l"ddsuser" \
-l"ddskernel" -l"ddsserialization" -l"ddsconfparser" -l"ddsconf" -l"ddsdatabase" \
-l"ddsutil" -l"ddsos" -ldl $(subst lib,-l,$(sort $(basename $(notdir $(wildcard /usr/lib/librt.so /lib/librt.so))))) \
-lpthread -lSimpleAmqpClient -lyaml-cpp
ARCHIVE  = /opt/sal/ts_sal/test/archiver/cpp
CARCHIVE = /opt/sal/ts_sal/test/catchuparchiver/cpp
PCLUSTER = /opt/sal/ts_sal/test/processingcluster/cpp
TCS      = /opt/sal/ts_sal/test/tcs/cpp
CAMERA   = /opt/sal/ts_sal/test/camera/cpp
CFLAGS   = -g -Wall -c 

all: CommandListener AckSubscriber EventSubscriber Test_CommandListener Test_AckSubscriber Test_EventSubscriber SimplePublisher Consumer

OCS_Bridge: OCS_Bridge.cpp SimplePublisher
	$(CC) -std=c++11 -I.. -L/usr/local/lib -lSimpleAmqpClient -lyaml-cpp SimplePublisher.o -c -o OCS_Bridge.o OCS_Bridge.cpp

CommandListener: CommandListener.cpp OCS_Bridge Toolsmod
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o $(ARCHIVE)/src/.obj/CheckStatus.o OCS_Bridge.o SimplePublisher.o Toolsmod.o -Wall -o CommandListener CommandListener.cpp $(LDLIBS) 

AckSubscriber: AckSubscriber.cpp Consumer SimplePublisher OCS_Bridge Toolsmod
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o $(ARCHIVE)/src/.obj/CheckStatus.o OCS_Bridge.o Consumer.o SimplePublisher.o Toolsmod.o -Wall -g -o AckSubscriber AckSubscriber.cpp $(LDLIBS) 

EventSubscriber: EventSubscriber.cpp SimplePublisher
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(TCS)/src/.obj/SAL_tcs.o $(CAMERA)/src/.obj/CheckStatus.o SimplePublisher.o -Wall -g -o EventSubscriber EventSubscriber.cpp $(LDLIBS) 

Test_OCS_Bridge: Test_OCS_Bridge.cpp SimplePublisher
	$(CC) -std=c++11 -I.. -L/usr/local/lib -lSimpleAmqpClient -lyaml-cpp SimplePublisher.o -c -o Test_OCS_Bridge.o Test_OCS_Bridge.cpp

Test_CommandListener: Test_CommandListener.cpp Test_OCS_Bridge Toolsmod
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o $(ARCHIVE)/src/.obj/CheckStatus.o Test_OCS_Bridge.o SimplePublisher.o Toolsmod.o -Wall -o Test_CommandListener Test_CommandListener.cpp $(LDLIBS) 

Test_AckSubscriber: Test_AckSubscriber.cpp Consumer SimplePublisher Test_OCS_Bridge Toolsmod
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o $(ARCHIVE)/src/.obj/CheckStatus.o Test_OCS_Bridge.o Consumer.o SimplePublisher.o Toolsmod.o -Wall -g -o Test_AckSubscriber Test_AckSubscriber.cpp $(LDLIBS) 

Test_EventSubscriber: Test_EventSubscriber.cpp SimplePublisher
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(TCS)/src/.obj/SAL_tcs.o $(CAMERA)/src/.obj/CheckStatus.o SimplePublisher.o -Wall -g -o Test_EventSubscriber Test_EventSubscriber.cpp $(LDLIBS) 

SimplePublisher: SimplePublisher.cpp
	$(CC) -L/usr/local/lib -lSimpleAmqpClient -c -o SimplePublisher.o SimplePublisher.cpp

Consumer: Consumer.cpp 
	$(CC) $(INC) $(LDFLAGS) $(ARCHIVE)/src/.obj/SAL_archiver.o $(ARCHIVE)/src/.obj/CheckStatus.o -c -o Consumer.o Consumer.cpp -lSimpleAmqpClient 

Toolsmod: Toolsmod.cpp
	$(CC) -std=c++11 -c -o Toolsmod.o Toolsmod.cpp

clean:
	rm -i *.o CommandListener EventListener AckSubscriber
