"""
Command line program
"""

import sys
import os
import logging
from time import sleep, ctime, time
from hdfmap import list_files
from nexus2srs import nxs2dat, set_logging_level


logger = logging.getLogger(__name__)
DAT_SUBFOLDER = 'spool'  # DLS specific


def doc():
    import nexus2srs
    help(nexus2srs)


def default_srs_folder(nexus_folder: str, srs_folder: str | None = None) -> str:
    """Return default folder for converted dat files"""
    if srs_folder is None:
        srs_folder = os.path.join(nexus_folder, DAT_SUBFOLDER)
    logger.info(f"srs_folder: {srs_folder}, exists: {os.path.isdir(srs_folder)}")
    if not os.path.isdir(srs_folder):
        raise FileNotFoundError(f"Folder doesn't exist: {srs_folder}")
    return srs_folder


def synchronise_files(nexus_folder, srs_folder=None, write_tiff=False, seconds_since_modified=300):
    """Synchronise converted files between folders"""
    srs_folder = default_srs_folder(nexus_folder, srs_folder)
    nexus_files = list_files(nexus_folder)
    dat_files = list_files(srs_folder)
    logger.info(f"Synchronising {len(nexus_files)} .nxs files in {nexus_folder}\n" +
                f" with {len(dat_files)} .dat files in {srs_folder}")
    conversions = 0
    for nxs_file in nexus_files:
        # check if file is still being written
        if os.path.getmtime(nxs_file) > time() - seconds_since_modified:
            logger.info(f"Ignoring '{nxs_file}' as modified too recently")
            continue
        dat_file = os.path.join(srs_folder, os.path.basename(nxs_file)[:-4] + '.dat')
        if dat_file in dat_files:
            continue
        logger.info(f"Converting {nxs_file} to {dat_file}")
        print(f"Converting {nxs_file} to {dat_file}")
        nxs2dat(nxs_file, dat_file, write_tiff)
        conversions += 1
    return conversions


def continuous_sync(nexus_folder, srs_folder=None, write_tiff=False, pol_seconds=300):
    """Continuously monitor folders and synchronise nexus and dat files"""
    srs_folder = default_srs_folder(nexus_folder, srs_folder)
    print("Starting continuous sync of:")
    print(f"     Nexus files in: {nexus_folder}")
    print(f"    to Dat files in: {srs_folder}")
    print(f"Checking folders every {pol_seconds}s")
    while True:
        conversions = synchronise_files(nexus_folder, srs_folder, write_tiff, seconds_since_modified=pol_seconds)
        print(f"{ctime()}  converted {conversions} scans. Press Ctrl+C to exit.")
        sleep(pol_seconds)


def run_nexus2srs(*args):
    """
    argument runner for nexus2srs

        run_nexus2srs(*arguments)

    Arguments
        file.nxs    Convert file.nxs to file.dat
        file.nxs newfile.dat    Convert file.nxs to newfile.dat
        /folder     convert all folder/*.nxs files to folder/spool/*.dat
        /folder /new    convert all folder/*.nxs files to new/*.dat
        -tiff       Convert detector files to TIFF images
        -sync       Continuously synchronise folders
        -h, --help  Display documentation
        --info      Set logging level to INFO
        --debug     Set logging level to DEBUG
        --quiet     Turn off logging (except errors)

    Examples
        run_nexus2srs('/path/file.nxs', '-tiff') -> converts single file with TIFF generation
        run_nexus2srs('/path', '-tiff') -> converts all files in /path to dat files in /path/spool
    """
    if any(arg.lower() in ['-h', '--help', 'man'] for arg in args):
        doc()
        return
    if '--info' in args:
        set_logging_level('info')
    if '--debug' in args:
        set_logging_level('debug')
    if '--error' in args or '--quiet' in args:
        set_logging_level('error')

    tot = 0
    look_for_dir = True
    for n, arg in enumerate(args):
        if arg.endswith('.nxs'):
            tot += 1
            dat = args[n + 1] if len(args) > n + 1 and (
                    args[n + 1].endswith('.dat') or os.path.isdir(args[n + 1])
            ) else None
            print(f"\n----- {arg} -----")
            nxs2dat(arg, dat, '-tiff' in args)
            look_for_dir = False
        elif look_for_dir and os.path.isdir(arg):
            srs_folder = args[n + 1] if len(args) > n + 1 and os.path.isdir(args[n + 1]) else None
            if '-sync' in args:
                continuous_sync(arg, srs_folder, '-tiff' in args)
                break
            else:
                tot = synchronise_files(arg, srs_folder, '-tiff' in args, 0)
                break
    
    print('\nCompleted %d conversions' % tot)


def cli_nexus2srs():
    """command line argument runner for nexus2srs"""
    run_nexus2srs(*sys.argv)
