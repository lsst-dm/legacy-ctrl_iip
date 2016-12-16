import pyfits
import numpy as np 
import yaml 

f = open("ForwarderCfg.yaml")
cdm = yaml.load(f)
name = cdm["NAME"]

# name to self._name
def format(meta, params, path):
    data_array = np.fromfile(path, dtype=np.int32)
    
    not_write = ["BITPIX", "NAXIS", "NAXIS1", "NAXIS2"]

    header = meta.copy()
    header.update(params)

    hdu = pyfits.PrimaryHDU(data_array)
    hdu_header = hdu.header
    for key, value in header.iteritems(): 
        if key not in not_write: 
            hdu_header[key] = value 
    fitsname = "RAWCCD-" + str(header["CCDN"]) + "." + str(header["IMAGE_ID"]) \
               + "." + str(header["VISIT_ID"]) + ".fits" 
    hdu.writeto("/home/" + name + "/xfer_dir/" + fitsname)

def main(): 
    # assuming fetch file is successful 
    # read ccd.header file from /home/F1/xfer_dir
    header_file = open("/home/F1/xfer_dir/ccd.header", "r")
    header_dict = {}
    for line in header_file: 
	if (len(line.split("/")) == 2): 
	    kvpair, comment = line.split("/")
	    key, value = kvpair.split("=")
	    header_dict[key.strip()] = value
    
    # set up ccd specific params
    params = {} 
    params["CCDN"] = 1 
    params["VISIT_ID"] = 1 
    params["IMAGE_ID"] = 1
    
    format(header_dict, params, "/home/" + name + "/xfer_dir/RAWFILE-1.fits")
        
    
if __name__ == "__main__": main() 
