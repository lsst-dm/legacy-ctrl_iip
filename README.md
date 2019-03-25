# ctrl_iip
Image ingest and processing

environment variables:

Set CTRL_IIP_DIR to the root of this repository. (this will be set automatically
when this is integrated with the DM system)

Set PYTHONPATH to include $CTRL_IPP_DIR/python



Note about configuration files:

Configuration files are loaded from $CTRL_IIP_DIR/etc/config by default

If the environment variable IIP_CONFIG_DIR is set, it will look in 
this directory for configuration files.
