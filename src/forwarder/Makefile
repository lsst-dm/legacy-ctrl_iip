LSST_PATH       = /opt/lsst
RELEASE		= /srv/nfs/lsst-daq/daq-sdk/current
INCLUDE         = -I../../include/core -I../../include/forwarder -I$(LSST_PATH)/include
DAQ_INCLUDE     = -I$(RELEASE)/include 
LIBPATH         = -L$(LSST_PATH)/lib -Wl,-rpath,$(LSST_PATH)/lib \
		  -L$(LSST_PATH)/lib64 -Wl,-rpath,$(LSST_PATH)/lib64
DAQ_LIBPATH     = -L$(RELEASE)/x86/lib -Wl,-rpath,$(RELEASE)/x86/lib  
LIB             = -lSimpleAmqpClient -lyaml-cpp -lpthread -lcfitsio -lm -lcurl
DAQ_LIB         = -ldaq_daq -ldaq_ims -ldaq_dsi -ldaq_osa -ldaq_dss -ldaq_net -lcrypto
LOG_LIB         = -lboost_log -lboost_system -lboost_thread
OBJ_RULES       = IIPBase.o SimpleLogger.o SimplePublisher.o Toolsmod.o Consumer.o
OBJ		= $(addprefix ../obj/,$(OBJ_RULES))
BIN_DIR         = ../../bin

all: DAQForwarder

.PHONY: all dependency

dependency:
	$(MAKE) -C ../core $(OBJ_RULES)

DAQForwarder: DAQForwarder.cpp dependency
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK $(DAQ_INCLUDE) $(INCLUDE) $(DAQ_LIBPATH) $(LIBPATH) $(OBJ) -ggdb -o $(BIN_DIR)/$@ $< $(LIB) $(DAQ_LIB) $(LOG_LIB)

clean: 
	rm $(BIN_DIR)/DAQForwarder
