# Peakaboo

[![PyPI version](https://badge.fury.io/py/PEAKABOO.svg)](https://badge.fury.io/py/PEAKABOO)
[![Build Status](https://travis-ci.org/liud16/peakaboo.svg?branch=master)](https://travis-ci.org/liud16/peakaboo)
[![Coverage Status](https://img.shields.io/coveralls/github/liud16/peakaboo/master.svg)](https://coveralls.io/github/liud16/peakaboo?branch=master)

Peakaboo is a software package for analysis of transient absorption (TA) data. It can self-consistently identify spectrally and temporally evolvin signatures of charge carriers after photoexcitation in TA data. With minimal assumption, our algorithm recovers and visualizes the spectral and kinetic information of individual populations by combining methods such as multivariate adaptive regression spline fitting and data clustering.



## Software Requirements

- Required softwares are listed in requirements.txt
- ```pip install -r requirements.txt```
- ```pip``` will check the required software



## Installation instruction

- Install from pip:
    
    ```pip install PEAKABOO```


## How to use the package

- Run package from command line:

    ``python -m peakaboo <filename>``

- Please make sure file is in the directory from which you are running peakaboo
- *Do not* add extension, you will be prompted to specify once peakaboo is initiated


### Workflow:

    - User provides data in .csv or .txt format and specifies wavelength range and time-zero
    - Reduce noise in data
    - Find peaks in data with user-specific selection criteria
    - Classify peak outputs
    - Visualize and fit peak kinetics to exponential function
    - Peak info is saved


## Run test:

- in ``tests`` directory, run ``pytest`` from command line:
    ``python -m pytest``


## License

MIT
