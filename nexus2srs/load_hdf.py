"""
Python module with functions to load HDF files and write classic SRS .dat files

Usage (Python)
>> from load_hdf import nxs2dat
>> nxs2dat('12345.nxs', '12345.dat')

Usage (from terminal - converts scan files from NeXus to ASCII format):
$ python load_hdf 12345.nxs 12345.dat

By Dan Porter, PhD
Diamond Light Source Ltd.
2022
"""

import os
import datetime
import h5py
from numpy import squeeze, argmax, prod, reshape

__version__ = "0.2.0"
__date__ = "2023/01/12"

# --- Default HDF Addresses ---
# NeXus Classic Scan
NXENTRY = '/entry1'
NXSCAN = NXENTRY + '/scan'
NXSCANFIELDS = NXSCAN + '/scan_fields'
NXSCANHEADER = NXSCAN + '/scan_header'
NXMEASUREMENT = NXSCAN + '/measurement'
NXMETA = NXSCAN + '/positioners'

# I16 backwards compatibility
I16ENTRY = '/entry1'
I16MEASUREMENT = I16ENTRY + '/measurement'
I16META = I16ENTRY + '/before_scan'

# Header Data
SRSRUN = '/entry1/entry_identifier'
SRSDAT = '/entry1/start_time'
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
HEADER = """ &SRS
 SRSRUN=%s,SRSDAT=%s,SRSTIM=%s,
 SRSSTN='BASE',SRSPRJ='GDA_BASE',SRSEXP='Emulator',
 SRSTLE='                                                            ',
 SRSCN1='        ',SRSCN2='        ',SRSCN3='        ',"""  # % (srsrun, srsdat, srstim)

# Meta Fields - metadata fields that may not exist and need to be looked for
META_CMD = 'entry1/scan_command'
META_DATE = 'entry1/start_time'


def address_name(address):
    """Convert hdf address to name"""
    return os.path.basename(address)


def get_all_datasets(hdf):
    """Return a list of all HDF datasets and dataset addresses"""
    datasets = []

    def func(address, obj):
        if isinstance(obj, h5py.Dataset):
            datasets.append((address, obj))
    hdf.visititems(func)
    return datasets


def find_dataset(hdf, name):
    """Find address with matching name in HDF file (returns first found exact match)"""

    def func(address):
        if address.endswith('/%s' % name):
            return address
    return hdf.visit(func)


def dataset2metadata(dataset):
    """Convert hdf dataset to either float or string"""
    try:
        # numpy.squeeze converts any len(1) arrays to floats
        return float(squeeze(dataset))
    except ValueError:
        return "'%s'" % dataset[()]


def dataset2scandata(dataset):
    """Convert hdf dataset to 1D array"""
    return reshape(dataset, -1)


def generate_header(hdf):
    """Generate SRS Header string from hdf"""
    # 1. Check NXclassic_scan header
    if NXSCANHEADER in hdf:
        return '\n'.join(h for h in hdf[NXSCANHEADER])
    # Get Scan number
    if SRSRUN in hdf:
        srsrun = '%s' % hdf[SRSRUN][()]
    else:
        srsrun = os.path.splitext(os.path.basename(hdf.filename))[0]
    # Get Date + Time
    try:
        date = datetime.datetime.strptime(hdf[SRSDAT][()], DATE_FORMAT)
    except (KeyError, ValueError):
        date = datetime.datetime.fromtimestamp(os.path.getctime(hdf.filename))
    srsdat = date.strftime('%Y%m%d')
    srstim = date.strftime('%H%M%S')
    return HEADER % (srsrun, srsdat, srstim)


def required_metadata(hdf):
    """Generate required metadata fields from hdf"""
    meta = {}
    # Scan command
    if META_CMD in hdf:
        meta['cmd'] = hdf[META_CMD][()]
    else:
        meta['cmd'] = ''
    # Scan date
    try:
        date = datetime.datetime.strptime(hdf[META_DATE][()], DATE_FORMAT)
    except (KeyError, ValueError):
        date = datetime.datetime.fromtimestamp(os.path.getctime(hdf.filename))
    meta['date'] = date.strftime('%a %b %d %H:%M:%S %Y')
    # Image data path
    # Look for 'image_data' dataset - the address is not fixed as the detector name is unknown,
    # so we much search the file for it, which may be slow.
    image_data = find_dataset(hdf, 'image_data')  # returns None if image_data doesn't exist
    if image_data:
        # Get image path, e.g. '815893-pilatus3_100k-files
        image_path, _ = os.path.split(hdf[image_data][0])
        # Get detector name from path
        try:
            detector_name = image_path.split('-')[1]
        except IndexError:
            detector_name = 'image'
        meta[detector_name + '_path_template'] = image_path + '/%05d.tif'
    return meta


def get_scan_meta_data(hdf):
    """
    Create dicts of metadata and scan data from hdf file
    :param hdf: HDF Group object
    :return scandata: {name: array} dict of scanned data, all fields have n length arrays
    :return metadata: {name: value} dict of metadata, all fields are float/int/str
    """

    # 1. --- NXclassic_scan ---
    # Scan fields defined in entry1/scan/scan_fields, metadata in entry1/scan/positioners
    if NXSCANFIELDS in hdf:
        print('NXclassic_scan')
        scandata = {
            name: dataset2scandata(hdf[NXMEASUREMENT + '/%s' % name])
            for name in hdf[NXSCANFIELDS][()]
        }
        metadata = {
            address_name(adr): dataset2metadata(ds)
            for adr, ds in get_all_datasets(hdf[NXMETA]) if ds.size == 1
        }

    # 2. --- I16 historic scan ---
    # Scan data in /entry1/measurement, metadata in /entry1/before_scan
    elif I16META in hdf:
        print('I16 Historic scan')
        scandata = {
            name: dataset2scandata(ds)
            for name, ds in get_all_datasets(hdf[I16MEASUREMENT])
        }
        metadata = {
            address_name(adr): dataset2metadata(ds)
            for adr, ds in get_all_datasets(hdf[I16META]) if ds.size == 1
        }

    # 3. --- Load All Datasets ---
    # Generate a list of all datasets in file using hdf.visititems
    # Note that loading a dataset is just a link, not loading the actual data yet
    else:
        print('Generic scan, search whole file, determine scan shape')
        address_datasets = get_all_datasets(hdf)

        # --- Find Scan Length ---
        # Find datasets with ndim 1 or 2 and size > 1
        scan_shapes = [ds.shape for _, ds in address_datasets if (ds.ndim == 1 or ds.ndim == 2) and ds.size > 1]
        # use find the array with most points (might be a better way, look for the most common maybe?)
        # This works pretty well for 1/2 dimensional scans, but won't work for any higher dimension (if possible...)
        scan_shape = scan_shapes[argmax([prod(s) for s in scan_shapes])]
        print('Scan shape: %s' % scan_shape)

        # --- Load Data ---
        # Loop through each dataset, comparing ids to not replicate data
        #  if dataset is size==1, add to metadata
        #  if dataset is shape==scan_shape array, add to scandata
        ids = []
        metadata = {}
        scandata = {}
        for address, dataset in address_datasets:
            if dataset.id in ids:
                continue
            ids.append(dataset.id)
            name = address_name(address)

            # --- Metadata ---
            if dataset.size == 1:
                metadata[name] = dataset2metadata(dataset)

                # This is a horrid hack for cmd
                if name == 'scan_command' and 'cmd' not in metadata:
                    metadata['cmd'] = "'%s'" % dataset[()]

            # ---Scandata ---
            elif dataset.shape == scan_shape:
                try:
                    # Only add floats, reshape to 1D array
                    scandata[name] = reshape(dataset, -1) * 1.0
                except TypeError:
                    pass

    # --- Check Required metadat ---
    req_meta = required_metadata(hdf)
    req_meta.update(**metadata)
    return scandata, req_meta


"----------------------------------------------------------------------------"
"----------------------------- nxs2dat --------------------------------------"
"----------------------------------------------------------------------------"


def nxs2dat(nexus_file, dat_file=None):
    """
    Load HDF file and convert to classic SRS .dat file
    :param nexus_file: str filename of HDF/Nexus file
    :param dat_file: str filename of ASCII file to create (None renames nexus file as *.dat)
    :return: None
    """
    if dat_file is None:
        dat_file = os.path.splitext(nexus_file)[0] + '.dat'

    with h5py.File(nexus_file, 'r') as hdf:
        scandata, metadata = get_scan_meta_data(hdf)
        header = generate_header(hdf)

    # --- Scan length ---
    scan_length = len(next(iter(scandata.values())))
    print('Nexus File: %s' % nexus_file)
    print('Scan length: %s' % scan_length)

    # --- Metadata ---
    meta = '\n'.join(['%s=%s' % (name, value) for name, value in metadata.items()])
    # --- Scandata ---
    scanhead = '\t'.join(['%10s' % name for name in scandata])
    scan = '\n'.join(['\t'.join(['%10s' % scandata[name][n] for name in scandata]) for n in range(scan_length)])
    # --- Combine ---
    out = '\n'.join([
        header,
        '<MetaDataAtStart>',
        meta,
        '</MetaDataAtStart>',
        ' &END',
        scanhead,
        scan,
        ''  # blank line at end of file
    ])
    # print('\n---ASCII File---')
    # print(out)
    # print('------')
    with open(dat_file, 'wt') as newfile:
        newfile.write(out)
    print('Written to: %s' % dat_file)


if __name__ == '__main__':
    import sys
    for n, arg in enumerate(sys.argv):
        if arg == '-h' or arg.lower() == '--help':
            print(__doc__)
        if arg.endswith('.nxs'):
            dat = sys.argv[n + 1] if len(sys.argv) > n + 1 and sys.argv[n + 1].endswith('.dat') else None
            nxs2dat(arg, dat)
