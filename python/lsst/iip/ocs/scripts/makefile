CC	= g++ 
INCLUDE	= -I$(AT) -I$(AT)/src -I$(TS_SAL) -I$(SPLICE)\
          -I$(ATCAMERA) -I$(ATCAMERA)/src\
	  -I$(ATHEADER) -I$(ATHEADER)/src\
	  -I$(EFD) -I$(EFD)/src
LDSAL	= -L/opt/sal/ts_sal/lsstsal/lib -L$(SALPATH)/lib
SALPATH	= /opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux
LDLIBS	= -lsacpp_atArchiver_types -lpthread \
	  -lsacpp_atcamera_types\
	  -lsacpp_efd_types\
	  -lsacpp_atHeaderService_types\
	  -l"dcpssacpp" -l"dcpsgapi" -l"ddsuser" \
	  -l"ddskernel" -l"ddsserialization" -l"ddsconfparser" -l"ddsconf" -l"ddsdatabase" \
	  -l"ddsutil" -l"ddsos" -ldl $(subst lib,-l,$(sort $(basename $(notdir $(wildcard /usr/lib/librt.so /lib/librt.so)))))
TS_SAL	= /opt/sal/ts_sal/lsstsal/include
SPLICE	= /opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux/include/dcps/C++/SACPP
OBJ	= $(AT)/src/.obj/SAL_atArchiver.o\
	  $(ATHEADER)/src/.obj/SAL_atHeaderService.o\
	  $(ATCAMERA)/src/.obj/SAL_atcamera.o\
	  $(EFD)/src/.obj/SAL_efd.o
AT	= /opt/sal/ts_sal/test/atArchiver/cpp
ATCAMERA= /opt/sal/ts_sal/test/atcamera/cpp
ATHEADER= /opt/sal/ts_sal/test/atHeaderService/cpp
EFD	= /opt/sal/ts_sal/test/efd/cpp

all: emulator

emulator: emulator.cpp
	$(CC) -std=c++11 $(INCLUDE) $(LDSAL) $(OBJ) $^ -o $@ $(LDLIBS)
