import pytest
import os
import shutil
import subprocess
from nexus2srs import run_nexus2srs, set_logging_level


DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
FILE_NEW_NEXUS = os.path.join(DATA_FOLDER, '1040323.nxs')  # new nexus format
NEW_FOLDER = os.path.join(DATA_FOLDER, 'test')
SPOOL_FOLDER = os.path.join(DATA_FOLDER, 'spool')

set_logging_level('info')


def test_run_nexus2srs():
    # Make folder /test
    if os.path.isdir(NEW_FOLDER):
        shutil.rmtree(NEW_FOLDER)
    os.makedirs(NEW_FOLDER, exist_ok=True)
    print(f"Create folder : {NEW_FOLDER} : {os.path.isdir(NEW_FOLDER)}")
    command = f"python -m nexus2srs \"{FILE_NEW_NEXUS}\" \"{NEW_FOLDER}\" -tiff"
    print('Running command:')
    print(command)
    output = subprocess.run(command, shell=True, capture_output=True)
    print('\nOutput:')
    print(output.stdout.decode())

    assert os.path.exists(NEW_FOLDER + '/1040323.dat'), "file conversion not completed"
    assert os.path.exists(NEW_FOLDER + '/1040323-pil3_100k-files/00021.tif'), "TIFF file writing incomplete"
    # remove TIFF files
    shutil.rmtree(NEW_FOLDER)


def test_synchronise():
    # Make folder /test
    if os.path.isdir(SPOOL_FOLDER):
        print('Removing folder')
        shutil.rmtree(SPOOL_FOLDER)
    os.makedirs(SPOOL_FOLDER, exist_ok=True)
    print(f"Create folder : {SPOOL_FOLDER} : {os.path.isdir(SPOOL_FOLDER)}")
    print(os.listdir(SPOOL_FOLDER))
    command = f"python -m nexus2srs \"{DATA_FOLDER}\" --info"
    print('Running command:')
    print(command)
    output = subprocess.run(command, shell=True, capture_output=True)
    print('\nOutput:')
    print(output.stdout.decode())

    nexus_files = [file for file in os.listdir(DATA_FOLDER) if file.endswith('.nxs')]
    dat_files = [file for file in os.listdir(SPOOL_FOLDER) if file.endswith('.dat')]
    assert len(nexus_files) == len(dat_files), 'not all files converted'
    # remove TIFF files
    shutil.rmtree(SPOOL_FOLDER)
