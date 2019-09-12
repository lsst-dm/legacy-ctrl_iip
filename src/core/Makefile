INCLUDE		= -I/opt/lsst/include -I../../include
LDPATH		= -L/opt/lsst/lib 
LOG_LIB         = -lboost_log -lboost_filesystem -lboost_system -lboost_thread
LIBS		= -lyaml-cpp -lpthread
OBJ		= $(addprefix ../obj/, \
		      RabbitConnection.o \
		      RedisConnection.o \
		      RedisResponse.o \
		      SimplePublisher.o \
		      Consumer.o \
		      SimpleLogger.o \
		      IIPBase.o \
		      Credentials.o)

.PHONY: clean mkdir

all: $(OBJ)

mkdir:
	mkdir -p $(OBJ_DIR)

../obj/%.o: %.cpp
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK -c $(INCLUDE) $< -o $@

clean:
	rm $(OBJ)
