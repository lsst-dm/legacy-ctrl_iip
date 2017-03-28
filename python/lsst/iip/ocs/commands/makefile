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
-lpython2.7
ARCHIVE  = /opt/sal/ts_sal-master/test/archiver/cpp
CARCHIVE = /opt/sal/ts_sal-master/test/catchuparchiver/cpp
PCLUSTER = /opt/sal/ts_sal-master/test/processingcluster/cpp
CFLAGS   = -g -Wall 
TARGET   = sacpp_archiver_enable_commander

all: $(TARGET)

$(TARGET): $(TARGET).cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(LDLIBS) $(ARCHIVE)/src/.obj/CheckStatus.o $(ARCHIVE)/src/.obj/SAL_archiver.o -o $(TARGET) $(TARGET).cpp 
