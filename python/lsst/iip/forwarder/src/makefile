INCLUDE       = -I../../ocs/include -I../include -I./
DAQ_INCLUDE       = -I../../include 
LIBPATH       = -L../../ocs/lib -Wl,-rpath,../../ocs/lib -L../lib 
DAQ_LIBPATH       = -L../../lib -Wl,-rpath,../../lib  
LIB           = -lSimpleAmqpClient -lyaml-cpp -lpthread -lcfitsio -lm -lcurl
DAQ_LIB           = -ldaq_daq -ldaq_ims -ldaq_dsi -ldaq_osa -ldaq_dss -ldaq_net
OBJ           = ../../ocs/obj/Consumer.o ../../ocs/obj/SimplePublisher.o

all: Forwarder

Forwarder: Forwarder.cpp
	g++ -std=c++11 $(DAQ_INCLUDE) $(INCLUDE) $(DAQ_LIBPATH) $(LIBPATH) $(OBJ) -g -o Forwarder Forwarder.cpp $(LIB) $(DAQ_LIB)

DAQForwarder: test.cpp
	g++ -std=c++11 $(DAQ_INCLUDE) $(INCLUDE) $(DAQ_LIBPATH) $(LIBPATH) $(OBJ) -ggdb -o test test.cpp $(LIB) $(DAQ_LIB)

clean: 
	rm Forwarder
