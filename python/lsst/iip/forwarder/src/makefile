include ../../ocs/src/makefile
RELEASE	      = /home/lsst-daq/daq-sdk/current
INCLUDE       = -I../../ocs/include \
		-I../include \
		-I../../include \
		-I/usr/local/boost_1_66_0
DAQ_INCLUDE   = -I/home/lsst-daq/daq-sdk/current/include 
LIBPATH       = -L../../lib -Wl,-rpath,../../lib \
		-L/usr/local/lib -Wl,-rpath,/usr/local/lib \
		-L/usr/local/lib64 -Wl,-rpath,/usr/local/lib64 \
		-L/usr/local/boost_1_66_0/stage/lib -Wl,-rpath,/usr/local/boost_1_66_0/stage/lib
DAQ_LIBPATH   = -L/home/lsst-daq/daq-sdk/current/x86/lib -Wl,-rpath,/home/lsst-daq/daq-sdk/current/x86/lib  
LIB           = -lSimpleAmqpClient -lyaml-cpp -lpthread -lcfitsio -lm -lcrypto -lcurl
DAQ_LIB       = -ldaq_daq -ldaq_ims -ldaq_dsi -ldaq_osa -ldaq_dss -ldaq_net
LOG_LIB       = -lboost_log_setup -lboost_log -lboost_thread -lboost_system -lboost_filesystem
OBJ           = $(ROOT_DIR)/ocs/obj/Consumer.o $(ROOT_DIR)/ocs/obj/SimplePublisher.o

all: Forwarder

Forwarder: Forwarder.cpp SimplePublisher Consumer
	g++ -std=c++11 $(DAQ_INCLUDE) $(INCLUDE) $(DAQ_LIBPATH) $(LIBPATH) $(OBJ) -DBOOST_LOG_DYN_LINK -ggdb -o Forwarder Forwarder.cpp $(LIB) $(DAQ_LIB) $(LOG_LIB)

clean: 
	rm Forwarder


