ifeq ($(LSST_SDK_INSTALL), /opt/lsst)
SAL_INCLUDE	= -I$(LSST_SDK_INSTALL)/ts_sal/include
SAL_LDPATH	= -L$(LSST_SDK_INSTALL)/ts_sal/lib
else
SAL_INCLUDE 	= -I$(LSST_SDK_INSTALL)/ts_sal/test/include \
		  -I$(LSST_SDK_INSTALL)/ts_sal/lsstsal/include
SAL_LDPATH	= -L$(LSST_SDK_INSTALL)/ts_sal/test/lib
endif
DEVICES		= MTArchiver ATArchiver \
		  CatchupArchiver PromptProcessing MTCamera ATCamera EFD
SAL_LIB		= $(patsubst %,-lsacpp_%_types, $(DEVICES)) \
		  $(patsubst %,-lSAL_%, $(DEVICES)) \
		  -ldcpssacpp -lddskernel
INCLUDE     	= -I$(L1_LIB_PATH)/include \
		  -I../../include/core \
	    	  -I../../include/ocs \
		  -I$(OSPL_HOME)/include/dcps/C++/SACPP \
		  -I$(OSPL_HOME)/include/sys \
		  $(SAL_INCLUDE)
LDPATH      	= -L$(L1_LIB_PATH)/lib \
		  -L$(L1_LIB_PATH)/lib64 \
		  -L$(OSPL_HOME)/lib \
		  $(SAL_LDPATH)
L1_LIB         	= -lpthread -lyaml-cpp -lSimpleAmqpClient \
                  -lboost_log -lboost_system -lboost_thread
L1_OBJ         	= ../obj/IIPBase.o ../obj/SimpleLogger.o ../obj/SimplePublisher.o ../obj/Toolsmod.o ../obj/Consumer.o
OBJ_DIR        	= ../obj
BIN_DIR	       	= ../../bin
EXE		= CommandListener EventSubscriber AckSubscriber
BIN_EXE		= $(patsubst %,$(BIN_DIR)/%,$(EXE))
RUN_EXE		= $(patsubst %,$(BIN_DIR)/run_%.sh,$(EXE))

all: $(EXE)

.PHONY: all dependency

dependency:
	$(MAKE) -C ../core all

%: %.cpp dependency
	g++ -std=c++11 -DBOOST_LOG_DYN_LINK $(INCLUDE) $(LDPATH) $(L1_OBJ) -o $(BIN_DIR)/$@ $< $(SAL_LIB) $(L1_LIB)

install:
	install -d $(L1_INSTALL_PATH)/bin
	install -m 755 -D $(BIN_DIR)/setup.env $(L1_INSTALL_PATH)/bin
	install -m 755 -D $(BIN_EXE) $(RUN_EXE) $(L1_INSTALL_PATH)/bin

clean: 
	rm $(BIN_EXE)
