BUILD_DIR		= bin
INSTALL_DIR		= /opt/lsst/dm-prompt

all: ocsbuild

ocsbuild:
	cd src/ocs && $(MAKE)

install:
	cd ocs/src && $(MAKE) install
	install -d $(INSTALL_DIR)/bin $(INSTALL_DIR)/python $(INSTALL_DIR)/python/logs $(INSTALL_DIR)/config
	install -m 755 -D *.py $(INSTALL_DIR)/python
	install -m 755 -D CommandListener $(INSTALL_DIR)/bin
	install -m 755 -D EventSubscriber $(INSTALL_DIR)/bin
	install -m 755 -D AckSubscriber $(INSTALL_DIR)/bin
	install -m 755 -D check_services.sh $(INSTALL_DIR)/bin
	install -m 755 -D at_rmq_purge_queues.sh $(INSTALL_DIR)/bin
	install -m 755 -D L1SystemCfg.yaml $(INSTALL_DIR)/config
	install -D etc/services/l1d-*  /etc/systemd/system

clean:
	rm -rf $(INSTALL_DIR)
