INCLUDE       = -I../../ocs/include -I../include
LIBPATH       = -L../../ocs/lib -Wl,-rpath,../../ocs/lib -L../lib, ../lib 
LIB           = -lSimpleAmqpClient -lyaml-cpp -lpthread -lcfitsio -lm -lcurl
OBJ           = ../../ocs/obj/Consumer.o ../../ocs/obj/SimplePublisher.o

all: Forwarder

Forwarder: Forwarder.cpp
	g++ -std=c++11 $(INCLUDE) $(LIBPATH) $(OBJ) -g -o Forwarder Forwarder.cpp $(LIB)

clean: 
	rm Forwarder
