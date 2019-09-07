#LSST_PATH       = /opt/lsst
#RELEASE		= /srv/nfs/lsst-daq/daq-sdk/current
#INCLUDE         = -I../../include/core -I../../include/forwarder -I$(LSST_PATH)/include
#DAQ_INCLUDE     = -I$(RELEASE)/include 
#LIBPATH         = -L$(LSST_PATH)/lib -Wl,-rpath,$(LSST_PATH)/lib \
#		  -L$(LSST_PATH)/lib64 -Wl,-rpath,$(LSST_PATH)/lib64
#DAQ_LIBPATH     = -L$(RELEASE)/x86/lib -Wl,-rpath,$(RELEASE)/x86/lib  
#LIB             = -lSimpleAmqpClient -lyaml-cpp -lpthread -lcfitsio -lm -lcurl
#DAQ_LIB         = -ldaq_daq -ldaq_ims -ldaq_dsi -ldaq_osa -ldaq_dss -ldaq_net -lcrypto
#LOG_LIB         = -lboost_log -lboost_system -lboost_filesystem -lboost_thread
#OBJ_RULES       = IIPBase.o SimpleLogger.o SimplePublisher.o Toolsmod.o Consumer.o Credentials.o
#OBJ		= $(addprefix ../obj/,$(OBJ_RULES))
#BIN_DIR         = ../../bin
#
#all: DAQForwarder
#
#.PHONY: all dependency
#
#dependency:
#	$(MAKE) -C ../core $(OBJ)
#
#DAQForwarder: DAQForwarder.cpp dependency
#	g++ -std=c++11 -DBOOST_LOG_DYN_LINK $(DAQ_INCLUDE) $(INCLUDE) $(DAQ_LIBPATH) $(LIBPATH) $(OBJ) -ggdb -o $(BIN_DIR)/$@ $< $(LIB) $(DAQ_LIB) $(LOG_LIB)
#
#clean: 
#	rm $(BIN_DIR)/DAQForwarder
#

INCLUDE		= -I$(EXPORT_ROOT)/include -I/opt/lsst/include \
		  -I../../include -I/usr/include
LIBPATH		= -L$(EXPORT_ROOT)/x86/lib -L/opt/lsst/lib -L/usr/lib64
LIB		= -ldaq_ims -ldaq_daq -ldaq_dsi -lcfitsio -lboost_log \
		  -lboost_system -lboost_filesystem -lboost_thread -lpthread \
		  -lcurl -lSimpleAmqpClient -lyaml-cpp -lhiredis
OBJ		= $(addprefix ../obj/, \
			FileSender.o \
			Scoreboard.o \
			FitsOpener.o \
			FileOpener.o \
			PixelArray.o \
			StripeArray.o \
			Formatter.o \
			FitsFormatter.o \
			HeaderFetcher.o \
			CURLHandle.o \
			DAQFetcher.o \
			MessageBuilder.o \
			RedisResponse.o)
RMQ_OBJ       	= $(addprefix ../obj/, \
			RabbitConnection.o \
			IIPBase.o \
			SimpleLogger.o \
			SimplePublisher.o \
			Consumer.o \
			Credentials.o)

.PHONY: core mkdir

all: ../../bin/fwd

mkdir:
	mkdir -p ../obj

../obj/%.o: %.cpp
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK -pg -g -c $(INCLUDE) $< -o $@

core:
	$(MAKE) -C ../core $(RMQ_OBJ)

../../bin/fwd: miniforwarder.cpp mkdir core $(OBJ)
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK -pg -g $(INCLUDE) $(LIBPATH) $(OBJ) $(RMQ_OBJ) $< -o $@ $(LIB)

RedisConnection: RedisConnection.cpp ../obj/RedisResponse.o
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK -pg -g $(INCLUDE) $(LIBPATH) $(OBJ) $(RMQ_OBJ) $< -o $@ $(LIB)
