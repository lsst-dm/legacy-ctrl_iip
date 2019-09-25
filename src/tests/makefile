INCLUDE		= -I/opt/lsst/include -I../../include
LDPATH		= -L/opt/lsst/lib64 -L/opt/lsst/lib
LIB		= -lhiredis -lyaml-cpp
BOOST_LIB	= -lboost_log -lboost_filesystem -lboost_system -lboost_unit_test_framework
OBJ_DIR		= ../obj
OBJ		= $(addprefix $(OBJ_DIR)/, \
			RedisConnection.o \
			RedisResponse.o)
TEST_OBJ	= $(addprefix $(OBJ_DIR)/, \
		  	RedisConnectionTest.o \
			RedisResponseTest.o \
			ReadoutPatternTest.o)
FWD_OBJ 	= $(addprefix $(OBJ_DIR)/, \
		  	ReadoutPattern.o)


.PHONY: all
all: runner

core:
	make -C ../core $(OBJ)

fwd:
	make -C ../forwarder $(FWD_OBJ) 

$(OBJ_DIR)/%Test.o: %Test.cpp
	g++ -std=c++11 -DBOOST_TEST_DYN_LINK $(INCLUDE) -c $< -o $@

runner: Runner.cpp core fwd $(TEST_OBJ)
	g++ -std=c++11 -DBOOST_TEST_DYN_LINK $(INCLUDE) $(LDPATH) $(OBJ) $(FWD_OBJ) $(TEST_OBJ) $< -o $@ $(BOOST_LIB) $(LIB)

test: runner
	./runner
	rm runner
