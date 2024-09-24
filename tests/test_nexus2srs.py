import pytest
import os
from nexus2srs import nxs2dat

DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
FILE_NEW_NEXUS = DATA_FOLDER + '/1040323.nxs'  # new nexus format


def test_nxs2dat_new_nexus():
    new_file = FILE_NEW_NEXUS.replace('.nxs', '.dat')
    if os.path.exists(new_file):
        os.remove(new_file)
    nxs2dat(FILE_NEW_NEXUS, new_file, True)
    assert os.path.exists(new_file), "file conversion not completed"
    assert os.path.exists(DATA_FOLDER + '/1040323-pil3_100k-files/00021.tif'), "tif file writing imcomplete"
    with open(new_file, 'r') as f:
        srs_text = f.read()
    assert srs_text.count('\n') == 239, "file conversion has wrong number of lines"
    assert "pil3_100k_path_template='1040323-pil3_100k-files/%05d.tif'" in srs_text, "path template missing"
