INCLUDE		= -I/opt/lsst/include \
		  -I../../include/core \
		  -I../../include/ocs
LDPATH		= -L/opt/lsst/lib 
LOG_LIB         = -lboost_log -lboost_filesystem -lboost_system -lboost_thread
LIBS		= -lyaml-cpp -lpthread
OBJ_DIR		= ../obj
OBJ		= SimplePublisher.o Consumer.o SimpleLogger.o Toolsmod.o IIPBase.o Credentials.o

all: builddir $(OBJ)
.PHONY: clean

builddir:
	mkdir -p $(OBJ_DIR)

SimplePublisher.o: SimplePublisher.cpp
	g++ -std=c++11 $(INCLUDE) $(LDPATH) -c -o $(OBJ_DIR)/$@ $< -lSimpleAmqpClient 

Consumer.o: Consumer.cpp 
	g++ -std=c++11 $(INCLUDE) $(LDPATH) -c -o $(OBJ_DIR)/$@ $< -lSimpleAmqpClient 

SimpleLogger.o: SimpleLogger.cpp
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK $(INCLUDE) $(LDPATH) $< -c -o $(OBJ_DIR)/$@ $(LOG_LIB)

Toolsmod.o: Toolsmod.cpp
	g++ -std=c++11 $(INCLUDE) -c -o $(OBJ_DIR)/$@ $<

Credentials.o: Credentials.cpp SimpleLogger.o
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK $(INCLUDE) $(LDPATH) $(OBJ_DIR)/SimpleLogger.o $< -c -o $(OBJ_DIR)/$@ $(LOG_LIB)

IIPBase.o: IIPBase.cpp SimpleLogger.o SimplePublisher.o Credentials.o
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK $(INCLUDE) $(LDPATH) $(OBJ_DIR)/SimplePublisher.o $(OBJ_DIR)/Credentials.o $(OBJ_DIR)/SimpleLogger.o $< -c -o $(OBJ_DIR)/$@ $(LOG_LIB)

A: A.cpp IIPBase.o SimpleLogger.o Credentials.o
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK $(INCLUDE) $(LDPATH) $(OBJ_DIR)/SimpleLogger.o $(OBJ_DIR)/Credentials.o $(OBJ_DIR)/IIPBase.o $< -o $@ -lpthread $(LOG_LIB) $(LIBS)

clean:
	rm $(OBJ_DIR)/$(OBJ)
