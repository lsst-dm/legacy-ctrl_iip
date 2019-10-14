INCLUDE		= -I$(EXPORT_ROOT)/include -I/usr/local/include -I../../include
LDPATH		= -L$(EXPORT_ROOT)/x86/lib\
		  -L/usr/local/lib64\
		  -L/usr/local/lib\
		  -L../lib
LIB_DIR		= ../lib
LIB		= -llsst_l1_forwarder -llsst_l1_core -llsst_l1_tests\
		  -ldaq_ims -ldaq_daq -ldaq_dsi\
		  -lboost_thread -lboost_log -lboost_system -lboost_filesystem\
		  -lboost_unit_test_framework\
		  -lpthread -lcurl -lSimpleAmqpClient -lhiredis\
		  -lcfitsio -lyaml-cpp
OBJ_DIR		= ../obj
OBJ		= $(addprefix $(OBJ_DIR)/, \
		  	BeaconTest.o \
		  	RabbitConnectionTest.o \
		  	RedisConnectionTest.o \
		  	RedisResponseTest.o \
			ReadoutPatternTest.o \
			miniforwarderTest.o \
			WatcherTest.o)

.PHONY: all lib

all: runner

lib:
	$(MAKE) -C ../forwarder ../lib/liblsst_l1_core.so ../lib/liblsst_l1_forwarder.so

$(OBJ_DIR)/%.o: %.cpp
	g++ -std=c++11 -fPIC -DBOOST_TEST_DYN_LINK $(INCLUDE) -c $< -o $@

$(LIB_DIR)/liblsst_l1_tests.so: $(OBJ)
	gcc -shared $(OBJ) -o $@

runner: Runner.cpp lib $(LIB_DIR)/liblsst_l1_tests.so
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK -DBOOST_TEST_DYN_LINK -g $(INCLUDE) $(LDPATH) $< -o $@ $(LIB)

test: runner
	./runner
	rm runner
