"""
nexus2srs
Lightweight function to convert Nexus (.nxs) scan Files to the classic SRS .dat files.

Usage:
>> from nexus2srs import nxs2dat
>> nxs2dat('12345.nxs')

By Dan Porter, PhD
Diamond Light Source Ltd.
2022
"""

from nexus2srs.load_hdf import nxs2dat

__version__ = "0.1.0"
__date__ = "2022/12/16"


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
    import os
    out += '\nRunning in directory: %s\n' % os.path.abspath('.')
    return out


