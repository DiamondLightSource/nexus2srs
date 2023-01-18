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
*numpy* and *h5py*


### Methodology
Follows the following protocol:
1. Search for NXclassic_scan with dataset 'entry1/scan/scan_fields', defining names of scan arrays,
   scan arrays in 'entry1/scan/measurement', metadata in 'entry1/scan/positioners'
2. Search for NXclassic_scan with dataset 'entry1/scan/scan_fields',
   Names from scan_fields are searched in dataset addresses and dataset 'gda_field_name' attributes,
   metadata in 'entry1/scan/positioners'
3. Search for I16historic_scan: scan arrays in 'entry1/measurement', metadata in 'entry1/before_scan'
4. Generic search:
    scan data are 1D or 2D datasets (size>1) with shapes matching the most common dataset shape,
    metadata are size 1 datasets

### Alternative Methodology
Follows the following protocol:
1. Search all datasets for one called "scan_fields"
    1. Use names from "scan_fields" to populate scandata
    2. search datasets for matching name or matching dataset.attr['gda_field_name']
2. If "scan_fields" not available, determine scan shape from most common dataset shapes with size > 1
   1. Add all unique datasets with shape matching scan_shape to scandata
3. Add all datasets with size=1 to metadata
4. search for datasets 'scan_command', 'start_time', 'scan_header' to complete the file header
5. search for dataset 'image_address' and add metadata field %s_path_template where %s is the detector name


### Current Issues / ToDo

 - Creation of TIF images from HDF
 - Hard-coded HDF addresses - entry1/scan, entry1/measurement etc.
 - Loss of order information in scan data for generic style
 - Missing scancn commands (loss of original scan command)
 - Missing metadta - kgam, kdelta, kap, kth, kmu