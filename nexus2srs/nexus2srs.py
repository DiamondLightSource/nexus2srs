"""
Python module with functions to load HDF files and write classic SRS .dat files

By Dan Porter, PhD
Diamond Light Source Ltd.
2023
"""

import os
import datetime
import re

import h5py
import numpy as np
from numpy import ndindex
import hdfmap

__version__ = "0.6.0"
__date__ = "2024/09/26"

# --- Default HDF Names ---
NXSCANFIELDS = 'scan_fields'
NXSCANHEADER = 'scan_header'
NXMEASUREMENT = 'measurement'
NXMETA = 'positioners'
NXRUN = 'entry_identifier'
NXCMD = 'scan_command'
NXDATE = 'start_time'
NXIMAGE = 'image_data'
NXDETECTOR = 'NXdetector'
NXDATA = 'data'
NXATTR = 'local_name'  # 'gda_field_name'  # dataset attribute name

PATH_TEMPLATE = '%05d.tif'
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
HEADER = """ &SRS
 SRSRUN=%s,SRSDAT=%s,SRSTIM=%s,
 SRSSTN='BASE',SRSPRJ='GDA_BASE',SRSEXP='Emulator',
 SRSTLE='                                                            ',
 SRSCN1='        ',SRSCN2='        ',SRSCN3='        ',"""  # % (srsrun, srsdat, srstim)


def write_image(image: np.ndarray, filename: str):
    """Write 2D array to TIFF image file"""
    if os.path.isfile(filename):
        return
    from PIL import Image
    im = Image.fromarray(image)
    im.save(filename, "TIFF")
    print('Written image to %s' % filename)


def nexus_scan_number(hdf_file: h5py.File, hdf_map: hdfmap.HdfMap) -> int:
    """
    Generate scan number from file, use entry_identifier or generate file filename
    :param hdf_file: h5py.File object
    :param hdf_map: HdfMap object
    :return: int
    """
    if NXRUN in hdf_map:
        print(f"Scan number from {NXRUN}")
        return int(hdf_map.get_data(hdf_file, NXRUN))
    name = os.path.splitext(os.path.basename(hdf_file.filename))[0]
    numbers = re.findall(r'\d{4,}', name)
    if numbers:
        return int(numbers[0])
    return 0


def nexus_date(hdf_file: h5py.File, hdf_map: hdfmap.HdfMap) -> datetime.datetime:
    """
    Generate date of file, using either start_time or file creation date
    :param hdf_file: h5py.File object
    :param hdf_map: HdfMap object
    :return: datetime object
    """
    if NXDATE in hdf_map:
        date = hdf_map.get_data(hdf_file, NXDATE)
        if isinstance(date, datetime.datetime):
            return date
    print(f"'{NXDATE}' not available or note datetime, using file creation time")
    return datetime.datetime.fromtimestamp(os.path.getctime(hdf_file.filename))


def nexus_header(hdf_file: h5py.File, hdf_map: hdfmap.HdfMap) -> str:
    """
    Generate header from nexus file
    :param hdf_file: h5py.File object
    :param hdf_map: HdfMap object
    :return: str
    """
    if NXSCANHEADER in hdf_map:
        return '\n'.join(h for h in hdf_map.get_data(hdf_file, NXSCANHEADER))
    else:
        date = nexus_date(hdf_file, hdf_map)
        srsrun = nexus_scan_number(hdf_file, hdf_map)
        srsdat = date.strftime('%Y%m%d')
        srstim = date.strftime('%H%M%S')
        return HEADER % (srsrun, srsdat, srstim)


def nexus_detectors(hdf_file: h5py.File, hdf_map: hdfmap.HdfMap) -> (dict, dict):
    """
    Generate detector paths from nexus file
    :param hdf_file: h5py.File object
    :param hdf_map: HdfMap object
    :return: metadata, detector_image_paths
    :return: {'detector_path_template': 'image_path_template'}, {'detector_name': (path, template)}
    """
    metadata = {}
    detector_image_paths = {}
    # Check for 'image_data' field (these files should exist already)
    if NXIMAGE in hdf_map:
        # image_data is an array of tif image names
        image_data = hdf_map.get_data(hdf_file, NXIMAGE)
        # Get image path, e.g. '815893-pilatus3_100k-files
        image_path = os.path.dirname(image_data[0])
        template = "%s/%s" % (image_path, PATH_TEMPLATE)
        # Get detector name from path '0-NAME-files'
        try:
            name = image_path.split('-')[1]
        except IndexError:
            name = 'detector'
        metadata[f"{name}_path_template"] = template

    # build image path from detector class names
    filename, ext = os.path.splitext(os.path.basename(hdf_file.filename))
    for name, path in hdf_map.image_data.items():
        template = f"{filename}-{name}-files/{PATH_TEMPLATE}"
        metadata[f"{name}_path_template"] = template
        detector_image_paths[name] = (path, template)
    return metadata, detector_image_paths


def generate_datafile(hdf_file: h5py.File, hdf_map: hdfmap.HdfMap) -> (str, dict):
    """
    General purpose function to retrieve data from HDF files
    :param hdf_file: h5py.File object
    :param hdf_map: HdfMap object
    :return: dat_string, {'detector_name': (path, template)}
    """
    # metadata
    metadata_str = hdf_map.create_metadata_list(hdf_file)
    # scandata
    scannables_str = hdf_map.create_scannables_table(hdf_file)
    # Date
    date = nexus_date(hdf_file, hdf_map)

    # --- Additional metadata ---
    req_meta = {
        'cmd': hdf_map.get_data(hdf_file, NXCMD, default=''),
        'date': date.strftime("%a %b %d %H:%M:%S %Y"),
    }
    # Detectors
    det_meta, detector_image_paths = nexus_detectors(hdf_file, hdf_map)
    req_meta.update(det_meta)
    # generate string
    required_metadata_str = '\n'.join([f"{name}='{value}'" for name, value in req_meta.items()])

    # --- Header ---
    header = nexus_header(hdf_file, hdf_map)

    # --- Build String ---
    out = '\n'.join([
        header,
        '<MetaDataAtStart>',
        required_metadata_str,
        metadata_str,
        '</MetaDataAtStart>',
        ' &END',
        scannables_str,
        ''  # blank line at end of file
    ])
    return out, detector_image_paths


def write_tifs(hdf: h5py.File, save_dir: str, detector_image_paths: dict):
    """
    Exctract image frames from detectors and save as tif images
    :param hdf: h5py.File object
    :param save_dir: str name of directory to create image folder '{scan}-{detector}-files/'
    :param detector_image_paths: {'detector_name': ('path', 'template')}
    :return: None
    """

    # --- write image data ---
    for name, (hdf_path, template) in detector_image_paths.items():
        print(f'Detector images: {name}: {hdf_path}, template: {template}')
        # Create image folder
        det_folder = os.path.dirname(template)
        det_dir = os.path.join(save_dir, det_folder)
        im_file = os.path.join(save_dir, template)
        if not os.path.isdir(det_dir):
            os.makedirs(det_dir)
            print('Created folder: %s' % det_dir)
        # Write TIF images
        data = hdf[hdf_path]
        # Assume first index is the scan index
        for im, idx in enumerate(ndindex(data.shape[:-2])):  # ndindex returns index iterator of each image
            image = data[idx]
            print(im_file % (im + 1), idx, image.shape)
            write_image(image, im_file % (im + 1))


"----------------------------------------------------------------------------"
"----------------------------- nxs2dat --------------------------------------"
"----------------------------------------------------------------------------"


def nxs2dat(nexus_file: str, dat_file: str = None, write_tif: bool = False):
    """
    Load HDF file and convert to classic SRS .dat file
    :param nexus_file: str filename of HDF/Nexus file
    :param dat_file: str filename of ASCII file to create (None renames nexus file as *.dat)
    :param write_tif: Bool, if True also writes any HDF images to TIF files in a folder
    :return: None
    """
    if dat_file is None:
        dat_file = os.path.splitext(nexus_file)[0] + '.dat'

    nxs_map = hdfmap.create_nexus_map(nexus_file)
    print('Nexus File: %s' % nexus_file)
    with hdfmap.load_hdf(nexus_file) as hdf:
        # --- get scan data and header data from HDF ---
        outstr, detector_image_paths = generate_datafile(hdf, nxs_map)

        with open(dat_file, 'wt') as newfile:
            newfile.write(outstr)
        print('Written to: %s' % dat_file)

        if write_tif:
            write_tifs(hdf, os.path.dirname(dat_file), detector_image_paths)
