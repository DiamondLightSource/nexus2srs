"""
Test

"""

import os, time
from nexus2srs import nxs2dat
# from nexus2srs.nexus2srs import nxs2dat, nxs2dat2

f = "example_files/782761.nxs"
# f = "example_files/794932.nxs"
f = "example_files/815893.nxs"  # NXclassic_scan (eta)
# f = "example_files/879486.nxs"  # 2D scan
f = "example_files/i10-759799.nxs"

new = '%s_new.dat' % os.path.splitext(f)[0]
nxs2dat(f, new)

stop
# f = r"C:\Users\grp66007/OneDrive - Diamond Light Source Ltd/I16/Nexus_Format/example_nexus\705061.nxs"
f = r"C:\Users\grp66007/OneDrive - Diamond Light Source Ltd/I16/Nexus_Format/example_nexus\879486.nxs"
# f = r"C:\Users\grp66007/OneDrive - Diamond Light Source Ltd/I16/Nexus_Format/I21_example/examples/Proposal_ID\i21-157111.nxs"
# f = r"C:\Users\grp66007\OneDrive - Diamond Light Source Ltd\I16\Nexus_Format\exampledata-master\DLS\i16\hdf5\538039.nxs"
# f = r"\\data.diamond.ac.uk\i16\data\2023\cm33911-1\970792.nxs"
# f = r"\\data.diamond.ac.uk\i16\data\2018\mt18964-1\705097.nxs"
# f = r"\\data.diamond.ac.uk\i16\data\2018\mt18964-1\705094.nxs"
# f = r"\\data.diamond.ac.uk\i16\data\2022\cm31138-9\937171.nxs"
# f = r"C:\Users\grp66007/OneDrive - Diamond Light Source Ltd/I16/Nexus_Format/example_nexus\782761.nxs"
# f = r"C:\Users\grp66007\OneDrive - Diamond Light Source Ltd\I16\Nexus_Format\I10_nexus\example_I10_Nexus_Files\i10-608314.nxs"  # I10 scan
f = r"C:\Users\grp66007\OneDrive - Diamond Light Source Ltd\Projects\LiCoO2\I13 Experiment 2023\example_Data\i13-1-368910.nxs"  # I13-1 scan
nxs2dat(f, 'test.dat', False)

tests = [
    "example_files/782761.nxs",
    "example_files/794932.nxs",
    "example_files/815893.nxs",  # NXclassic_scan (eta)
    "example_files/879486.nxs",  # 2D scan
    r"C:\Users\grp66007/OneDrive - Diamond Light Source Ltd/I16/Nexus_Format/example_nexus\705061.nxs",
    r"C:\Users\grp66007/OneDrive - Diamond Light Source Ltd/I16/Nexus_Format/example_nexus\879486.nxs",
    r"C:\Users\grp66007/OneDrive - Diamond Light Source Ltd/I16/Nexus_Format/I21_example/examples/Proposal_ID\i21-157111.nxs",
    r"C:\Users\grp66007\OneDrive - Diamond Light Source Ltd\I16\Nexus_Format\exampledata-master\DLS\i16\hdf5\538039.nxs",
    r"\\data.diamond.ac.uk\i16\data\2023\cm33911-1\970792.nxs",
    r"\\data.diamond.ac.uk\i16\data\2018\mt18964-1\705097.nxs",
    r"\\data.diamond.ac.uk\i16\data\2018\mt18964-1\705094.nxs",
    r"\\data.diamond.ac.uk\i16\data\2022\cm31138-9\937171.nxs",
    r"C:\Users\grp66007/OneDrive - Diamond Light Source Ltd/I16/Nexus_Format/example_nexus\782761.nxs",
]
# t0 = time.time()
# for f in tests:
#     nxs2dat(f, 'test.dat')
# t1 = time.time()
# dif = t1 - t0
# print('Tests took: %.2f s for %d files, %.3s per file' % (dif, len(tests), dif/len(tests)))



