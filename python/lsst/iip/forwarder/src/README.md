# Forwarder

## Installation Caveat
Forwarder depends on `cfitsio` library. Under the `cfitsio`, fwdr uses `fpack` 
utility program to compress fitsfile. To compile, cfitsio with fpack, 

./configure --prefix=<path>
make cfitsio 
make fpack
make funpack
make install 

This will create a `bin` directory under cfitsio prefix path. Forwarder uses the
fpack executable to compress fitsfile. 

Then, we need to add `prefix` to the $PATH variable. 
