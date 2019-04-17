INSTALL_DIR		= /opt/lsst/dm-prompt

all: core ocsbuild

core:
	$(MAKE) -C src/core

ocsbuild:
	$(MAKE) -C src/ocs

clean:
	rm -rf $(INSTALL_DIR)
