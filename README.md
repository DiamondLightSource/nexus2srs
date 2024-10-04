# nexus2srs
Program to convert NeXus (.nxs) scan Files to the classic ASCII SRS .dat files.


By Dan Porter, *Diamond Light Source Ltd.* 2023-2024


### Usage
From Terminal:
```
$ python -m nexus2srs '12345.nxs' '12345.dat' -tiff
```

In Python script:
```Python
from nexus2srs import nxs2dat

nxs2dat('12345.nxs', '/spool', write_tiff=False)
```

### Requirements
**python 3.10+**,
*hdfmap*, *h5py*, *numpy*, plus *pillow* for writing TIFF images

### Installation
From PyPI:
```
$ python -m pip install nexus2srs
```

### Methodology
The file conversion follows the following protocol:
1. Open .nxs HDF file (using h5py) and create list of all datasets and groups using hdfmap
2. Generate the top part of the header, either by looking for the **'scan_header'** dataset or by populating with date, time and run number.
3. Generate the list of metadata items in the header by selecting datasets with *size <= 1*, as available:
   1. Search for datasets with attribute **@local_name**, the name saved will be the last part of this name.
   2. If no **@local_name** datasets are found, take dataset names of all *size <= 1* datasets in the file. Each dataset is saved as 'name' and 'group_name'.
4. Build table of scanned data points by selecting datasets of equal shape with *size >= 1*, as available:
   1. Get names of fields from the dataset called **'scan_fields'**, find these datasets in the first **NXdata** group or group called **'measurement'**
   2. Or, take all datasets in the default or first **NXdata** or group called **'measurement'**, with the same shape as the first dataset in this group
   3. Or, take all datasets in the file with shape equal to with the most common dataset shape in the file
5. Search for dataset **'image_data'**, generate a template from the first contained TIFF image path and add to metadata
6. Find 3D+ arrays in all **NXdetector** groups, generate and add TIFF image paths to metadata 


For metadata and the table of scanned data, if the datasets contain the **@decimals** attribute, they will be rounded accordingly. 


Once the conversion is complete, the components are joined into a single string including the header, metadata and 
table of scanned data. By default, a NeXus file at *'folder/file.nxs' will be saved as *'folder/file.dat'*. 
If TIFF writing is enabled, detector image data from 3+D arrays in all **NXdetector** groups will be saved as TIFF 
images into a sub-folder like *'folder/****RunNo***_***DetectorName****_files/00001.tif'*. Files will not be overwritten if 
they already exist.

### Testing (Jan 2023)

 - Testing has been performed on several thousand old I16, I10 and I21 nexus files.
 - No unexpected failures were found in these, however none of the files conform to the new, ideal nexus structure.
 - Local files are converted in ~0.3s per file without image conversion.
 - See Jupyter notebook [nexus2srs_tests.ipynb](https://github.com/DiamondLightSource/nexus2srs/blob/master/examples/nexus2srs_tests.ipynb) for more information.
 - Tested with nxs2dat jupyter processor on I16 15/12/2023, updated TIFF file writing.

### Update September 2024

Significant re-factoring of code to include the [hdfmap](https://github.com/DiamondLightSource/hdfmap) package.
The HdfMap function takes care of creating the scannables table and the metadata, using current NeXus best practice.
This allows for correct identification of metadata and uses "local_names" and "decimals" attributes.

