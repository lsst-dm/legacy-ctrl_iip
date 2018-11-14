AR             = /opt/sal/ts_sal/test/MTArchiver/cpp
CU             = /opt/sal/ts_sal/test/CatchupArchiver/cpp
PP             = /opt/sal/ts_sal/test/PromptProcessing/cpp
AT             = /opt/sal/ts_sal/test/ATArchiver/cpp
ATC            = /opt/sal/ts_sal/test/ATCamera/cpp
MTC            = /opt/sal/ts_sal/test/MTCamera/cpp
EFD            = /opt/sal/ts_sal/test/EFD/cpp
SAL_INCLUDE    = -I/opt/sal/ts_sal/lsstsal/include \
		 -I/opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux/include/dcps/C++/SACPP
DM_INCLUDE     = -I../include \
		 -I$(AR) -I$(AR)/src \
		 -I$(CU) -I$(CU)/src \
		 -I$(PP) -I$(PP)/src \
		 -I$(AT) -I$(AT)/src \
		 -I$(MTC) -I$(MTC)/src \
		 -I$(ATC) -I$(ATC)/src \
		 -I$(EFD) -I$(EFD)/src 
SAL_LDPATH     = -L/opt/sal/ts_sal/lsstsal/lib \
		 -L/opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux/lib
DM_LDPATH      = -L/usr/local/lib -Wl,-rpath,/usr/local/lib \
		 -L/usr/local/lib64 -Wl,-rpath,/usr/local/lib64 
L1_LIB         = -lpthread -lyaml-cpp -lSimpleAmqpClient
SAL_LIB        = -lsacpp_MTArchiver_types \
		 -lsacpp_CatchupArchiver_types \
		 -lsacpp_PromptProcessing_types \
		 -lsacpp_ATArchiver_types \
		 -lsacpp_MTCamera_types \
		 -lsacpp_ATCamera_types \
		 -lsacpp_EFD_types \
		 -ldcpssacpp -lddskernel
DM_OBJ         = $(AR)/src/.obj/SAL_MTArchiver.o \
		 $(CU)/src/.obj/SAL_CatchupArchiver.o \
		 $(PP)/src/.obj/SAL_PromptProcessing.o \
		 $(AT)/src/.obj/SAL_ATArchiver.o \
		 $(MTC)/src/.obj/SAL_MTCamera.o \
		 $(ATC)/src/.obj/SAL_ATCamera.o \
		 $(EFD)/src/.obj/SAL_EFD.o 
L1_OBJ         = ../obj/OCS_Bridge.o ../obj/SimplePublisher.o ../obj/Toolsmod.o

all: CommandListener EventSubscriber AckSubscriber

OCS_Bridge: OCS_Bridge.cpp SimplePublisher
	$(CC) $(COMPVERS) $(INCLUDE) $(DM_LDPATH) $(OBJ_DIR)/SimplePublisher.o -c -o $(OBJ_DIR)/OCS_Bridge.o OCS_Bridge.cpp -lSimpleAmqpClient -lyaml-cpp 

SimplePublisher: SimplePublisher.cpp
	$(CC) $(COMPVERS) $(INCLUDE) $(DM_LDPATH) -c -o $(OBJ_DIR)/SimplePublisher.o SimplePublisher.cpp -lSimpleAmqpClient 

Consumer: Consumer.cpp 
	$(CC) $(COMPVERS) $(INCLUDE) $(DM_LDPATH) -c -o $(OBJ_DIR)/Consumer.o Consumer.cpp -lSimpleAmqpClient 

Toolsmod: Toolsmod.cpp
	$(CC) $(COMPVERS) $(INCLUDE) -c -o ../obj/Toolsmod.o Toolsmod.cpp

CommandListener: CommandListener.cpp SimplePublisher Toolsmod OCS_Bridge
	g++ -std=c++11 $(SAL_INCLUDE) $(DM_INCLUDE) $(SAL_LDPATH) $(DM_LDPATH) $(DM_OBJ) $(L1_OBJ) -o $@ $^ $(SAL_LIB) $(L1_LIB)

EventSubscriber: EventSubscriber.cpp SimplePublisher
	g++ -std=c++11 $(SAL_INCLUDE) $(DM_INCLUDE) $(SAL_LDPATH) $(DM_LDPATH) $(DM_OBJ) $(L1_OBJ) -o $@ $^ $(SAL_LIB) $(L1_LIB)

AckSubscriber: AckSubscriber.cpp Consumer
	g++ -std=c++11 $(SAL_INCLUDE) $(DM_INCLUDE) $(SAL_LDPATH) $(DM_LDPATH) $(DM_OBJ) $(L1_OBJ) -o $@ $^ $(SAL_LIB) $(L1_LIB)

clean: 
	rm -i CommandListener EventSubscriber AckSubscriber
