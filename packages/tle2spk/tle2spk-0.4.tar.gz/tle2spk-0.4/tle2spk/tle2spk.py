#!/usr/bin/env/python3

import spiceypy as cspice
import os as os
import numpy as np

def tle2spk( name , leapsecons , tle , year , first , last):
    """
    This function generates an spk kernel from an input file
    containing a set of TLE (Two Line Elements) propagating the orbit
    between two epochs

    :param name: name of the generated spk file. Example: 'filename.bsp'
    :type name: str
    :param leapsecons: enter the leapsecons kernel path as
                    "./kernels/filename.tls"
    :type leapsecons: str
    :param tle: filename.txt containing the TLE as:
                1 25544U 98067A   18157.52607057  .00016717  00000-0  10270-3 0  9001
                2 25544  51.6411  71.8659 0003216 157.6093 202.5200 15.54141383 36857
                1 25544U 98067A   18158.55489335  .00016717  00000-0  10270-3 0  9013
                2 25544  51.6409  66.7373 0003245 162.2935 197.8331 15.54143414 37016
                .
                .
                .
                (an example TLE file is provided)
    :type tle: str
    :param year: integer with the first year appearing in the set
                    of Two Line Elements
    :type year: int
    :param first: first epoch (UTC format) of the propagation for the spk
                  example: '2018-06-01T00:00:00'
    :type first: str
    :param last: last epoch (UTC format) of the propagation for the spk
    :type last: str
    :return: spk file in the working directory

    """

    try:
        os.remove(name)
    except:
        print('generating spk file')

    file = open(tle, "r")
    a = file.readlines()
    n = len(a) // 2  # number of TLE entries

    print('reading', n, ' Two Line Elements')

    cspice.furnsh(leapsecons)

    tle_list = []

    for tle in a:
        tle_list.append(tle.split('\n')[0])

    print(tle_list)

    CONSTS = [1.082616e-3, -2.53881e-6, -1.65597e-6, 7.43669161e-2,
              120., 78., 6378.135, 1.]

    epoch_x = []
    elems_x = []
    for i in range(0, n, 1):
        epoch_x.append(0)
    for i in range(0, n * 10, 1):
        elems_x.append(0)

    # -------   cspice.getelm   -------

    for i in range(0, n, 1):
        lines = [tle_list[i * 2], tle_list[i * 2 + 1]]
        epoch, elems = cspice.getelm(year, 138, lines)
        epoch_x[i] = epoch
        elems_x[0 + i * 10:9 + i * 10] = elems

    handle = cspice.spkopn(name, 'test', 0)

    first = cspice.utc2et(first)
    last = cspice.utc2et(last)

    cspice.spkw10(handle, 25544, 399, 'J2000', first, last,
                  'test segment', CONSTS, n, elems_x, epoch_x)
    cspice.spkcls(handle)

    return