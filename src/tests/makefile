INCLUDE		= -I/opt/lsst/include -I../../include
LDPATH		= -L/opt/lsst/lib64 -L/opt/lsst/lib
LIB		= -lhiredis -lyaml-cpp -lcfitsio
BOOST_LIB	= -lboost_log -lboost_filesystem -lboost_system -lboost_unit_test_framework
OBJ_DIR		= ../obj
OBJ		= $(addprefix $(OBJ_DIR)/, \
		  	FitsOpener.o \
		  	YAMLFormatter.o \
			RedisConnection.o \
			RedisResponse.o)
TEST_OBJ	= $(addprefix $(OBJ_DIR)/, \
			YAMLFormatterTest.o \
		  	RedisConnectionTest.o \
			RedisResponseTest.o)


.PHONY: all
all: runner

core:
	make -C ../core $(OBJ)

$(OBJ_DIR)/%Test.o: %Test.cpp
	g++ -std=c++11 $(INCLUDE) -c $< -o $@

runner: Runner.cpp core $(TEST_OBJ)
	g++ -std=c++11 $(INCLUDE) $(LDPATH) $(OBJ) $(TEST_OBJ) $< -o $@ $(BOOST_LIB) $(LIB)

test: runner
	./runner
	rm runner
