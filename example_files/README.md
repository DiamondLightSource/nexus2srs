# Example Nexus and SRS Files

## File Types
| Filename   | Description                                 |
|------------|---------------------------------------------|
| *.dat      | SRS file in ASCII format                    |
| *.nxs      | NeXus file in HDF format                    |
| #_new.dat  | Converted files using nxs2dat               |
| #_tree.txt | Printout of tree structure of NeXus file    |

## Scan numbers
| Number | Description    | Scan Command                                                                       |
|--------|----------------|------------------------------------------------------------------------------------|
| 782761 | hkl scan       | scan hkl [0, 0.5, -16.5] [0, 0.9, -16.5] [0.0, 0.01, 0.0] pil3_100k 5 roi1 roi2 Ta |
| 794932 | eta scan       | scancn eta 0.01 61 BeamOK pil3_100k 1 roi2                                         |
| 815893 | NXclassic_scan | scan eta 30.97 32.56 0.02 BeamOK pil3_100k 1 roi2                                  |
| 879486 | 2D scan        | scan sz 9.45 9.55 0.05 sperp -0.2 0.2 0.02 pil3_100k 1 roi2                        |
| 970792 | kdelta scan    | Missing measurement, scan length < 6                                               |

