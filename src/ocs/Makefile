LSST_BUILDDIR  = /opt/lsst
DM_BUILDDIR    = /opt/lsst/dm-prompt
OSPL_PATH      = /opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux
AR             = /opt/sal/ts_sal/test/MTArchiver/cpp
CU             = /opt/sal/ts_sal/test/CatchupArchiver/cpp
PP             = /opt/sal/ts_sal/test/PromptProcessing/cpp
AT             = /opt/sal/ts_sal/test/ATArchiver/cpp
ATC            = /opt/sal/ts_sal/test/ATCamera/cpp
MTC            = /opt/sal/ts_sal/test/MTCamera/cpp
EFD            = /opt/sal/ts_sal/test/EFD/cpp
SAL_INCLUDE    = -I/opt/sal/ts_sal/lsstsal/include \
		 -I$(OSPL_PATH)/include/dcps/C++/SACPP \
		 -I$(OSPL_PATH)/include/sys \
		 -I$(OSPL_PATH)/include
DM_INCLUDE     = -I../../include/ocs \
		 -I$(LSST_BUILDDIR)/include \
		 -I/opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux/include/dcps/C++/SACPP \
		 -I$(AR) -I$(AR)/src \
		 -I$(CU) -I$(CU)/src \
		 -I$(PP) -I$(PP)/src \
		 -I$(AT) -I$(AT)/src \
		 -I$(MTC) -I$(MTC)/src \
		 -I$(ATC) -I$(ATC)/src \
		 -I$(EFD) -I$(EFD)/src 
SAL_LDPATH     = -L/opt/sal/ts_sal/lsstsal/lib -Wl,-rpath,/opt/sal/ts_sal/lsstsal/lib \
		 -L$(OSPL_PATH)/lib -Wl,-rpath,$(OSPL_PATH)/lib
DM_LDPATH      = -L$(LSST_BUILDDIR)/lib -Wl,-rpath,$(LSST_BUILDDIR)/lib \
		 -L$(LSST_BUILDDIR)/lib64 -Wl,-rpath,$(LSST_BUILDDIR)/lib64 
L1_LIB         = -lpthread -lyaml-cpp -lSimpleAmqpClient
SAL_LIB        = -lsacpp_MTArchiver_types \
		 -lsacpp_CatchupArchiver_types \
		 -lsacpp_PromptProcessing_types \
		 -lsacpp_ATArchiver_types \
		 -lsacpp_MTCamera_types \
		 -lsacpp_ATCamera_types \
		 -lsacpp_EFD_types \
		 -ldcpssacpp -lddskernel
DM_OBJ         = $(AR)/src/.obj/SAL_MTArchiver.o \
		 $(CU)/src/.obj/SAL_CatchupArchiver.o \
		 $(PP)/src/.obj/SAL_PromptProcessing.o \
		 $(AT)/src/.obj/SAL_ATArchiver.o \
		 $(MTC)/src/.obj/SAL_MTCamera.o \
		 $(ATC)/src/.obj/SAL_ATCamera.o \
		 $(EFD)/src/.obj/SAL_EFD.o 
L1_OBJ         = ../obj/OCS_Bridge.o ../obj/SimplePublisher.o ../obj/Toolsmod.o
OBJ_DIR        = ../obj
BIN_DIR	       = ../../bin

all: CommandListener EventSubscriber AckSubscriber

CommandListener: CommandListener.cpp
	g++ -std=c++11 $(SAL_INCLUDE) $(DM_INCLUDE) $(SAL_LDPATH) $(DM_LDPATH) $(DM_OBJ) $(L1_OBJ) -o $(BIN_DIR)/$@ $< $(SAL_LIB) $(L1_LIB)

EventSubscriber: EventSubscriber.cpp
	g++ -std=c++11 $(SAL_INCLUDE) $(DM_INCLUDE) $(SAL_LDPATH) $(DM_LDPATH) $(DM_OBJ) $(L1_OBJ) -o $(BIN_DIR)/$@ $< $(SAL_LIB) $(L1_LIB)

AckSubscriber: AckSubscriber.cpp
	g++ -std=c++11 $(SAL_INCLUDE) $(DM_INCLUDE) $(SAL_LDPATH) $(DM_LDPATH) $(DM_OBJ) $(L1_OBJ) ../obj/Consumer.o -o $(BIN_DIR)/$@ $< $(SAL_LIB) $(L1_LIB)

install:
	install -d $(DM_BUILDDIR)/include $(DM_BUILDDIR)/bin
	install -m 755 -D ../include/* $(DM_BUILDDIR)/include
	install -m 755 -D ../bin/* $(DM_BUILDDIR)/bin

clean: 
	rm $(BIN_DIR)/CommandListener \
	   $(BIN_DIR)/EventSubscriber \
	   $(BIN_DIR)/AckSubscriber
