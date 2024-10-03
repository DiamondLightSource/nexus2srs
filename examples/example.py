"""
Test nexus2srs
"""

from itertools import chain
from hdfmap import list_files
from nexus2srs import run_nexus2srs, set_logging_level


set_logging_level('info')

# f = "example_files/782761.nxs"
# f = "example_files/794932.nxs"
# f = "example_files/815893.nxs"  # NXclassic_scan (eta)
f = "example_files/879486.nxs"  # 2D scan
# f = "example_files/i10-759799.nxs"

# new = '%s_hdfmap.dat' % os.path.splitext(f)[0]
# run_nexus2srs(f, new)

# Multiple files
files = list_files('example_files', '.nxs')
dat_files = (f"{f[:-4]}_hdfmap.dat" for f in files)
run_nexus2srs(*chain(*zip(files, dat_files)))

