"""
Play with hdf files
"""

import h5py
import numpy as np
from PIL import Image
from nexus2srs.nexus2srs_old import get_all_datasets, find_dataset
import time

# hdf = h5py.File('794932.nxs', 'r')
# hdf = h5py.File('example_files/879486.nxs', 'r')  # 2D scan
#hdf = h5py.File("example_files/815893.nxs", 'r')  # NXclassic_scan
#hdf = h5py.File(r"\\data.diamond.ac.uk\i16\data\2022\cm31138-1\914860.nxs")
hdf = h5py.File(r"C:\Users\grp66007\OneDrive - Diamond Light Source Ltd\I16\Nexus_Format\I10_nexus\example_I10_Nexus_Files\i10-608314.nxs")  # I10 scan

address_datasets = get_all_datasets(hdf)

array_addresses = [adr for adr, ds in address_datasets if ds.ndim > 1]
t0 = time.time()
for n in range(1000):
    sfa = [adr for adr, ds in address_datasets if adr.endswith('/scan_fields')]
t1 = time.time()
print('address search: %s' % (t1 - t0))

t0 = time.time()
for n in range(1000):
    sfa = find_dataset(hdf, 'scan_fields')
t1 = time.time()
print('find_dataset search: %s' % (t1 - t0))  # MUCH slower!
