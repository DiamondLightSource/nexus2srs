"""
Python module with functions to load HDF files and write classic SRS .dat files

Usage (Python)
>> from nexus2srs import nxs2dat
>> nxs2dat('12345.nxs', '12345.dat')

Usage (from terminal - converts scan files from NeXus to ASCII format):
$ python nexus2srs 12345.nxs 12345.dat

By Dan Porter, PhD
Diamond Light Source Ltd.
2022
"""

import os
import datetime
import h5py
from collections import Counter
from numpy import squeeze, reshape, argmax, prod

__version__ = "0.3.0"
__date__ = "2023/01/16"

# --- Default HDF Addresses ---
# NeXus Classic Scan
NXENTRY = '/entry1'
NXSCAN = NXENTRY + '/scan'
NXSCANFIELDS = NXSCAN + '/scan_fields'
NXSCANHEADER = NXSCAN + '/scan_header'
NXMEASUREMENT = NXSCAN + '/measurement'
NXMETA = NXSCAN + '/positioners'
NXATTR = 'gda_field_name'  # dataset attribute name

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


def get_all_groups(hdf):
    """Return a list of all HDF groups with addresses and nx_class name"""
    datasets = []

    def func(address, obj):
        if isinstance(obj, h5py.Group):
            # NX_class attribute usually returns bytes, decode to str or get AttributeError if str
            nx_class = obj.attrs['NX_class'].decode() if 'NX_class' in obj.attrs else ''
            datasets.append((address, obj, nx_class))
    hdf.visititems(func)
    return datasets


def find_dataset(hdf, name):
    """Find address with matching name in HDF file (returns first found exact match, or None)"""

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
    image_address = find_dataset(hdf, 'image_data')  # returns None if image_data doesn't exist
    if image_address:
        # Get image path, e.g. '815893-pilatus3_100k-files
        image_data = reshape(hdf[image_address], -1).astype(str)
        image_path, _ = os.path.split(image_data[0])
        # Get detector name from path
        try:
            detector_name = image_path.split('-')[1]
        except IndexError:
            detector_name = 'image'
        meta[detector_name + '_path_template'] = image_path + '/%05d.tif'
    return meta


def get_scan_meta_data(hdf):
    """
    Create dicts of metadata and scan data from hdf file. Metadata are size 1 values, scandata are 1D arrays

    Follows the following protocol:
        1. Search for NXclassic_scan with dataset 'entry1/scan/scan_fields', defining names of scan arrays
           scan arrays in 'entry1/scan/measurement', metadata in 'entry1/scan/positioners'
        2. Search for NXclassic_scan with dataset 'entry1/scan/scan_fields',
           Names from scan_fields are searched in dataset addresses and dataset 'gda_field_name' attributes,
           metadata in 'entry1/scan/positioners
        3. Search for I16historic_scan: scan arrays in 'entry1/measurement', metadata in 'entry1/before_scan'
        4. Generic search:
            scan data are 1D or 2D datasets (size>1) with shapes matching the most common dataset shape
            metadata are size 1 datasets

    Note: In python>=3.6, the {} dict preseverves the key order,
          so the order of scandata will match how it was generated

    :param hdf: HDF Group object
    :return scandata: {name: array} dict of scanned data, all fields have n length arrays
    :return metadata: {name: value} dict of metadata, all fields are float/int/str
    """

    # 1. --- NXclassic_scan ---
    # Scan fields defined in entry1/scan/scan_fields, metadata in entry1/scan/positioners
    if NXSCANFIELDS in hdf and NXMEASUREMENT in hdf:
        print('NXclassic_scan')
        scandata = {
            name: dataset2scandata(hdf[NXMEASUREMENT + '/%s' % name])
            for name in hdf[NXSCANFIELDS][()]
        }
        metadata = {
            address_name(adr): dataset2metadata(ds)
            for adr, ds in get_all_datasets(hdf[NXMETA]) if ds.size == 1
        }

    # 1.5. --- NXclassic_scan with scan name attributes ---
    # Scan fields defined in entry1/scan/scan_fields, metadata somewhere
    # datasets have attributes "gda_field_name" to check againsts scan_fields
    elif NXSCANFIELDS in hdf:
        print('NXclassic_scan with gda_field_name attribute search')
        address_datasets = get_all_datasets(hdf)
        address_datasets = [(adr, ds) for adr, ds in address_datasets if ds.size > 1]  # select arrays
        scan_names = [address_name(adr) for adr, ds in address_datasets]
        scan_gda_names = [ds.attrs[NXATTR] if NXATTR in ds.attrs else '' for adr, ds in address_datasets]
        scandata = {}
        for scan_field in hdf[NXSCANFIELDS][()]:
            if scan_field in scan_names:
                adr, ds = address_datasets[scan_names.index(scan_field)]  # returns first instance
            elif scan_field in scan_gda_names:
                adr, ds = address_datasets[scan_names.index(scan_field)]
            else:
                print('Scan field %s not available' % scan_field)
                continue
            scandata[scan_field] = dataset2scandata(ds)
        metadata = {
            address_name(adr): dataset2metadata(ds)
            for adr, ds in get_all_datasets(hdf[NXMETA]) if ds.size == 1
        }

    # 2. --- I16 historic scan ---
    # Scan data in /entry1/measurement, metadata in /entry1/before_scan
    # Measurement fields with no entries are ignored
    elif I16META in hdf and I16MEASUREMENT in hdf and len(hdf[I16MEASUREMENT]) > 0:
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
        if len(scan_shapes) == 0:
            # Catch situation of no array data - cannot be converted to SRS
            # raise Exception('File contains no scan data (no arrays greater than length 1)')
            print('Warning: File contains no scan data (no arrays greater than length 1)')
            scan_shape = None
        else:
            # Method 1: find the array with most points
            # This works pretty well for 1/2 dimensional scans, but won't work for any higher dimension (if possible...)
            # Finding the largest array doesn't work well for short scans, as unit_cell(6) might be longer
            # scan_shape = scan_shapes[argmax([prod(s) for s in scan_shapes])]
            # Method 2:  find the most common scan shape
            scan_shape, counts = Counter(scan_shapes).most_common(1)[0]  # from collections import Counter
            # Or
            # shapes, counts = np.unique(np.array(scan_shapes, dtype=object), return_counts=True)
            # scan_shape = shapes[argmax(counts)]  #  this is slower than Counter
            print('Scan shape: ' + str(scan_shape))

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


def get_scan_meta_data2(hdf):
    """
    Create dicts of metadata and scan data from hdf file. Metadata are size 1 values, scandata are 1D arrays

    Follows the following protocol:
        1. Search all datasets for one called "scan_fields"
        1.1 Use names from "scan_fields" to populate scandata, matching dataset names or dataset.attr['gda_field_name']
        2. If "scan_fields" not available, determine scan shape from most common dataset shapes with size > 1
        2.5 Add all unique datasets with shape matching scan_shape to scandata
        3. Add all datasets with size=1 to metadata

    Note: In python>=3.6, the {} dict preseverves the key order,
          so the order of scandata will match how it was generated

    :param hdf: HDF Group object
    :return scandata: {name: array} dict of scanned data, all fields have n length arrays
    :return metadata: {name: value} dict of metadata, all fields are float/int/str
    """

    address_datasets = get_all_datasets(hdf)  # [(hdf_address, hdf_dataset)]
    ids = []
    metadata = {}
    scandata = {}

    # scan_fields_address = find_dataset(hdf, 'scan_fields')  # slow
    scan_fields_address = [adr for adr, ds in address_datasets if adr.endswith('/scan_fields')]  # fast
    if scan_fields_address:
        print('NXclassic_scan')
        scan_fields = hdf[scan_fields_address[0]][()]
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
        scan_shape = None
    else:
        # Generic scan - find scan shape
        # Find datasets with ndim 1 or 2 and size > 1
        scan_shapes = [ds.shape for _, ds in address_datasets if (ds.ndim == 1 or ds.ndim == 2) and ds.size > 1]
        if len(scan_shapes) == 0:
            # Catch situation of no array data - cannot be converted to SRS
            print('Warning: File contains no scan data (no arrays greater than length 1)')
            scan_shape = None
            # raise Exception('File contains no scan data (no arrays greater than length 1)')
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

    print('Nexus File: %s' % nexus_file)
    with h5py.File(nexus_file, 'r') as hdf:
        scandata, metadata = get_scan_meta_data(hdf)
        header = generate_header(hdf)

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


def nxs2dat2(nexus_file, dat_file=None):
    """
    Load HDF file and convert to classic SRS .dat file (Alternative version)
    :param nexus_file: str filename of HDF/Nexus file
    :param dat_file: str filename of ASCII file to create (None renames nexus file as *.dat)
    :return: None
    """
    if dat_file is None:
        dat_file = os.path.splitext(nexus_file)[0] + '.dat'

    with h5py.File(nexus_file, 'r') as hdf:
        scandata, metadata = get_scan_meta_data2(hdf)
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
