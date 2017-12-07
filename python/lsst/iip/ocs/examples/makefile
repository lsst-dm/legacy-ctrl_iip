all: Publisher Subscriber

Publisher: Publisher.cpp
	g++ -std=c++11 -I../include -L../lib -Wl,-rpath,../lib ../obj/SimplePublisher.o Publisher.cpp -g -o Publisher -lSimpleAmqpClient

Subscriber: Subscriber.cpp 
	g++ -std=c++11 -I../include -L../lib -Wl,-rpath,../lib ../obj/Consumer.o Subscriber.cpp -g -o Subscriber -lSimpleAmqpClient -lyaml-cpp -lpthread

Subscriber_mthreads: Subscriber_mthreads.cpp 
	g++ -std=c++11 -I../include -L../lib -Wl,-rpath,../lib ../obj/Consumer.o Subscriber_mthreads.cpp -g -o Subscriber_mthreads -lSimpleAmqpClient -lyaml-cpp -lpthread

clean: 
	rm Publisher Subscriber
