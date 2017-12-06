INCLUDE       = -I../../ocs/include
LIBPATH       = -L../../ocs/lib -Wl,-rpath,../../ocs/lib
LIB           = -lSimpleAmqpClient -lyaml-cpp
OBJ           = ../../ocs/obj/Consumer.o ../../ocs/obj/SimplePublisher.o

all: Forwarder

Forwarder: Forwarder.cpp
	g++ -std=c++11 $(INCLUDE) $(LIBPATH) $(OBJ) -o Forwarder Forwarder.cpp $(LIB)

clean: 
	rm Forwarder
