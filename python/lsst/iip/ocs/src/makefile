INC	 = -I/opt/sal/test/dm/cpp/src\
-I/opt/sal/lsstsal/include\
-I$(SALPATH)/include/dcps/C++/SACPP\
-I$(SALPATH)/include/sys\
-I/opt/sal/test/dm/cpp\
-I$(SALPATH)/examples/include -I/opt/sal/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux/include/sys\
-I/usr/local/include -I/opt/sal/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux/include
SALPATH	 = /opt/sal/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux
LIBSAL	 = /opt/sal/lsstsal/lib
CC	 = g++
SOPATH   = /opt/sal/test/dm/cpp/src/.obj
LDFLAGS  = -L$(SALPATH)/lib -L$(LIBSAL) -L/usr/lib/python2.7/config -L/usr/local/lib -L/opt/sal/test/dm/cpp
LDLIBS   = -lsacpp_dm_types -l"sacpp_dm_types$(LIBSUFFIX)" -l"dcpssacpp" -l"dcpsgapi" -l"ddsuser" \
-l"ddskernel" -l"ddsserialization" -l"ddsconfparser" -l"ddsconf" -l"ddsdatabase" \
-l"ddsutil" -l"ddsos" -ldl $(subst lib,-l,$(sort $(basename $(notdir $(wildcard /usr/lib/librt.so /lib/librt.so))))) \
-lpthread -lpython2.7 -lSimpleAmqpClient -lyaml-cpp
CFLAGS   = -g -Wall -c 

all: CommandListener EventListener AckSubscriber SimplePublisher Consumer

OCS_Bridge: OCS_Bridge.cpp SimplePublisher
	$(CC) -std=c++11 -I.. -L/usr/local/lib -lSimpleAmqpClient -lyaml-cpp SimplePublisher.o -c -o OCS_Bridge.o OCS_Bridge.cpp

CommandListener: CommandListener.cpp OCS_Bridge
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(SOPATH)/CheckStatus.o $(SOPATH)/SAL_dm.o OCS_Bridge.o SimplePublisher.o -Wall -o CommandListener CommandListener.cpp $(LDLIBS) 

EventListener: EventListener.cpp OCS_Bridge
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(SOPATH)/CheckStatus.o $(SOPATH)/SAL_dm.o OCS_Bridge.o SimplePublisher.o -Wall -o EventListener EventListener.cpp $(LDLIBS) 

AckSubscriber: AckSubscriber.cpp Consumer
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(SOPATH)/CheckStatus.o $(SOPATH)/SAL_dm.o Consumer.o -Wall -o AckSubscriber AckSubscriber.cpp $(LDLIBS) 

SimplePublisher: SimplePublisher.cpp
	$(CC) -L/usr/local/lib -lSimpleAmqpClient -c -o SimplePublisher.o SimplePublisher.cpp

Consumer: Consumer.cpp 
	$(CC) -L/usr/local/lib -lSimpleAmqpClient -c -o Consumer.o Consumer.cpp

clean:
	rm -i *.o CommandListener EventListener AckSubscriber
