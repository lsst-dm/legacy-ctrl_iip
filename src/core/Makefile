INCLUDE		= -I/opt/lsst/include \
		  -I../../include/core \
		  -I../../include/ocs
LDPATH		= -L/opt/lsst/lib 
LOG_LIB         = -lboost_log -lboost_system -lboost_thread
LIBS		= -lyaml-cpp
OBJ_DIR		= ../obj

all: builddir SimplePublisher Consumer SimpleLogger IIPBase

builddir:
	mkdir -p $(OBJ_DIR)

SimplePublisher: SimplePublisher.cpp
	g++ -std=c++11 $(INCLUDE) $(LDPATH) -c -o $(OBJ_DIR)/$@.o $^ -lSimpleAmqpClient 

Consumer: Consumer.cpp 
	g++ -std=c++11 $(INCLUDE) $(LDPATH) -c -o $(OBJ_DIR)/$@.o $^ -lSimpleAmqpClient 

SimpleLogger: SimpleLogger.cpp
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK $(INCLUDE) $(LDPATH) $< -c -o $(OBJ_DIR)/$@.o $(LOG_LIB)

IIPBase: IIPBase.cpp SimpleLogger
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK $(INCLUDE) $(LDPATH) $(OBJ_DIR)/SimpleLogger.o $< -c -o $(OBJ_DIR)/$@.o $(LOG_LIB)

A: A.cpp IIPBase SimpleLogger
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK $(INCLUDE) $(LDPATH) $(OBJ_DIR)/SimpleLogger.o $(OBJ_DIR)/IIPBase.o $< -o $@ -lpthread $(LOG_LIB) $(LIBS)
