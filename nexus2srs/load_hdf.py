"""
Python module with functions to load HDF files and write classic SRS .dat files
"""

import os
import h5py
from numpy import squeeze


def address_name(address):
    """Convert hdf address to name"""
    return os.path.basename(address)


def nxs2dat(filename):
    """Load HDF file"""

    with h5py.File(filename, 'r') as hdf:

        all_addresses = []
        all_datasets = []

        def func(address, obj):
            if isinstance(obj, h5py.Dataset):
                # print(name, obj.ndim, obj.size)
                all_addresses.append(address)
                all_datasets.append(obj)

        hdf.visititems(func)
        n_datasets = len(all_datasets)

        # --- Find Scan Data ---
        # Find datasets with ndim=1 arrays of fixed length
        scan_lengths = [ds.size for ds in all_datasets if ds.ndim == 1 and ds.size > 1]
        print('Scan length max: %d' % max(scan_lengths))
        print('Scan length min: %d' % min(scan_lengths))
        scan_length = max(scan_lengths)
        # use max scan_lenghts

        # --- Find metadata ---
        # Find datasets with single value
        meta_ids = []
        scan_ids = []
        metadata = {}
        scandata = {}
        for n in range(n_datasets):
            if all_datasets[n].id not in meta_ids and all_datasets[n].size == 1:
                meta_ids.append(all_datasets[n].id)
                metadata[address_name(all_addresses[n])] = squeeze(all_datasets[n])
            elif all_datasets[n].id not in scan_ids and all_datasets[n].ndim ==1 and all_datasets[n].size == scan_length:
                scan_ids.append(all_datasets[n].id)
                try:
                    # Only add floats/ ints
                    scandata[address_name(all_addresses[n])] = squeeze(all_datasets[n]) * 1.0
                except TypeError:
                    pass

        # Print metadata
        print('Nexus File: %s' % filename)
        print('--- Metadata ---')
        for name, value in metadata.items():
            print('%s=%s' % (name, value))

        print('\n\n--- Scandata ---')
        print(', '.join(['%10s' % name for name in scandata]))
        for n in range(scan_length):
            print(', '.join(['%10s' % scandata[name][n] for name in scandata]))

        print('\n TheEnd')




