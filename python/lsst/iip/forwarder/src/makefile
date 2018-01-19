INCLUDE       = -I../../ocs/include -I/home/hwin16/downloads/cfitsio
LIBPATH       = -L../../ocs/lib -Wl,-rpath,../../ocs/lib -L/home/hwin16/downloads/cfitsio/lib
LIB           = -lSimpleAmqpClient -lyaml-cpp -lpthread -lcfitsio -lm -lcurl
OBJ           = ../../ocs/obj/Consumer.o ../../ocs/obj/SimplePublisher.o

all: Forwarder Formatter

Forwarder: Forwarder.cpp
	g++ -std=c++11 $(INCLUDE) $(LIBPATH) $(OBJ) -g -o Forwarder Forwarder.cpp $(LIB)

Formatter: Formatter.cpp
	g++ -std=c++11 $(INCLUDE) $(LIBPATH) $(OBJ) -g -o Formatter Formatter.cpp $(LIB)

clean: 
	rm Forwarder Formatter
