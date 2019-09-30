INCLUDE		= -I$(EXPORT_ROOT)/include -I/opt/lsst/include -I../../include
LDPATH		= -L$(EXPORT_ROOT)/x86/lib -L/opt/lsst/lib64 -L/opt/lsst/lib -L../lib
LIB		= -llsst_l1_forwarder -llsst_l1_core -ldaq_ims -ldaq_daq -ldaq_dsi \
		  -lcfitsio -lyaml-cpp -lboost_log -lboost_system -lboost_filesystem \
		  -lboost_thread -lpthread -lcurl -lSimpleAmqpClient -lhiredis \
		  -lboost_unit_test_framework
OBJ_DIR		= ../obj
TEST_OBJ	= $(addprefix $(OBJ_DIR)/, \
		  	RabbitConnectionTest.o \
		  	RedisConnectionTest.o \
			ReadoutPatternTest.o \
			miniforwarderTest.o)
FWD_OBJ 	= ../obj/miniforwarder.o

.PHONY: all

all: runner

lib:
	make -C ../forwarder ../lib/liblsst_l1_core.so ../lib/liblsst_l1_forwarder.so

$(OBJ_DIR)/%Test.o: %Test.cpp
	g++ -std=c++11 -DBOOST_TEST_DYN_LINK $(INCLUDE) -c $< -o $@

runner: Runner.cpp lib $(TEST_OBJ)
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK -DBOOST_TEST_DYN_LINK $(INCLUDE) $(LDPATH) $(TEST_OBJ) $< -o $@ $(LIB)

test: runner
	./runner
	rm runner
