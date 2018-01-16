all: Publisher Subscriber

Publisher: Publisher.cpp
	g++ -std=c++11 -I../include -L../lib -Wl,-rpath,../lib ../obj/SimplePublisher.o Publisher.cpp -g -o Publisher -lSimpleAmqpClient

Subscriber: Subscriber.cpp 
	g++ -std=c++11 -I../include -L../lib -Wl,-rpath,../lib ../obj/Consumer.o Subscriber.cpp -g -o Subscriber -lSimpleAmqpClient -lyaml-cpp -lpthread

Subscriber2: Subscriber2.cpp 
	g++ -std=c++11 -I../include -L../lib -Wl,-rpath,../lib ../obj/Consumer.o Subscriber2.cpp -g -o Subscriber2 -lSimpleAmqpClient -lyaml-cpp -lpthread
clean: 
	rm Publisher Subscriber
