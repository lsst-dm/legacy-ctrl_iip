INCLUDE       = -I../../ocs/include -I../include
DAQ_INCLUDE       = -I../../include 
LIBPATH       = -L../../ocs/lib -Wl,-rpath,../../ocs/lib -L../lib 
DAQ_LIBPATH       = -L../../lib -Wl,-rpath,../../lib  
LIB           = -lSimpleAmqpClient -lyaml-cpp -lpthread -lcfitsio -lm -lcurl
DAQ_LIB           = -ldaq -lims -ldsi -losa -ldss -lnet
OBJ           = ../../ocs/obj/Consumer.o ../../ocs/obj/SimplePublisher.o

all: Forwarder

Forwarder: Forwarder.cpp
	g++ -std=c++11 $(INCLUDE) $(LIBPATH) $(OBJ) -g -o Forwarder Forwarder.cpp $(LIB)

ScratchForwarder: ScratchForwarder.cpp
	g++ -std=c++11 $(DAQ_INCLUDE) $(INCLUDE) $(DAQ_LIBPATH) $(LIBPATH) $(OBJ) -g -o ScratchForwarder ScratchForwarder.cpp $(DAQ_LIB) $(LIB)

DAQForwarder: DAQForwarder.cpp
	g++ -std=c++11 $(DAQ_INCLUDE) $(INCLUDE) $(DAQ_LIBPATH) $(LIBPATH) $(OBJ) -g -o DAQForwarder DAQForwarder.cpp $(DAQ_LIB) $(LIB)

clean: 
	rm Forwarder
