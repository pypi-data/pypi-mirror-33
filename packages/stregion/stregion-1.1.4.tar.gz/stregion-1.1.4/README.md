# stregion

**DO NOT USE THIS PACKAGE IN YOUR PROJECT**

This is a frozen fork of `pyregion`. This repository's codebase is permanently
stuck in 2013. This repository will never be updated and therefore is not
useful except where required by old projects under https://github.com/spacetelescope
that rely on any patches made here long ago.

We have rebranded this software as `stregion` for the sole purpose of
avoiding conflicts with the existing `pyregion` package on PyPI.


If you stumbled upon this package by mistake, go ahead and check out one of the
following projects instead:


* https://github.com/astropy/regions
* https://github.com/astropy/pyregion

------------------

stregion is a python module to parse ds9 region files.
It supports ciao region files.


## FEATURES

* `ds9` and `ciao` region files.
* (physical, wcs) coordinate conversion to the image coordinate.
* convert regions to `matplotlib` patches.
* convert regions to spatial filter (i.e., generate mask images)

## LICENSE

All files (see exception below) are under MIT License. See LICENSE.

* `lib/kapteyn_celestial.py` is from the Kapteyn package
  (http://www.astro.rug.nl/software/kapteyn/). See `LICENSE_kapteyn.txt`.
