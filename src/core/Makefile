INCLUDE		= -I/opt/lsst/include \
		  -I../../include
LDPATH		= -L/opt/lsst/lib 
LOG_LIB         = -lboost_log -lboost_filesystem -lboost_system -lboost_thread
LIBS		= -lyaml-cpp -lpthread
OBJ_DIR		= ../obj
OBJ		= $(OBJ_DIR)/SimplePublisher.o \
	          $(OBJ_DIR)/Consumer.o \
	          $(OBJ_DIR)/SimpleLogger.o \
	          $(OBJ_DIR)/Toolsmod.o \
	          $(OBJ_DIR)/IIPBase.o \
	          $(OBJ_DIR)/Credentials.o

all: builddir $(OBJ)
.PHONY: clean

builddir:
	mkdir -p $(OBJ_DIR)

$(OBJ_DIR)/%.o: %.cpp
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK $(INCLUDE) -c -o $@ $<

clean:
	rm $(OBJ_DIR)/$(OBJ)
