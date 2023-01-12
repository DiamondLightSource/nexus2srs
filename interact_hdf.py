"""
Play with hdf files
"""

import h5py
import numpy as np
from nexus2srs.load_hdf import get_all_datasets

# hdf = h5py.File('794932.nxs', 'r')
hdf = h5py.File('879486.nxs', 'r')  # 2D scan


all_addresses, all_datasets = get_all_datasets(hdf)
