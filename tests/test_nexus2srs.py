import pytest
import os
import shutil
from nexus2srs import nxs2dat, set_logging_level

set_logging_level('info')

DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
FILE_NEW_NEXUS = DATA_FOLDER + '/1040323.nxs'  # new nexus format

FILES = [
    '1040323.nxs',  # I16, new nexus, hkl scan, scan hkl
    '1049598.nxs',  # I16, old nexus, eta scan, scan hkl
    '1054135.nxs',  # I16, new nexus, slit scan, scan s5 [0, 0] [1, 0] [0.1, 0] Waittime 0.1 diode
    'i06-353130.nxs',  # i06, 2D pol energy scan, scan pol ('pc', 'nc') energy (707.4, 700) ds 1 20 1 medipix 1
]


def test_nxs2dat_new_nexus():
    nexus_file = DATA_FOLDER + '/' + FILES[0]
    new_file = nexus_file.replace('.nxs', '.dat')
    if os.path.exists(new_file):
        os.remove(new_file)
    nxs2dat(nexus_file, new_file, True)
    assert os.path.exists(new_file), "file conversion not completed"
    assert os.path.exists(DATA_FOLDER + '/1040323-pil3_100k-files/00021.tif'), "tif file writing imcomplete"
    # remove tif files
    shutil.rmtree(DATA_FOLDER + '/1040323-pil3_100k-files')
    # Check dat file
    with open(new_file, 'r') as f:
        srs_text = f.read()
    assert srs_text.count('\n') == 208, "file conversion has wrong number of lines"
    assert "pil3_100k_path_template='1040323-pil3_100k-files/%05d.tif'" in srs_text, "path template missing"


def test_nxs2dat_old_nexus():
    nexus_file = DATA_FOLDER + '/' + FILES[1]
    new_file = nexus_file.replace('.nxs', '.dat')
    if os.path.exists(new_file):
        os.remove(new_file)
    nxs2dat(nexus_file, new_file, False)
    assert os.path.exists(new_file), "file conversion not completed"
    with open(new_file, 'r') as f:
        srs_text = f.read()
    assert srs_text.count('\n') == 537, "file conversion has wrong number of lines"
    assert "pil3_100k_path_template='1049598-pil3_100k-files/%05d.tif'" in srs_text, "path template missing"


def test_nxs2dat_new_nexus2():
    nexus_file = DATA_FOLDER + '/' + FILES[2]
    new_file = nexus_file.replace('.nxs', '.dat')
    if os.path.exists(new_file):
        os.remove(new_file)
    nxs2dat(nexus_file, new_file, False)
    assert os.path.exists(new_file), "file conversion not completed"
    with open(new_file, 'r') as f:
        srs_text = f.read()
    assert srs_text.count('\n') == 219, "file conversion has wrong number of lines"


def test_nxs2dat_3d_i06():
    nexus_file = DATA_FOLDER + '/' + FILES[3]
    new_file = nexus_file.replace('.nxs', '.dat')
    if os.path.exists(new_file):
        os.remove(new_file)
    nxs2dat(nexus_file, new_file, True)
    assert os.path.exists(new_file), "file conversion not completed"
    assert os.path.exists(DATA_FOLDER + '/i06-353130-medipix-files/00001.tif'), "tif file writing imcomplete"
    # remove tif files
    shutil.rmtree(DATA_FOLDER + '/i06-353130-medipix-files')
    # Check dat file
    with open(new_file, 'r') as f:
        srs_text = f.read()
    assert srs_text.count('\n') == 195, "file conversion has wrong number of lines"
    assert "medipix_path_template='i06-353130-medipix-files/%05d.tif'" in srs_text, "path template missing"

