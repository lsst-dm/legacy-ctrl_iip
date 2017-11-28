SALINC	 = -I$(ARCHIVE) -I$(ARCHIVE)/src -I$(CARCHIVE) -I$(CARCHIVE)/src -I$(PCLUSTER) -I$(PCLUSTER)/src\
-I$(CAMERA) -I$(CAMERA)/src\
-I$(TCS) -I$(TCS)/src\
-I/opt/sal/ts_sal/lsstsal/include\
-I$(SALPATH)/include/dcps/C++/SACPP
INCLUDE  = -I../core/include -I../include
SALPATH	 = /opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux
LIBSAL	 = /opt/sal/ts_sal/lsstsal/lib
CC	 = g++
LDFLAGS  = -L$(SALPATH)/lib -L$(LIBSAL) -L/usr/lib/python2.7/config -L/opt/sal/test/dm/cpp -L../core/lib64 -L../core/lib -Wl,-rpath,../core/lib64 -Wl,-rpath,../core/lib
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
COMPVERS = -std=c++11

all: CommandListener AckSubscriber EventSubscriber Test_CommandListener Test_AckSubscriber Test_EventSubscriber SimplePublisher Consumer

OCS_Bridge: OCS_Bridge.cpp SimplePublisher
	$(CC) $(COMPVERS) $(INCLUDE) -Wl,-rpath,../core/lib -L../core/lib ../obj/SimplePublisher.o -c -o ../obj/OCS_Bridge.o OCS_Bridge.cpp -lSimpleAmqpClient -lyaml-cpp 

CommandListener: CommandListener.cpp OCS_Bridge Toolsmod
	$(CC) $(COMPVERS) $(INCLUDE) $(SALINC) $(LDFLAGS) $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o $(ARCHIVE)/src/.obj/CheckStatus.o ../obj/OCS_Bridge.o ../obj/SimplePublisher.o ../obj/Toolsmod.o -Wall -o CommandListener CommandListener.cpp $(LDLIBS) 

AckSubscriber: AckSubscriber.cpp Consumer SimplePublisher OCS_Bridge Toolsmod
	$(CC) $(COMPVERS) $(INCLUDE) $(SALINC) $(LDFLAGS) $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o $(ARCHIVE)/src/.obj/CheckStatus.o ../obj/OCS_Bridge.o ../obj/Consumer.o ../obj/SimplePublisher.o ../obj/Toolsmod.o -Wall -g -o AckSubscriber AckSubscriber.cpp $(LDLIBS) 

EventSubscriber: EventSubscriber.cpp SimplePublisher
	$(CC) $(COMPVERS) $(INCLUDE) $(SALINC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(TCS)/src/.obj/SAL_tcs.o $(CAMERA)/src/.obj/CheckStatus.o ../obj/SimplePublisher.o -Wall -g -o EventSubscriber EventSubscriber.cpp $(LDLIBS) 

Test_OCS_Bridge: Test_OCS_Bridge.cpp SimplePublisher
	$(CC) $(COMPVERS) $(INCLUDE) -Wl,-rpath,../core/lib -L../core/lib ../obj/SimplePublisher.o -c -o ../obj/Test_OCS_Bridge.o Test_OCS_Bridge.cpp -lSimpleAmqpClient -lyaml-cpp 

Test_CommandListener: Test_CommandListener.cpp Test_OCS_Bridge Toolsmod
	$(CC) $(COMPVERS) $(INCLUDE) $(SALINC) $(LDFLAGS) $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o $(ARCHIVE)/src/.obj/CheckStatus.o ../obj/Test_OCS_Bridge.o ../obj/SimplePublisher.o ../obj/Toolsmod.o -Wall -o Test_CommandListener Test_CommandListener.cpp $(LDLIBS) 

Test_AckSubscriber: Test_AckSubscriber.cpp Consumer SimplePublisher Test_OCS_Bridge Toolsmod
	$(CC) $(COMPVERS) $(INCLUDE) $(SALINC) $(LDFLAGS) $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o $(ARCHIVE)/src/.obj/CheckStatus.o ../obj/Test_OCS_Bridge.o ../obj/Consumer.o ../obj/SimplePublisher.o ../obj/Toolsmod.o -Wall -g -o Test_AckSubscriber Test_AckSubscriber.cpp $(LDLIBS) 

Test_EventSubscriber: Test_EventSubscriber.cpp SimplePublisher
	$(CC) $(COMPVERS) $(INCLUDE) $(SALINC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(TCS)/src/.obj/SAL_tcs.o $(CAMERA)/src/.obj/CheckStatus.o ../obj/SimplePublisher.o -Wall -g -o Test_EventSubscriber Test_EventSubscriber.cpp $(LDLIBS) 

SimplePublisher: SimplePublisher.cpp
	$(CC) $(COMPVERS) $(INCLUDE) -Wl,-rpath,../core/lib -L../core/lib -c -o ../obj/SimplePublisher.o SimplePublisher.cpp -lSimpleAmqpClient 

Consumer: Consumer.cpp 
	$(CC) $(COMPVERS) $(INCLUDE) -Wl,-rpath,../core/lib -L../core/lib -c -o ../obj/Consumer.o Consumer.cpp -lSimpleAmqpClient 

Toolsmod: Toolsmod.cpp
	$(CC) $(COMPVERS) $(INCLUDE) -c -o ../obj/Toolsmod.o Toolsmod.cpp

clean:
	rm -i *.o CommandListener EventSubscriber AckSubscriber Test_CommandListener Test_AckSubscriber Test_EventSubscriber
