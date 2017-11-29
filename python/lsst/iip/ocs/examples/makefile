all: Publisher Subscriber

Publisher: Publisher.cpp
	g++ -std=c++11 -I../include -L../core/lib -Wl,-rpath,../core/lib64 -Wl,-rpath,../core/lib ../obj/SimplePublisher.o Publisher.cpp -g -o Publisher -lSimpleAmqpClient

Subscriber: Subscriber.cpp 
	g++ -std=c++11 -I../include -L../core/lib -Wl,-rpath,../core/lib64 -Wl,-rpath,../core/lib ../obj/Consumer.o Subscriber.cpp -g -o Subscriber -lSimpleAmqpClient -lyaml-cpp 

clean: 
	rm Publisher Subscriber
