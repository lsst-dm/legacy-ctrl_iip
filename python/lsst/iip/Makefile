DM_BUILDDIR		= /opt/lsst/dm-prompt

all: ocsbuild

ocsbuild:
	cd ocs/src && $(MAKE)

install:
	cd ocs/src && $(MAKE) install
	install -d $(DM_BUILDDIR)/bin $(DM_BUILDDIR)/include $(DM_BUILDDIR)/bin/logs
	install -m 755 -D *.py $(DM_BUILDDIR)/bin
	install -m 755 -D L1SystemCfg.yaml $(DM_BUILDDIR)/bin

clean:
	echo "nothing"
