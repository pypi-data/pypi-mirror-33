----------------------------------------     tle2spk     ----------------------------------------

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