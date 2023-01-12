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


### Current Issues / ToDo

 - Creation of TIF images from HDF
 - Loss of order information in scan data
 - Missing scancn commands (loss of original scan command)
 - Missing metadta - kgam, kdelta, kap, kth, kmu