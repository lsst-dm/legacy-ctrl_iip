SALPATH	   = /opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux
INC	   = -I$(ARCHIVE) -I$(ARCHIVE)/src -I$(CARCHIVE) -I$(CARCHIVE)/src -I$(PCLUSTER) -I$(PCLUSTER)/src\
	     -I/opt/sal/ts_sal/lsstsal/include\
	     -I$(SALPATH)/include/dcps/C++/SACPP\
	     -I$(CAMERA) -I$(CAMERA)/src\
	     -I$(TCS) -I$(TCS)/src\
	     -I$(SALPATH)/examples -I$(SALPATH)/examples/include\
	     -I$(ATCAMERA) -I$(ATCAMERA)/src\
	     -I$(ATARCHIVER) -I$(ATARCHIVER)/src\
	     -I$(EFD) -I$(EFD)/src\
	     -I../include -I/usr/local/include -I/usr/local/boost_1_66_0
CC	   = g++
LDFLAGS    = -L$(SALPATH)/lib -L/opt/sal/ts_sal/lsstsal/lib -L/usr/lib/python2.7/config -L../lib -Wl,-rpath,../lib \
	     -L/usr/local/lib -Wl,-rpath,/usr/local/lib -L/usr/local/lib64 -Wl,-rpath,/usr/local/lib64 -L/usr/local/boost_1_66_0/stage/lib -Wl,-rpath,/usr/local/boost_1_66_0/stage/lib
LDLIBS     = -lsacpp_camera_types -l"dcpssacpp" -l"dcpsgapi" -l"ddsuser" \
	     -l"ddskernel" -l"ddsserialization" -l"ddsconfparser" -l"ddsconf" -l"ddsdatabase" \
	     -l"ddsutil" -l"ddsos" -ldl $(subst lib,-l,$(sort $(basename $(notdir $(wildcard /usr/lib/librt.so /lib/librt.so))))) \
	     -lpthread -lSimpleAmqpClient \
	     -lsacpp_atcamera_types -lsacpp_atArchiver_types -lsacpp_efd_types
ARCHIVE    = /opt/sal/ts_sal/test/archiver/cpp
CARCHIVE   = /opt/sal/ts_sal/test/catchuparchiver/cpp
PCLUSTER   = /opt/sal/ts_sal/test/processingcluster/cpp
CAMERA     = /opt/sal/ts_sal/test/camera/cpp
ATCAMERA   = /opt/sal/ts_sal/test/atcamera/cpp
ATARCHIVER = /opt/sal/ts_sal/test/atArchiver/cpp
EFD        = /opt/sal/ts_sal/test/efd/cpp
TCS 	   = /opt/sal/ts_sal/test/tcs/cpp
CFLAGS     = -g -Wall -c 

all: takeImages \
	startIntegration \
	startReadout \
	endReadout \
	startShutterOpen \
	endShutterOpen \
	startShutterClose \
	endShutterClose \
	tcsTarget \
	sacpp_atcamera_startIntegration_send \
	sacpp_atcamera_endReadout_send \
	sacpp_efd_LargeFileObjectAvailable_send

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

sacpp_atcamera_startIntegration_send: sacpp_atcamera_startIntegration_send.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(ATCAMERA)/src/.obj/SAL_atcamera.o $(ATCAMERA)/src/.obj/CheckStatus.o  -Wall -o $@ $< $(LDLIBS) 

sacpp_atcamera_endReadout_send: sacpp_atcamera_endReadout_send.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(ATCAMERA)/src/.obj/SAL_atcamera.o $(ATCAMERA)/src/.obj/CheckStatus.o  -Wall -o $@ $< $(LDLIBS) 

sacpp_efd_LargeFileObjectAvailable_send: sacpp_efd_LargeFileObjectAvailable_send.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(EFD)/src/.obj/SAL_efd.o $(EFD)/src/.obj/CheckStatus.o  -Wall -o $@ $< $(LDLIBS) 

clean:
	rm takeImages startIntegration startReadout endReadout startShutterOpen endShutterOpen startShutterClose endShutterClose tcsTarget \
	sacpp_atcamera_startIntegration_send \
	sacpp_atcamera_endReadout_send \
	sacpp_efd_LargeFileObjectAvailable_send
