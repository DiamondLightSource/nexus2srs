"""

"""
if __name__ == '__main__':

    import sys
    from nexus2srs import nxs2dat

    for n, arg in enumerate(sys.argv):
        if arg == '-h' or arg.lower() == '--help':
            import nexus2srs
            help(nexus2srs)
        if arg.endswith('.nxs'):
            dat = sys.argv[n + 1] if len(sys.argv) > n + 1 and sys.argv[n + 1].endswith('.dat') else None
            nxs2dat(arg, dat)

