"""
Compare old vs converted ASCII dat files
Uses Py16 package
"""

import sys, os
import numpy as np
from nexus2srs import nxs2dat

pth = os.path.expanduser('~/OneDrive - Diamond Light Source Ltd/PythonProjects')
sys.path.insert(0, pth + '/Py16')
from Py16progs import read_dat_file


nexus_file = 'example_files/794932.nxs'
old_dat = '%s.dat' % os.path.splitext(nexus_file)[0]
converted_file = '%s_new.dat' % os.path.splitext(nexus_file)[0]

dold = read_dat_file(old_dat)
nxs2dat(nexus_file, converted_file)
dnew = read_dat_file(converted_file)

mold = dold.metadata
mnew = dnew.metadata

print('\n--- Compare %s files ---' % nexus_file)
print('Scan Items the same: %s' % (dold.keys() == dnew.keys()))
print('Scan Order the same: %s' % (list(dold.keys()) == list(dnew.keys())))

scan_length_old = len(next(iter(dold.values())))
scan_length_new = len(next(iter(dnew.values())))
print('Scan length the same: (%d, %d) %s' % (scan_length_old, scan_length_new, scan_length_old == scan_length_new))

print('Meta Items the same: (%d, %d) %s' % (len(mold), len(mnew), mold.keys() == mnew.keys()))
print('\nMeta Items in Old File:')
print('\t '.join(['%12s'] * 3) % ('Name', 'Old', 'New'))
for name in mold:
    newval = mnew[name] if name in mnew else '***None***'
    print('\t '.join(['%12s'] * 3) % (name, mold[name], newval))

print('\nNew Meta Items in New File:')
print('Name        Value')
for name in mnew:
    if name in mold:
        continue
    print('%12s %12s' % (name, mnew[name]))


