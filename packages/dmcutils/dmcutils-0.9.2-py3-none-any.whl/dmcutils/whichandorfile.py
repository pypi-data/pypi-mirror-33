#!/usr/bin/env python
"""
Assuming a series of Andor Solis saved files, which one has the desired time range given:
start time, kinetic time
"""
import logging
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
from typing import Tuple, Union
from dateutil.parser import parse
from astropy.io import fits


def whichfile(firstfn: Path, treq: np.ndarray) -> Tuple[Path, Union[None, Path]]:
    """
    reads the first file in a kinetic series saved by Andor Solis to find
    which filename corresponds to a desired time

    input: firstfn FIRST file in kinetic series
    treq: single or pair of datetime to request
    """
    firstfn = Path(firstfn).expanduser()
    treq = np.atleast_1d(treq)
    assert isinstance(treq[0], datetime)

    with fits.open(str(firstfn), 'readonly') as h:
        kineticsec = h[0].header['KCT']
        framesperfile = h[0].header['NAXIS3']
        tstartseries = parse(h[0].header['FRAME'] + 'Z')  # NOTE: you must specify first file in series!

    secondsperfile = kineticsec * framesperfile

    dt = treq[0] - tstartseries
    assert dt >= timedelta(0), 'your time {} is before the first file start {}'.format(treq[0], tstartseries)
# %% start file
    startfn = getandorfn(dt, secondsperfile, firstfn)
# %% last file
    lastfn: Union[None, Path]
    if treq.size > 1:
        lastfn = getandorfn(treq[-1] - tstartseries, secondsperfile, firstfn)
    else:
        lastfn = None

    return startfn, lastfn


def getandorfn(dt: timedelta, secperfile, firstfn: Path) -> Path:
    """ generate Solis sequential FITS filename based on elapsed time"""
    fnum = dt // timedelta(seconds=secperfile)

    fn = firstfn.parent / (firstfn.stem + '_X{}.fits'.format(fnum))
    if not fn.is_file():
        raise FileNotFoundError(f'could not find {fn}')
        
    return fn


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='find which FITS file your data is in from Andor Solis')
    p.add_argument('firstfn', help='first file of kinetic series')
    p.add_argument('treq', help=' yyyy-mm-ddTHH-MM-SSZ you want', nargs='+')
    P = p.parse_args()

    treq = [parse(t) for t in P.treq]

    startfn, lastfn = whichfile(P.firstfn, treq)
    print(startfn.name)
    if lastfn:
        print(lastfn.name)
