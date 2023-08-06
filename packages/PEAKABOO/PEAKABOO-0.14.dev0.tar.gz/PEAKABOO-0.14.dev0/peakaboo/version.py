from os.path import join as pjoin

# Format expected by setup.py and doc/source/conf.py: string of form "X.Y.Z"
_version_major = 0
_version_minor = 14
_version_micro = ''  # use '' for first of series, number for 1 and above
_version_extra = 'dev'


# Construct full version string from these.
_ver = [_version_major, _version_minor]
if _version_micro:
    _ver.append(_version_micro)
if _version_extra:
    _ver.append(_version_extra)

__version__ = '.'.join(map(str, _ver))

CLASSIFIERS = ["Development Status :: 3 - Alpha",
               "Environment :: Console",
               "Intended Audience :: Science/Research",
               "License :: OSI Approved :: MIT License",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Scientific/Engineering"]


description = "Peakaboo: Feature Analysis in Transient Absorption Spectroscopy"

long_description = """

PEAKABOO
========
We have designed an open-source package to identify self-consistent spectrally
and temporally evolving signatures of charge carriers after photoexcitation in
transient absorption (TA) data. With minimal assumption, our algorithm
recovers and visualizes the spectral and kinetics information of
the individual population by combining methods such as multivariate
adaptive regression spline fitting anddata clustering.

To get started using these components in your own software, please go to the
repository README: https://github.com/liud16/peakaboo/README.md

License
=======
``PEAKABOO`` is licensed under the terms of the MIT license. See the file
"LICENSE" for information on the history of this software, terms & conditions
for usage, and a DISCLAIMER OF ALL WARRANTIES.
"""

NAME = "PEAKABOO"
MAINTAINER = "demi_ian_jing"
MAINTAINER_EMAIL = "demiliu@uw.edu"
DESCRIPTION = description
LONG_DESCRIPTION = long_description
URL = "http://github.com/liud16/peakaboo"
DOWNLOAD_URL = ""
LICENSE = "MIT"
AUTHOR = "DEMI_IAN_JING"
AUTHOR_EMAIL = "demiliu@uw.edu"
PLATFORMS = "OS Independent"
MAJOR = _version_major
MINOR = _version_minor
MICRO = _version_micro
VERSION = __version__
PACKAGE_DATA = {'PEAKABOO': [pjoin('data', '*')]}
REQUIRES = ["numpy", "scipy", "peakutils", "sklearn", "pandas", "matplotlib"]
