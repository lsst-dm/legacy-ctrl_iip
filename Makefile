INSTALL_DIR		= /opt/lsst/dm-prompt

all: ocsbuild

ocsbuild:
	 $(MAKE) -C src/ocs

clean:
	rm -rf $(INSTALL_DIR)
