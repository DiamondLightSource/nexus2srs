"""

"""
if __name__ == '__main__':

    import sys
    from nexus2srs import nxs2dat

    tot = 0
    for n, arg in enumerate(sys.argv):
        if arg == '-h' or arg.lower() == '--help':
            tot += 1
            import nexus2srs
            help(nexus2srs)
        if arg.endswith('.nxs'):
            tot += 1
            dat = sys.argv[n + 1] if len(sys.argv) > n + 1 and sys.argv[n + 1].endswith('.dat') else None
            nxs2dat(arg, dat)

    if tot > 1:
        print('\nCompleted %d conversions' % tot)
    else:
        import nexus2srs
        help(nexus2srs)