#!/usr/bin/env python3
"""Tool to research signal values.
Read *.dat:
import csv
values = list(map(int, [i[2] for i in [r for r in csv.reader(open('/mnt/shares/VCS/my/iosc.py/_sample/sample_ascii.dat'))]]))
"""
import math
from collections import namedtuple
import numpy as np

DataClass = namedtuple('DataClass', ['spp', 'a', 'b', 'p', 's', 'v'])
Data = DataClass(
    spp=20,  # samples per period
    a=0.1138916015625,  # general multiplier
    b=0.05694580078125,  # offset
    p=933,  # primary multiplier
    s=1,  # secondary multiplier
    v=(
        -83, -15, 55, 122, 182, 228, 260, 271, 260, 228,
        178, 113, 43, -30, -95, -150, -187, -202, -195, -165,
        -118, -57, 10, 78, 138, 187, 219, 230, 221, 191,
        143, 83, 17, -50, -111, -161, -195, -208, -199, -169
    )
)


def main():
    def _win(__a, __i, __spp) -> np.array:
        return __a[__i + 1 - __spp:__i + 1] if i + 1 >= __spp else np.pad(__a[:__i + 1], (__spp - __i - 1, 0))

    def _fft(__w) -> np.array:
        return np.fft.fft(__w, norm='ortho')

    values = np.array(Data.v) * Data.a + Data.b
    print("# \t     Sec\t     Mid\t     Eff\t  H1_mod\t  H1_ang\t      H2\t      H3\t      H5\n==\t" + "\t".join(
        8 * [8 * "="]))
    for i, v in enumerate(values):
        # Array window (float[Data.spp] = 0,…value[0],…value[i])
        w = _win(values, i, Data.spp)
        print("{:2d}\t{:8.3f}\t{:8.3f}\t{:8.3f}\t{:8.3f}\t{:8.3f}\t{:8.3f}\t{:8.3f}\t{:8.3f}".format(
            i, v, np.average(w),
            np.sqrt(np.average(w**2)),  # np.std() not helps
            np.abs(_fft(w))[1],
            np.degrees(np.angle(_fft(w)))[1],
            np.abs(_fft(w))[2],
            np.abs(_fft(w))[3],
            np.abs(_fft(w))[5],
        ))


if __name__ == '__main__':
    main()
