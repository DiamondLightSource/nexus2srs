# nexus2srs
Lightweight function to convert Nexus (.nxs) scan Files to the classic SRS .dat files.

### Usage
From Terminal:
```
$ python -m nexus2srs '12345.nxs'
```

In Python script:
```Python
from nexus2srs import nxs2dat

nxs2dat('12345.nxs')
```

### Requirements
*numpy* and *h5py*


### Current Issues / ToDo

 - Should metadata strings have quotes?
 - Are blank strings in metadata ok?
 - Strings in scandata
 - Generate Old style detector path spec
 - Generate header with time/date
 - Missing 'cmd' in metadata?
 - How to handle multi-dimensional scans? 
 - Loss of order information in scan data
 - Add Scan data shortcut for NXclassic_scan 
 - write dat file