# nexus2srs
Lightweight function to convert Nexus (.nxs) scan Files to the classic ascii SRS .dat files.


By Dan Porter, *Diamond Light Source Ltd.* 2023


### Usage
From Terminal:
```
$ python -m nexus2srs '12345.nxs' '12345.dat'
```

In Python script:
```Python
from nexus2srs import nxs2dat

nxs2dat('12345.nxs')
```

### Requirements
*h5py*, *numpy*, plus *pillow* for writing TIF images


### Methodology
The file conversion follows the following protocol:
0. Open .nxs HDF file (using h5py) and create list of all datasets and groups
1. Search all datasets for one called **"scan_fields"**
   1. Use names from **"scan_fields"** to populate scandata, matching dataset names or dataset.attr[**'gda_field_name'**]
2. If *"scan_fields"* not available, look for **"measurement"** group and add arrays to scandata
3. If *"measurement"* not available, determine scan shape from most common dataset shapes with *size > 1*
   1. Add all unique datasets with shape matching scan_shape to scandata
4. Add all datasets with *size = 1* to metadata
5. search for datasets **'scan_command'**, **'start_time'**, **'scan_header'** to complete the file header
6. search for dataset **'image_data'** and add metadata field *'%s_path_template'* where %s is the detector name
7. search for **NXdetector/data** dataset, if required write TIF images from area detector data

Searching the HDF file for names is done only once, building a list of HDF addresses and datasets that is 
easy and fast to search.  

### Current Issues / ToDo

 - Loss of order information in scan data for generic style
 - Missing scancn commands (loss of original scan command)
 - Many metadata values different in comarisons, possibly saved at different point?

### Testing

 - Testing has beenb performed on several thousand old I16, I10 and I21 nexus files.
 - No unexpected failures were found in these, however none of the files conform to the new, ideal nexus structure.
 - Local files are converted in ~0.3s per file without image conversion.
 - See Jupyter notebook [nexus2srs_tests.ipynb](https://github.com/DanPorter/nexus2srs/blob/master/nexus2srs_tests.ipynb) for more information.
 - Tested with nxs2dat jupyter processor on I16 15/12/2023, updated TIF file writing.

