INCLUDE		= -I$(EXPORT_ROOT)/include -I/opt/lsst/include \
		  -I../../include
LDPATH		= -L$(EXPORT_ROOT)/x86/lib -L/usr/local/lib -L/usr/local/lib64 -L../lib
BIN_DIR		= ../../bin
LIB_DIR		= ../lib
OBJ_DIR		= ../obj
OBJ		= $(addprefix ../obj/, \
			CURLHandle.o \
			DAQFetcher.o \
			FileSender.o \
			FitsOpener.o \
			FitsFormatter.o \
			Formatter.o \
			HeaderFetcher.o \
			MessageBuilder.o \
			miniforwarder.o \
			PixelArray.o \
			ReadoutPattern.o \
			Scoreboard.o \
			StripeArray.o)
LIB		= -llsst_l1_forwarder -llsst_l1_core -ldaq_ims -ldaq_daq -ldaq_dsi \
		  -lcfitsio -lyaml-cpp -lboost_log -lboost_system -lboost_filesystem \
		  -lboost_thread -lpthread -lcurl -lSimpleAmqpClient -lhiredis

.PHONY: core clean $(LIB_DIR)/liblsst_l1_core.so

all: release

mkdir:
	mkdir -p $(OBJ_DIR) $(LIB_DIR) $(BIN_DIR)

$(OBJ_DIR)/%.o: %.cpp
	g++ -std=c++11 -fPIC -DBOOST_LOG_DYN_LINK -g -c $(INCLUDE) $< -o $@

$(LIB_DIR)/liblsst_l1_core.so:
	$(MAKE) -C ../core $@

$(LIB_DIR)/liblsst_l1_forwarder.so: $(OBJ)
	gcc -shared $(OBJ) -o $@

debug: main.cpp mkdir $(LIB_DIR)/liblsst_l1_core.so $(LIB_DIR)/liblsst_l1_forwarder.so
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK -pg -g $(INCLUDE) $(LDPATH) $< -o $(BIN_DIR)/debug $(LIB)

release: main.cpp mkdir $(LIB_DIR)/liblsst_l1_core.so $(LIB_DIR)/liblsst_l1_forwarder.so
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK $(INCLUDE) $(LDPATH) $< -o $(BIN_DIR)/Forwarder $(LIB)

clean:
	rm $(OBJ) $(LIB_DIR)/liblsst_l1_forwarder.so
