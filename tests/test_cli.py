import pytest
import os
import shutil
from nexus2srs import run_nexus2srs, set_logging_level


DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
FILE_NEW_NEXUS = os.path.join(DATA_FOLDER, '1040323.nxs')  # new nexus format
NEW_FOLDER = os.path.join(DATA_FOLDER, 'test')

set_logging_level('info')


def test_run_nexus2srs():
    # Make folder /test
    os.makedirs(NEW_FOLDER, exist_ok=True)
    command = f"python -m nexus2srs {FILE_NEW_NEXUS} {NEW_FOLDER} -tiff"
    print(command)
    run_nexus2srs(*command.split())

    assert os.path.exists(NEW_FOLDER + '/1040323.dat'), "file conversion not completed"
    assert os.path.exists(NEW_FOLDER + '/1040323-pil3_100k-files/00021.tif'), "TIFF file writing incomplete"
    # remove TIFF files
    shutil.rmtree(NEW_FOLDER)
