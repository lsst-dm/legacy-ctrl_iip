ARCHIVE  	= /opt/sal/ts_sal/test/archiver/cpp
ATARCHIVE  	= /opt/sal/ts_sal/test/atArchiver/cpp
CARCHIVE 	= /opt/sal/ts_sal/test/catchuparchiver/cpp
PCLUSTER 	= /opt/sal/ts_sal/test/processingcluster/cpp
HEADER   	= /opt/sal/ts_sal/test/headerService/cpp
CAMERA   	= /opt/sal/ts_sal/test/camera/cpp
EFD      	= /opt/sal/ts_sal/test/efd/cpp
ATARCHIVE	= /opt/sal/ts_sal/test/atArchiver/cpp
ATCAMERA 	= /opt/sal/ts_sal/test/atcamera/cpp
SALINC	 	= -I$(ARCHIVE) -I$(ARCHIVE)/src\
	 	  -I$(ATARCHIVE) -I$(ATARCHIVE)/src\
		  -I$(CARCHIVE) -I$(CARCHIVE)/src\
		  -I$(PCLUSTER) -I$(PCLUSTER)/src\
		  -I$(CAMERA) -I$(CAMERA)/src\
		  -I$(EFD) -I$(EFD)/src\
		  -I$(ATCAMERA) -I$(ATCAMERA)/src\
		  -I$(ATARCHIVE) -I$(ATARCHIVE)/src\
		  -I/opt/sal/ts_sal/lsstsal/include\
		  -I$(SALPATH)/include/dcps/C++/SACPP\
		  -I$(SALPATH)/include/sys\
		  -I$(SALPATH)/include\
		  -I$(SALPATH)/examples/include
INCLUDE  	= -I../include -I/usr/local/include -I/usr/local/boost_1_66_0
SALPATH	 	= /opt/sal/ts_opensplice/OpenSpliceDDS/V6.4.1Community/HDE/x86_64.linux
LIBSAL	 	= /opt/sal/ts_sal/lsstsal/lib
CC	 	= g++
SAL_LDPATH  	= -L$(SALPATH)/lib -L$(LIBSAL) -L/usr/lib/python2.7/config 
#DM_LDPATH 	= -L../lib -Wl,-rpath,../lib-L/usr/local/lib -Wl,-rpath,/usr/local/lib -L/usr/local/lib64 -Wl,-rpath,/usr/local/lib64
DM_LDPATH 	= -L/usr/local/lib -Wl,-rpath,/usr/local/lib -L/usr/local/lib64 -Wl,-rpath,/usr/local/lib64 -L/usr/local/boost_1_66_0/stage/lib -Wl,-rpath,/usr/local/boost_1_66_0/stage/lib
SAL_LDLIB	= -lsacpp_archiver_types -lsacpp_catchuparchiver_types -lsacpp_processingcluster_types\
		  -lsacpp_camera_types -lsacpp_atcamera_types -lsacpp_efd_types -lsacpp_atArchiver_types\
		  -l"dcpssacpp" -l"dcpsgapi" -l"ddsuser" \
		  -l"ddskernel" -l"ddsserialization" -l"ddsconfparser" -l"ddsconf" -l"ddsdatabase" \
		  -l"ddsutil" -l"ddsos" -ldl $(subst lib,-l,$(sort $(basename $(notdir $(wildcard /usr/lib/librt.so /lib/librt.so)))))
DM_LDLIB        = -lpthread -lSimpleAmqpClient -lyaml-cpp
CFLAGS   	= -g -Wall -c 
COMPVERS 	= -std=c++11
OBJ_DIR         = ../obj
DM_OBJ          = ../obj/OCS_Bridge.o ../obj/SimplePublisher.o ../obj/Toolsmod.o ../obj/Consumer.o
OCS_OBJ         = $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o $(ARCHIVE)/src/.obj/CheckStatus.o
AT_OBJ          = $(ATARCHIVE)/src/.obj/SAL_atArchiver.o

TARGET   = sacpp_archiver_start_commander \
	   sacpp_archiver_stop_commander \
	   sacpp_archiver_enable_commander \
	   sacpp_archiver_disable_commander \
	   sacpp_archiver_standby_commander \
	   sacpp_archiver_enterControl_commander \
	   sacpp_archiver_exitControl_commander \
	   sacpp_archiver_abort_commander \
	   sacpp_archiver_SummaryState_log \
 	   sacpp_archiver_AppliedSettingsMatchStart_log \
	   sacpp_archiver_SettingVersions_log \
	   sacpp_archiver_ErrorCode_log \
	   sacpp_catchuparchiver_start_commander \
	   sacpp_catchuparchiver_stop_commander \
	   sacpp_catchuparchiver_enable_commander \
	   sacpp_catchuparchiver_disable_commander \
	   sacpp_catchuparchiver_standby_commander \
	   sacpp_catchuparchiver_enterControl_commander \
	   sacpp_catchuparchiver_exitControl_commander \
	   sacpp_catchuparchiver_abort_commander \
	   sacpp_catchuparchiver_SummaryState_log \
 	   sacpp_catchuparchiver_AppliedSettingsMatchStart_log \
	   sacpp_catchuparchiver_SettingVersions_log \
	   sacpp_catchuparchiver_ErrorCode_log \
	   sacpp_processingcluster_start_commander \
	   sacpp_processingcluster_stop_commander \
	   sacpp_processingcluster_enable_commander \
	   sacpp_processingcluster_disable_commander \
	   sacpp_processingcluster_standby_commander \
	   sacpp_processingcluster_enterControl_commander \
	   sacpp_processingcluster_exitControl_commander \
	   sacpp_processingcluster_abort_commander \
	   sacpp_processingcluster_SummaryState_log \
 	   sacpp_processingcluster_AppliedSettingsMatchStart_log \
	   sacpp_processingcluster_SettingVersions_log \
	   sacpp_processingcluster_ErrorCode_log \
	   sacpp_atArchiver_start_commander \
	   sacpp_atArchiver_stop_commander \
	   sacpp_atArchiver_enable_commander \
	   sacpp_atArchiver_disable_commander \
	   sacpp_atArchiver_standby_commander \
	   sacpp_atArchiver_enterControl_commander \
	   sacpp_atArchiver_exitControl_commander \
	   sacpp_atArchiver_abort_commander \
	   sacpp_atArchiver_SummaryState_log \
 	   sacpp_atArchiver_AppliedSettingsMatchStart_log \
	   sacpp_atArchiver_SettingVersions_log \
	   sacpp_atArchiver_ErrorCode_log
all: $(TARGET)

%: %.cpp
	$(CC) -std=c++11 $(INCLUDE) $(SALINC) $(SAL_LDPATH) $(DM_LDPATH) $(ARCHIVE)/src/.obj/CheckStatus.o $(ARCHIVE)/src/.obj/SAL_archiver.o $(CARCHIVE)/src/.obj/SAL_catchuparchiver.o $(PCLUSTER)/src/.obj/SAL_processingcluster.o $(AT_OBJ) ../obj/SimplePublisher.o -o $@ $< $(SAL_LDLIB) $(DM_LDLIB)

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
	   sacpp_processingcluster_ErrorCode_log \
	   sacpp_atArchiver_start_commander \
	   sacpp_atArchiver_stop_commander \
	   sacpp_atArchiver_enable_commander \
	   sacpp_atArchiver_disable_commander \
	   sacpp_atArchiver_standby_commander \
	   sacpp_atArchiver_enterControl_commander \
	   sacpp_atArchiver_exitControl_commander \
	   sacpp_atArchiver_abort_commander \
	   sacpp_atArchiver_SummaryState_log \
 	   sacpp_atArchiver_AppliedSettingsMatchStart_log \
	   sacpp_atArchiver_SettingVersions_log \
	   sacpp_atArchiver_ErrorCode_log
