INC	 = -I$(ARCHIVE) -I$(ARCHIVE)/src -I$(CARCHIVE) -I$(CARCHIVE)/src -I$(PCLUSTER) -I$(PCLUSTER)/src\
-I/opt/sal/ts_sal/lsstsal/include\
-I$(SALPATH)/include/dcps/C++/SACPP\
-I$(CAMERA) -I$(CAMERA)/src\
-I$(TCS) -I$(TCS)/src\
-I$(SALPATH)/examples -I$(SALPATH)/examples/include
SALPATH	 = /opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux
LIBSAL	 = /opt/sal/ts_sal/lsstsal/lib
CC	 = g++
LDFLAGS  = -L$(SALPATH)/lib -L$(LIBSAL) -L/usr/lib/python2.7/config -L../core/lib -L../core/lib64 -L/opt/sal/test/dm/cpp -Wl,-rpath,../core/lib -Wl,-rpath,../core/lib64
LDLIBS   = -lsacpp_camera_types -lsacpp_scheduler_types -lsacpp_tcs_types -l"dcpssacpp" -l"dcpsgapi" -l"ddsuser" \
-l"ddskernel" -l"ddsserialization" -l"ddsconfparser" -l"ddsconf" -l"ddsdatabase" \
-l"ddsutil" -l"ddsos" -ldl $(subst lib,-l,$(sort $(basename $(notdir $(wildcard /usr/lib/librt.so /lib/librt.so))))) \
-lpthread -lSimpleAmqpClient
ARCHIVE  = /opt/sal/ts_sal/test/archiver/cpp
CARCHIVE = /opt/sal/ts_sal/test/catchuparchiver/cpp
PCLUSTER = /opt/sal/ts_sal/test/processingcluster/cpp
CAMERA   = /opt/sal/ts_sal/test/camera/cpp
TCS 	 = /opt/sal/ts_sal/test/tcs/cpp
CFLAGS   = -g -Wall -c 

all: takeImages startIntegration startReadout endReadout startShutterOpen endShutterOpen startShutterClose endShutterClose tcsTarget

takeImages: sacpp_camera_takeImages_commander.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o  -Wall -o takeImages sacpp_camera_takeImages_commander.cpp $(LDLIBS) 

startIntegration: sacpp_camera_startIntegration_send.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o  -Wall -o startIntegration sacpp_camera_startIntegration_send.cpp $(LDLIBS) 

startReadout: sacpp_camera_startReadout_send.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o  -Wall -o startReadout sacpp_camera_startReadout_send.cpp $(LDLIBS) 

endReadout: sacpp_camera_endReadout_send.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o  -Wall -o endReadout sacpp_camera_endReadout_send.cpp $(LDLIBS) 

startShutterOpen: sacpp_camera_startShutterOpen_send.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o  -Wall -o startShutterOpen sacpp_camera_startShutterOpen_send.cpp $(LDLIBS) 

endShutterOpen: sacpp_camera_endShutterOpen_send.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o  -Wall -o endShutterOpen sacpp_camera_endShutterOpen_send.cpp $(LDLIBS) 

startShutterClose: sacpp_camera_startShutterClose_send.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o  -Wall -o startShutterClose sacpp_camera_startShutterClose_send.cpp $(LDLIBS) 

endShutterClose: sacpp_camera_endShutterClose_send.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(CAMERA)/src/.obj/SAL_camera.o $(CAMERA)/src/.obj/CheckStatus.o  -Wall -o endShutterClose sacpp_camera_endShutterClose_send.cpp $(LDLIBS) 

tcsTarget: sacpp_tcs_target_commander.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(TCS)/src/.obj/SAL_tcs.o $(TCS)/src/.obj/CheckStatus.o  -Wall -o tcsTarget sacpp_tcs_target_commander.cpp $(LDLIBS) 

clean:
	rm -i takeImages startIntegration startReadout endReadout startShutterOpen endShutterOpen startShutterClose endShutterClose tcsTarget
