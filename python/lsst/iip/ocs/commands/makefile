INC	 = -I$(ARCHIVE) -I$(ARCHIVE)/src -I$(CARCHIVE) -I$(CARCHIVE)/src -I$(PCLUSTER) -I$(PCLUSTER)/src\
-I/opt/sal/ts_sal/lsstsal/include\
-I$(SALPATH)/include/dcps/C++/SACPP\
-I$(SALPATH)/examples/include\
-I../include
SALPATH	 = /opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux
LIBSAL	 = /opt/sal/ts_sal/lsstsal/lib
CC	 = g++
LDFLAGS  = -L$(SALPATH)/lib -L$(LIBSAL) -L/usr/lib/python2.7/config -L../lib -Wl,-rpath,../lib
LDLIBS   = -lsacpp_archiver_types -lsacpp_catchuparchiver_types -lsacpp_processingcluster_types -l"dcpssacpp" -l"dcpsgapi" -l"ddsuser" \
-l"ddskernel" -l"ddsserialization" -l"ddsconfparser" -l"ddsconf" -l"ddsdatabase" \
-l"ddsutil" -l"ddsos" -ldl $(subst lib,-l,$(sort $(basename $(notdir $(wildcard /usr/lib/librt.so /lib/librt.so))))) \
-lSimpleAmqpClient -lyaml-cpp
ARCHIVE  = /opt/sal/ts_sal/test/archiver/cpp
CARCHIVE = /opt/sal/ts_sal/test/catchuparchiver/cpp
PCLUSTER = /opt/sal/ts_sal/test/processingcluster/cpp
CFLAGS   = -g -Wall 
TARGET   = sacpp_archiver_start_commander \
	   sacpp_archiver_stop_commander \
	   sacpp_archiver_enable_commander \
	   sacpp_archiver_disable_commander \
	   sacpp_archiver_standby_commander \
	   sacpp_archiver_enterControl_commander \
	   sacpp_archiver_exitControl_commander \
	   sacpp_archiver_abort_commander \
	   sacpp_catchuparchiver_start_commander \
	   sacpp_catchuparchiver_stop_commander \
	   sacpp_catchuparchiver_enable_commander \
	   sacpp_catchuparchiver_disable_commander \
	   sacpp_catchuparchiver_standby_commander \
	   sacpp_catchuparchiver_enterControl_commander \
	   sacpp_catchuparchiver_exitControl_commander \
	   sacpp_catchuparchiver_abort_commander \
	   sacpp_processingcluster_start_commander \
	   sacpp_processingcluster_stop_commander \
	   sacpp_processingcluster_enable_commander \
	   sacpp_processingcluster_disable_commander \
	   sacpp_processingcluster_standby_commander \
	   sacpp_processingcluster_enterControl_commander \
	   sacpp_processingcluster_exitControl_commander \
	   sacpp_processingcluster_abort_commander \
	   sacpp_archiver_SummaryState_log \
 	   sacpp_archiver_AppliedSettingsMatchStart_log \
	   sacpp_archiver_SettingVersions_log \
	   sacpp_archiver_ErrorCode_log \
	   sacpp_catchuparchiver_SummaryState_log \
 	   sacpp_catchuparchiver_AppliedSettingsMatchStart_log \
	   sacpp_catchuparchiver_SettingVersions_log \
	   sacpp_catchuparchiver_ErrorCode_log \
	   sacpp_processingcluster_SummaryState_log \
 	   sacpp_processingcluster_AppliedSettingsMatchStart_log \
	   sacpp_processingcluster_SettingVersions_log \
	   sacpp_processingcluster_ErrorCode_log

all: $(TARGET)

%: %.cpp
	$(CC) -std=c++11 $(INC) $(LDFLAGS) $(ARCHIVE)/src/.obj/CheckStatus.o $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o ../obj/SimplePublisher.o -o $@ $< $(LDLIBS) 

clean:
	rm sacpp_archiver_start_commander \
	   sacpp_archiver_stop_commander \
	   sacpp_archiver_enable_commander \
	   sacpp_archiver_disable_commander \
	   sacpp_archiver_standby_commander \
	   sacpp_archiver_enterControl_commander \
	   sacpp_archiver_exitControl_commander \
	   sacpp_archiver_abort_commander \
	   sacpp_catchuparchiver_start_commander \
	   sacpp_catchuparchiver_stop_commander \
	   sacpp_catchuparchiver_enable_commander \
	   sacpp_catchuparchiver_disable_commander \
	   sacpp_catchuparchiver_standby_commander \
	   sacpp_catchuparchiver_enterControl_commander \
	   sacpp_catchuparchiver_exitControl_commander \
	   sacpp_catchuparchiver_abort_commander \
	   sacpp_processingcluster_start_commander \
	   sacpp_processingcluster_stop_commander \
	   sacpp_processingcluster_enable_commander \
	   sacpp_processingcluster_disable_commander \
	   sacpp_processingcluster_standby_commander \
	   sacpp_processingcluster_enterControl_commander \
	   sacpp_processingcluster_exitControl_commander \
	   sacpp_processingcluster_abort_commander \
	   sacpp_archiver_SummaryState_log \
 	   sacpp_archiver_AppliedSettingsMatchStart_log \
	   sacpp_archiver_SettingVersions_log \
	   sacpp_archiver_ErrorCode_log \
	   sacpp_catchuparchiver_SummaryState_log \
 	   sacpp_catchuparchiver_AppliedSettingsMatchStart_log \
	   sacpp_catchuparchiver_SettingVersions_log \
	   sacpp_catchuparchiver_ErrorCode_log \
	   sacpp_processingcluster_SummaryState_log \
 	   sacpp_processingcluster_AppliedSettingsMatchStart_log \
	   sacpp_processingcluster_SettingVersions_log \
	   sacpp_processingcluster_ErrorCode_log
