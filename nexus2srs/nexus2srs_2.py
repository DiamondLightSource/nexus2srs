"""
Python module with functions to load HDF files and write classic SRS .dat files

Usage (Python)
>> from nexus2srs import nxs2dat
>> nxs2dat('12345.nxs', '12345.dat')

Usage (from terminal - converts scan files from NeXus to ASCII format):
$ python nexus2srs 12345.nxs 12345.dat

The file conversion follows the following protocol:
    0. Open .nxs HDF file (using h5py) and create list of all datasets
    1. Search all datasets for one called "scan_fields"
    1.1 Use names from "scan_fields" to populate scandata, matching dataset names or dataset.attr['gda_field_name']
    2. If "scan_fields" not available, determine scan shape from most common dataset shapes with size > 1
    2.1 Add all unique datasets with shape matching scan_shape to scandata
    3. Add all datasets with size=1 to metadata
    4. search for datasets 'scan_command', 'start_time', 'scan_header' to complete the file header
    5. search for dataset 'image_address' and add metadata field %s_path_template where %s is the detector name

By Dan Porter, PhD
Diamond Light Source Ltd.
2022
"""

import os
import datetime
import h5py
from collections import Counter
from numpy import squeeze, reshape

__version__ = "0.4.0"
__date__ = "2023/01/18"

# --- Default HDF Names ---
NXSCANFIELDS = 'scan_fields'
NXSCANHEADER = 'scan_header'
NXMEASUREMENT = 'measurement'
NXMETA = 'positioners'
NXRUN = 'entry_identifier'
NXCMD = 'scan_command'
NXDATE = 'start_time'
NXIMAGE = 'image_data'
NXATTR = 'gda_field_name'  # dataset attribute name

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
HEADER = """ &SRS
 SRSRUN=%s,SRSDAT=%s,SRSTIM=%s,
 SRSSTN='BASE',SRSPRJ='GDA_BASE',SRSEXP='Emulator',
 SRSTLE='                                                            ',
 SRSCN1='        ',SRSCN2='        ',SRSCN3='        ',"""  # % (srsrun, srsdat, srstim)


def address_name(address):
    """Convert hdf address to name"""
    return os.path.basename(address)


def filename2name(filename):
    """Convert filename to run number"""
    return os.path.splitext(os.path.basename(filename))[0]


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


def get_address_datasets(hdf):
    """
    Return a list of all HDF datasets and dataset addresses
    :param hdf: HDF file object from h5py.File
    :return: list of (address, dataset) for each unique dataset in hdf
    """
    datasets = []
    ids = []

    def func(address, obj):
        if isinstance(obj, h5py.Dataset):
            if obj.id not in ids:
                ids.append(obj.id)
                datasets.append((address, obj))
    hdf.visititems(func)
    return datasets


def search_address_datasets(name, address_datasets, default=None):
    """Search list of HDF (address, dataset) for field name, return address or default"""
    search = [adr for adr, ds in address_datasets if address_name(adr) == name]
    if search:
        return search[0]
    return default


def get_scan_meta_header(hdf):
    """
    Create dicts of metadata and scan data from hdf file. Metadata are size 1 values, scandata are 1D arrays

    Follows the following protocol:
        1. Search all datasets for one called "scan_fields"
        1.1 Use names from "scan_fields" to populate scandata, matching dataset names or dataset.attr['gda_field_name']
        2. If "scan_fields" not available, determine scan shape from most common dataset shapes with size > 1
        2.1 Add all unique datasets with shape matching scan_shape to scandata
        3. Add all datasets with size=1 to metadata
        4. search for datasets 'scan_command', 'start_time', 'scan_header' to complete the file header
        5. search for dataset 'image_address' and add metadata field %s_path_template where %s is the detector name

    Note: In python>=3.6, the {} dict preseverves the key order,
          so the order of scandata will match how it was generated

    :param hdf: HDF Group object
    :return scandata: {name: array} dict of scanned data, all fields have n length arrays
    :return metadata: {name: value} dict of metadata, all fields are float/int/str
    :return header: str of header data to add to dat file
    """

    # Find HDF addresses
    address_datasets = get_address_datasets(hdf)  # [(hdf_address, hdf_dataset)]
    # searching the list of addresses is much faster than searching the hdf file
    scan_fields_address = search_address_datasets(NXSCANFIELDS, address_datasets)
    scan_header_address = search_address_datasets(NXSCANHEADER, address_datasets)
    scan_id_address = search_address_datasets(NXRUN, address_datasets)
    scan_cmd_address = search_address_datasets(NXCMD, address_datasets)
    scan_time_address = search_address_datasets(NXDATE, address_datasets)
    scan_image_address = search_address_datasets(NXIMAGE, address_datasets)

    # Load data
    ids = []
    metadata = {}
    scandata = {}
    if scan_fields_address:
        print('NXclassic_scan')
        scan_fields = hdf[scan_fields_address][()]
        print('scan_fields: ' + ', '.join(scan_fields))
        scan_datasets = [(adr, ds) for adr, ds in address_datasets if ds.size > 1]  # select arrays
        scan_names = [address_name(adr) for adr, ds in scan_datasets]
        scan_gda_names = [ds.attrs[NXATTR] if NXATTR in ds.attrs else '' for adr, ds in scan_datasets]
        for scan_field in scan_fields:
            if scan_field in scan_names:
                adr, ds = scan_datasets[scan_names.index(scan_field)]  # returns first instance
            elif scan_field in scan_gda_names:
                adr, ds = scan_datasets[scan_names.index(scan_field)]
            else:
                print('Scan field %s not available' % scan_field)
                continue
            ids.append(ds.id)
            scandata[scan_field] = dataset2scandata(ds)
        scan_shape = None  # skip over finding additional arrays below
    else:
        print('Generic_scan - scan field names not preserved. Search for scan_shape')
        # Find datasets with ndim 1 or 2 and size > 1
        scan_shapes = [ds.shape for _, ds in address_datasets if (ds.ndim == 1 or ds.ndim == 2) and ds.size > 1]
        if len(scan_shapes) == 0:
            # Catch situation of no array data
            print('Warning: File contains no scan data (no arrays greater than length 1)')
            scan_shape = None
        else:
            scan_shape, counts = Counter(scan_shapes).most_common(1)[0]
            print('Scan shape: ' + str(scan_shape))

    # --- Load Data ---
    # Loop through each dataset, comparing ids to not replicate data
    #  if dataset is size==1, add to metadata
    #  if dataset is shape==scan_shape array, add to scandata
    for address, dataset in address_datasets:
        if dataset.id in ids:
            continue
        ids.append(dataset.id)
        name = address_name(address)

        # --- Metadata ---
        if dataset.size == 1:
            metadata[name] = dataset2metadata(dataset)

        # ---Scandata ---
        elif scan_shape and dataset.shape == scan_shape:
            try:
                # Only add floats, reshape to 1D array
                scandata[name] = reshape(dataset, -1) * 1.0
            except TypeError:
                pass

    # --- Find Required metadata ---
    try:
        date = datetime.datetime.strptime(hdf[scan_time_address][()], DATE_FORMAT)
    except (KeyError, ValueError, TypeError):
        date = datetime.datetime.fromtimestamp(os.path.getctime(hdf.filename))

    req_meta = {
        'cmd': hdf[scan_cmd_address][()] if scan_cmd_address else '',
        'date': date.strftime('%a %b %d %H:%M:%S %Y'),
    }
    # Image data path
    if scan_image_address:
        # Get image path, e.g. '815893-pilatus3_100k-files
        image_data = reshape(hdf[scan_image_address], -1).astype(str)
        image_path, _ = os.path.split(image_data[0])
        # Get detector name from path
        try:
            detector_name = image_path.split('-')[1]
        except IndexError:
            detector_name = 'image'
        req_meta[detector_name + '_path_template'] = image_path + '/%05d.tif'
    req_meta.update(**metadata)

    # --- generate header ---
    # 1. Check NXclassic_scan header
    if scan_header_address:
        header = '\n'.join(h for h in hdf[scan_header_address])
    else:
        srsrun = '%s' % hdf[scan_id_address][()] if scan_id_address else filename2name(hdf.filename)
        srsdat = date.strftime('%Y%m%d')
        srstim = date.strftime('%H%M%S')
        header = HEADER % (srsrun, srsdat, srstim)
    return scandata, req_meta, header


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

    print('Nexus File: %s' % nexus_file)
    with h5py.File(nexus_file, 'r') as hdf:
        scandata, metadata, header = get_scan_meta_header(hdf)

    # --- Scan length ---
    scan_length = len(next(iter(scandata.values()))) if scandata else 0
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
