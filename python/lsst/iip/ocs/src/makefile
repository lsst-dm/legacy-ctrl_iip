ARCHIVE  	= /opt/sal/ts_sal/test/archiver/cpp
CARCHIVE 	= /opt/sal/ts_sal/test/catchuparchiver/cpp
PCLUSTER 	= /opt/sal/ts_sal/test/processingcluster/cpp
HEADER   	= /opt/sal/ts_sal/test/headerService/cpp
CAMERA   	= /opt/sal/ts_sal/test/camera/cpp
EFD      	= /opt/sal/ts_sal/test/efd/cpp
ATARCHIVE	= /opt/sal/ts_sal/test/atArchiver/cpp
ATCAMERA 	= /opt/sal/ts_sal/test/atcamera/cpp
SALINC	 	= -I$(ARCHIVE) -I$(ARCHIVE)/src\
		  -I$(CARCHIVE) -I$(CARCHIVE)/src\
		  -I$(PCLUSTER) -I$(PCLUSTER)/src\
		  -I$(CAMERA) -I$(CAMERA)/src\
		  -I$(EFD) -I$(EFD)/src\
		  -I$(ATCAMERA) -I$(ATCAMERA)/src\
		  -I$(ATARCHIVE) -I$(ATARCHIVE)/src\
		  -I/opt/sal/ts_sal/lsstsal/include\
		  -I$(SALPATH)/include/dcps/C++/SACPP\
		  -I$(SALPATH)/include/sys\
		  -I$(SALPATH)/include
INCLUDE  	= -I../include -I/usr/local/include -I/usr/local/boost_1_66_0
SALPATH	 	= /opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux
LIBSAL	 	= /opt/sal/ts_sal/lsstsal/lib
CC	 	= g++
SAL_LDPATH  	= -L$(SALPATH)/lib -L$(LIBSAL) -L/usr/lib/python2.7/config 
#DM_LDPATH 	= -L../lib -Wl,-rpath,../lib-L/usr/local/lib -Wl,-rpath,/usr/local/lib -L/usr/local/lib64 -Wl,-rpath,/usr/local/lib64
DM_LDPATH 	= -L/usr/local/lib -Wl,-rpath,/usr/local/lib \
		  -L/usr/local/lib64 -Wl,-rpath,/usr/local/lib64 \
		  -L/usr/local/boost_1_66_0/stage/lib -Wl,-rpath,/usr/local/boost_1_66_0/stage/lib
SAL_LDLIB	= -lsacpp_archiver_types -lsacpp_catchuparchiver_types -lsacpp_processingcluster_types\
		  -lsacpp_camera_types -lsacpp_atcamera_types -lsacpp_efd_types -lsacpp_atArchiver_types\
		  -l"dcpssacpp" -l"dcpsgapi" -l"ddsuser" \
		  -l"ddskernel" -l"ddsserialization" -l"ddsconfparser" -l"ddsconf" -l"ddsdatabase" \
		  -l"ddsutil" -l"ddsos" -ldl $(subst lib,-l,$(sort $(basename $(notdir $(wildcard /usr/lib/librt.so /lib/librt.so)))))
DM_LDLIB        = -lpthread -lSimpleAmqpClient -lyaml-cpp
CFLAGS   	= -g -Wall -c 
COMPVERS 	= -std=c++11
OBJ_DIR         = ../obj
DM_OBJ          = ../obj/OCS_Bridge.o ../obj/SimplePublisher.o ../obj/Toolsmod.o ../obj/Consumer.o
OCS_OBJ         = $(ARCHIVE)/src/.obj/SAL_archiver.o \
		  $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o \
		  $(PCLUSTER)/src/.obj/SAL_processingcluster.o \
		  $(ARCHIVE)/src/.obj/CheckStatus.o
AT_OBJ          = $(ATARCHIVE)/src/.obj/SAL_atArchiver.o

all: CommandListener AckSubscriber EventSubscriber SimplePublisher Consumer

OCS_Bridge: OCS_Bridge.cpp SimplePublisher
	$(CC) $(COMPVERS) $(INCLUDE) $(DM_LDPATH) $(OBJ_DIR)/SimplePublisher.o -c -o $(OBJ_DIR)/OCS_Bridge.o OCS_Bridge.cpp -lSimpleAmqpClient -lyaml-cpp 

SimplePublisher: SimplePublisher.cpp
	$(CC) $(COMPVERS) $(INCLUDE) $(DM_LDPATH) -c -o $(OBJ_DIR)/SimplePublisher.o SimplePublisher.cpp -lSimpleAmqpClient 

Consumer: Consumer.cpp 
	$(CC) $(COMPVERS) $(INCLUDE) $(DM_LDPATH) -c -o $(OBJ_DIR)/Consumer.o Consumer.cpp -lSimpleAmqpClient 

Toolsmod: Toolsmod.cpp
	$(CC) $(COMPVERS) $(INCLUDE) -c -o ../obj/Toolsmod.o Toolsmod.cpp

CommandListener: CommandListener.cpp OCS_Bridge Toolsmod
	g++ -std=c++11 $(INCLUDE) $(SALINC) $(SAL_LDPATH) $(DM_LDPATH) $(OCS_OBJ) $(AT_OBJ) $(OBJ_DIR)/Toolsmod.o $(OBJ_DIR)/SimplePublisher.o $(OBJ_DIR)/OCS_Bridge.o CommandListener.cpp -o CommandListener $(SAL_LDLIB) $(DM_LDLIB)

AckSubscriber: AckSubscriber.cpp Consumer SimplePublisher OCS_Bridge Toolsmod
	$(CC) $(COMPVERS) $(INCLUDE) $(SALINC) $(SAL_LDPATH) $(DM_LDPATH) $(OCS_OBJ) $(AT_OBJ) $(DM_OBJ) -Wall -g -o AckSubscriber AckSubscriber.cpp $(SAL_LDLIB) $(DM_LDLIB)

EventSubscriber: EventSubscriber.cpp SimplePublisher
	$(CC) $(COMPVERS) $(INCLUDE) $(SALINC) $(SAL_LDPATH) $(DM_LDPATH) $(CAMERA)/src/.obj/SAL_camera.o $(ATCAMERA)/src/.obj/SAL_atcamera.o $(EFD)/src/.obj/SAL_efd.o $(CAMERA)/src/.obj/CheckStatus.o $(OBJ_DIR)/SimplePublisher.o -Wall -g -o EventSubscriber EventSubscriber.cpp $(SAL_LDLIB) $(DM_LDLIB)


clean:
	rm -i CommandListener EventSubscriber AckSubscriber $(OBJ_DIR)/*.o
