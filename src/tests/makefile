INCLUDE		= -I/opt/lsst/include -I../../include
LDPATH		= -L/opt/lsst/lib64 -L/opt/lsst/lib
LIB		= -lhiredis -lyaml-cpp -lpthread -lSimpleAmqpClient
BOOST_LIB	= -lboost_log -lboost_filesystem -lboost_system \
		  -lboost_thread -lboost_unit_test_framework
OBJ_DIR		= ../obj
SUP_OBJ		= $(addprefix $(OBJ_DIR)/, \
		  	IIPBase.o \
			SimpleLogger.o \
			Credentials.o)
CORE_OBJ	= $(addprefix $(OBJ_DIR)/, \
			RabbitConnection.o)
TEST_OBJ	= $(patsubst $(OBJ_DIR)/%.o, $(OBJ_DIR)/%Test.o, $(CORE_OBJ))

.PHONY: all

all: runner

core:
	make -C ../core $(CORE_OBJ) $(SUP_OBJ)

fwd:
	make -C ../forwarder $(FWD_OBJ) 

$(OBJ_DIR)/%Test.o: %Test.cpp
	g++ -std=c++11 -DBOOST_TEST_DYN_LINK $(INCLUDE) -c $< -o $@

runner: Runner.cpp core $(TEST_OBJ)
	g++ -std=c++11 -DBOOST_TEST_DYN_LINK $(INCLUDE) $(LDPATH) $(OBJ) $(SUP_OBJ) $(CORE_OBJ) $(TEST_OBJ) $< -o $@ $(BOOST_LIB) $(LIB)

test: runner
	./runner
	rm runner
