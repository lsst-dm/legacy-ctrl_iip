INCLUDE		= -I/opt/lsst/include -I../../include
LDPATH		= -L/opt/lsst/lib 
LOG_LIB         = -lboost_log -lboost_filesystem -lboost_system -lboost_thread
LIBS		= -lyaml-cpp -lpthread
OBJ		= $(addprefix ../obj/, \
			Consumer.o \
			Credentials.o \
			FileOpener.o \
			IIPBase.o \
			RabbitConnection.o \
			RedisConnection.o \
			RedisResponse.o \
			SimpleLogger.o \
			SimplePublisher.o )
LIB_DIR		= ../lib
OBJ_DIR		= ../obj

.PHONY: clean mkdir all

all: $(LIB_DIR)/liblsst_l1_core.so

mkdir:
	mkdir -p $(OBJ_DIR) $(LIB_DIR)

$(OBJ_DIR)/%.o: %.cpp
	g++ -std=c++11 -fPIC -DBOOST_LOG_DYN_LINK -c $(INCLUDE) $< -o $@

$(LIB_DIR)/liblsst_l1_core.so: mkdir $(OBJ)
	gcc -shared $(OBJ) -o $@

clean:
	rm $(OBJ) $(LIB_DIR)/liblsst_l1_core.so
