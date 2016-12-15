INC	 = -I/opt/sal/test/dm/cpp/src -I/opt/sal/lsstsal/include -I$(SALPATH)/include/dcps/C++/SACPP \
-I$(SALPATH)/include/sys -I/opt/sal/test/dm/cpp -I$(SALPATH)/examples/include \
-I/usr/include/python2.7 -I/usr/local/include
SALPATH	 = /opt/sal/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux
LIBSAL	 = /opt/sal/lsstsal/lib
CC	 = g++
SOPATH   = /opt/sal/test/dm/cpp/src/.obj
LDFLAGS  = -L$(SALPATH)/lib -L$(LIBSAL) -L/usr/lib/python2.7/config -L/usr/local/lib
LDLIBS   = -l"sacpp_dm_types$(LIBSUFFIX)" -l"dcpssacpp" -l"dcpsgapi" -l"ddsuser" \
-l"ddskernel" -l"ddsserialization" -l"ddsconfparser" -l"ddsconf" -l"ddsdatabase" \
-l"ddsutil" -l"ddsos" -ldl $(subst lib,-l,$(sort $(basename $(notdir $(wildcard /usr/lib/librt.so /lib/librt.so))))) \
-lboost_python -lpthread -lpython2.7 -lSimpleAmqpClient -lyaml-cpp
CFLAGS   = -g -Wall -c 

all: CommandListener EventListener AckSubscriber

OCS_Bridge.o: OCS_Bridge.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(SOPATH)/CheckStatus.o $(SOPATH)/SAL_dm.o $(CFLAGS) $(LDLIBS) -o OCS_Bridge.o OCS_Bridge.cpp

CommandListener: CommandListener.cpp OCS_Bridge.o 
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(SOPATH)/CheckStatus.o $(SOPATH)/SAL_dm.o OCS_Bridge.o -Wall $(LDLIBS) -o CommandListener CommandListener.cpp

EventListener: EventListener.cpp OCS_Bridge.o
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(SOPATH)/CheckStatus.o $(SOPATH)/SAL_dm.o OCS_Bridge.o -Wall $(LDLIBS) -o EventListener EventListener.cpp

AckSubscriber: AckSubscriber.cpp OCS_Bridge.o
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(SOPATH)/CheckStatus.o $(SOPATH)/SAL_dm.o OCS_Bridge.o -Wall $(LDLIBS) -o AckSubscriber AckSubscriber.cpp

clean:
	rm -i *.o CommandListener EventListener AckSubscriber
