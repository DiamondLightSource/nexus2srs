"""
Play with hdf files
"""

import h5py
import numpy as np

hdf = h5py.File('794932.nxs', 'r')

dataset_addresses = []

def get_dataset_addresses(name, obj):
    if isinstance(obj, h5py.Dataset):
        print(name, obj.shape, obj.size, obj.dtype)
        dataset_addresses.append(name)

hdf.visititems(get_dataset_addresses)

