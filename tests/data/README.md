# Example Nexus and SRS Files

## File Types
| Filename | Description                |
|----------|----------------------------|
| *.dat    | SRS file in ASCII format   |
| *.nxs    | NeXus file in HDF format   |
| *.hdf    | Detector image files       |
| *.tif    | Saved detector image files |

## Scan numbers
| Filename        | Beamline   | Description          | Scan Command                                                                           |
|-----------------|------------|----------------------|----------------------------------------------------------------------------------------|
| 1040323.nxs     | I16        | new nexus, hkl scan  | scan hkl [0.97, 0.02, 0.11] [0.97, 0.02, 0.13] [0, 0, 0.001] MapperProc pil3_100k 1    |
| 1049598.nxs     | I16        | old nexus, eta scan  | scan hkl [-0.05, 0, 0.933] [0.05, 0, 0.933] [0.001, 0, 0] BeamOK pil3_100k 1 roi2 roi1 |
| 1054135.nxs     | I16        | new nexus, slit scan | scan s5 [0, 0] [1, 0] [0.1, 0] Waittime 0.1 diode                                      |
| i06-353130.nxs  | i06        | 2D pol energy scan   | scan pol ('pc', 'nc') energy (707.4, 700) ds 1 20 1 medipix 1                          |


