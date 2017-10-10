INC	 = -I$(ARCHIVE) -I$(ARCHIVE)/src -I$(CARCHIVE) -I$(CARCHIVE)/src -I$(PCLUSTER) -I$(PCLUSTER)/src\
-I/opt/sal/ts_sal/lsstsal/include\
-I$(SALPATH)/include/dcps/C++/SACPP\
-I$(CAMERA) -I$(CAMERA)/src\
-I$(SCHEDULER) -I$(SCHEDULER)/src\
-I$(SALPATH)/examples -I$(SALPATH)/examples/include\
-I/opt/sal/ts_sal/test/scheduler/cpp\
-I/opt/sal/ts_sal/test/scheduler/cpp/src
SALPATH	 = /opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux
LIBSAL	 = /opt/sal/ts_sal/lsstsal/lib
CC	 = g++
SOPATH   = /opt/sal/ts_sal/test/archiver/cpp/src/.obj
LDFLAGS  = -L$(SALPATH)/lib -L$(LIBSAL) -L/usr/lib/python2.7/config -L/usr/local/lib -L/opt/sal/test/dm/cpp
LDLIBS   = -lsacpp_camera_types -lsacpp_scheduler_types -l"dcpssacpp" -l"dcpsgapi" -l"ddsuser" \
-l"ddskernel" -l"ddsserialization" -l"ddsconfparser" -l"ddsconf" -l"ddsdatabase" \
-l"ddsutil" -l"ddsos" -ldl $(subst lib,-l,$(sort $(basename $(notdir $(wildcard /usr/lib/librt.so /lib/librt.so))))) \
-lpthread -lSimpleAmqpClient
ARCHIVE  = /opt/sal/ts_sal/test/archiver/cpp
CARCHIVE = /opt/sal/ts_sal/test/catchuparchiver/cpp
PCLUSTER = /opt/sal/ts_sal/test/processingcluster/cpp
CAMERA   = /opt/sal/ts_sal/test/camera/cpp
SCHEDULER= /opt/sal/ts_sal/test/scheduler_target/cpp
CFLAGS   = -g -Wall -c 

all: takeImages startIntegration startReadout startShutterOpen endShutterOpen startShutterClose endShutterClose schedulerTarget

takeImages: sacpp_camera_takeImages_controller.cpp SimplePublisher 
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o SimplePublisher.o -Wall -o takeImages sacpp_camera_takeImages_controller.cpp $(LDLIBS) 

startIntegration: sacpp_camera_startIntegration_log.cpp SimplePublisher 
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o SimplePublisher.o -Wall -o startIntegration sacpp_camera_startIntegration_log.cpp $(LDLIBS) 

readout: sacpp_camera_startReadout_log.cpp SimplePublisher 
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o SimplePublisher.o -Wall -o readout sacpp_camera_startReadout_log.cpp $(LDLIBS) 

startShutterOpen: sacpp_camera_startShutterOpen_log.cpp SimplePublisher 
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o SimplePublisher.o -Wall -o startShutterOpen sacpp_camera_startShutterOpen_log.cpp $(LDLIBS) 

endShutterOpen: sacpp_camera_endShutterOpen_log.cpp SimplePublisher 
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o SimplePublisher.o -Wall -o endShutterOpen sacpp_camera_startShutterOpen_log.cpp $(LDLIBS) 

startShutterClose: sacpp_camera_startShutterClose_log.cpp SimplePublisher 
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o SimplePublisher.o -Wall -o startShutterClose sacpp_camera_startShutterClose_log.cpp $(LDLIBS) 

endShutterClose: sacpp_camera_endShutterClose_log.cpp SimplePublisher 
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o SimplePublisher.o -Wall -o endShutterClose sacpp_camera_startShutterClose_log.cpp $(LDLIBS) 

schedulerTarget: scheduler_targetDataSubscriber.cpp SimplePublisher 
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(SCHEDULER)/standalone/.obj/SAL_scheduler.o $(SCHEDULER)/standalone/.obj/CheckStatus.o SimplePublisher.o -Wall -o schedulerTarget scheduler_targetDataSubscriber.cpp $(LDLIBS) 

SimplePublisher: SimplePublisher.cpp
	$(CC) -L/usr/local/lib -lSimpleAmqpClient -c -o SimplePublisher.o SimplePublisher.cpp

clean:
	rm -i *.o CommandListener EventListener AckSubscriber
