"""
Test

"""

import os
from nexus2srs import nxs2dat

f = "example_files/782761.nxs"
# f = "example_files/794932.nxs"
# f = "example_files/815893.nxs"  # NXclassic_scan (eta)
# f = "example_files/879486.nxs"  # 2D scan

new = '%s_new.dat' % os.path.splitext(f)[0]
nxs2dat(f, new)

