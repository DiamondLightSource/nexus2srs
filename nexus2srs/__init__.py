"""
nexus2srs
Program to convert NeXus (.nxs) scan Files to the classic ASCII SRS .dat files.

Usage (in python):
>> from nexus2srs import nxs2dat
>> nxs2dat('12345.nxs', '12345.dat', write_tiff=False)

Usage (from terminal):
$ nexus2srs 12345.nxs 12345.dat
Include '-tiff' in arguments to save detector images as tif images.

By Dan Porter, PhD
Diamond Light Source Ltd.
2023-2024
"""

from nexus2srs.nexus2srs import __date__, __version__, set_logging_level, nxs2dat
from nexus2srs.cli import run_nexus2srs

__all__ = [
    'nxs2dat', 'run_nexus2srs', 'set_logging_level', 'version_info', 'module_info'
]


def version_info():
    return 'nexus2srs version %s (%s)' % (__version__, __date__)


def module_info():
    import sys
    out = 'Python version %s' % sys.version
    out += '\n at: %s' % sys.executable
    out += '\n %s: %s' % (version_info(), __file__)
    # Modules
    import numpy
    out += '\n     numpy version: %s' % numpy.__version__
    import h5py
    out += '\n      h5py version: %s' % h5py.__version__
    import hdfmap
    out += '\n    hdfmap version: %s' % hdfmap.__version__
    import os
    out += '\nRunning in directory: %s\n' % os.path.abspath('.')
    return out


