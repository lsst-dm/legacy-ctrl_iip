INCLUDE       = -I/usr/local/include -I../../ocs/include \
		-I../../include \
		-I../include \
		-I/usr/local/boost_1_66_0 
LIBPATH       = -L/usr/local/boost_1_66_0/stage/lib \
		-Wl,-rpath,/usr/local/boost_1_66_0/stage/lib \
		-L/usr/local/lib \
		-Wl,-rpath,/usr/local/lib \
		-L/usr/local/lib64 \
		-Wl,-rpath,/usr/local/lib64 \
		-L../../lib \
		-Wl,-rpath,../../lib
DAQ_LIB       = -ldaq_daq -ldaq_ims -ldaq_dsi -ldaq_osa -ldaq_dss -ldaq_net
LOG_LIB       = -lboost_log_setup -lboost_log -lboost_thread -lboost_system -lboost_filesystem
LIB           = -lSimpleAmqpClient -lyaml-cpp -lpthread -lcfitsio -lm -lcurl
OBJ           = ../../ocs/obj/Consumer.o ../../ocs/obj/SimplePublisher.o
GCCVERSION    = -std=c++11

all: DAQForwarder

DAQForwarder: DAQForwarder.cpp
	g++ $(GCCVERSION) $(INCLUDE) $(LIBPATH) -DBOOST_LOG_DYN_LINK $(OBJ) $^ -g -o $@ $(LOG_LIB) $(LIB) $(DAQ_LIB)

clean: 
	rm DAQForwarder
