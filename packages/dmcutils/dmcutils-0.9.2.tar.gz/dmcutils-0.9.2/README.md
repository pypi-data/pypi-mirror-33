[![Travis CI](https://travis-ci.org/scivision/dmcutils.svg?branch=master)](https://travis-ci.org/scivision/dmcutils)
[![Coverage](https://coveralls.io/repos/github/scivision/dmcutils/badge.svg?branch=master)](https://coveralls.io/github/scivision/dmcutils?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/4203c9d68d331350ce2f/maintainability)](https://codeclimate.com/github/scivision/dmcutils/maintainability)

# dmcutils


Programs used to help with the Dual-Multi-sCale (DMC) experiment.
Example of dealing with 100000 - 1 million Andor Neo spool files in a fast way.

## Installation

    python -m pip install -e .

## Functions

-   `angledist` computes angular distance between points (in degrees)
    for a pair of points with RA,decl. or az,el.


## Notes

[Install Matlab Engine](https://www.scivision.co/matlab-engine-callable-from-python-how-to-install-and-setup/)
optional, just for corrupted 2010 Solis files.

---

The Andor Solis Neo spool file format has changed at least three times.
This spool reader is known to work for the 2011-2012 versions (I don't have exact version numbers, but could find out if you need).

For 2008-Spring 2011 spool files, see the `andor_neo_spool` directory in this repo.

