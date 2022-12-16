"""

"""
if __name__ == '__main__':

    import sys
    from nexus2srs import nxs2dat

    for arg in sys.argv:
        if '.py' in arg:
            continue
        try:
            nxs2dat(arg)
        except Exception:
            pass

