"""
Command line program
"""

import sys
from nexus2srs import nxs2dat


def run_nexus2srs(*args):
    """argument runner for nexus2srs"""
    tot = 0
    for n, arg in enumerate(args):
        if arg == '-h' or arg.lower() == '--help' or arg == 'man':
            tot += 1
            import nexus2srs
            help(nexus2srs)
        if arg.endswith('.nxs'):
            tot += 1
            dat = args[n + 1] if len(args) > n + 1 and args[n + 1].endswith('.dat') else None
            print(f"\n----- {arg} -----")
            nxs2dat(arg, dat, '-tiff' in args)
    
    if tot > 0:
        print('\nCompleted %d conversions' % tot)
    else:
        import nexus2srs
        help(nexus2srs)


def cli_nexus2srs():
    """command line argument runner for nexus2srs"""
    run_nexus2srs(*sys.argv)
