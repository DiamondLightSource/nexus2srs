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
1. Search all datasets for one called "scan_fields"
   1. Use names from "scan_fields" to populate scandata, matching dataset names or dataset.attr['gda_field_name']
2. If "scan_fields" not available, look for "measurement" group and add arrays to scandata
3. If "measurement" not available, determine scan shape from most common dataset shapes with size > 1
   1. Add all unique datasets with shape matching scan_shape to scandata
4. Add all datasets with size=1 to metadata
5. search for datasets 'scan_command', 'start_time', 'scan_header' to complete the file header
6. search for dataset 'image_data' and add metadata field '%s_path_template' where %s is the detector name
7. search for NXdetector/data dataset, if required write TIF images from area detector data


### Current Issues / ToDo

 - Loss of order information in scan data for generic style
 - Missing scancn commands (loss of original scan command)

