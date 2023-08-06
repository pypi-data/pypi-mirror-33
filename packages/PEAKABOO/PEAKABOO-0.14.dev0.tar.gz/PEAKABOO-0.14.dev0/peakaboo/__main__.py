# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import peakaboo.data_smoothing as data_smoothing
from peakaboo.peak_finding_master import findpeaks
from peakaboo.peak_classify_master import classify
import peakaboo.smoothing_visualize as smoothing_visualize
import sys


if __name__ == '__main__':
    """main function to run functions based on user interaction"""

    print('--- Peakaboo: Peak Detection in Transient Absorption Spectra ---')
    print('Hello! Welcome to Peakaboo!')

    # file-type
    print('Please enter filetype (.csv or .txt)')
    filetype = input('Filetype: ')

    assert filetype == '.csv' or '.txt', ('Only .csv or .txt is compatible')

    # filename
    filename = sys.argv[1]

    # wavelength range
    print('Please choose cut-on wavelength (only number, in nm)')
    cuton_nm = int(input('Cut-on wavelength: '))

    print('Please choose cut-off wavelength (only number, in nm)')
    cutoff_nm = int(input('Cut-off wavelength: '))

    # time range
    print('Please enter true time zero (only number, in ps)')
    timezero = int(input('Time zero at: '))

    # load data
    if filetype == '.txt':
        nm, time, z = data_smoothing.load_data(
            filename + '.txt', cuton_nm, cutoff_nm, timezero)

    elif filetype == '.csv':
        nm, time, z = data_smoothing.load_data_csv(
            filename + '.csv', cuton_nm, cutoff_nm, timezero)

    # smooth data and visualize
    print('--- Reducing noise in data... ---')

    # reduce noise
    z_smooth = smoothing_visualize.smoothing(nm, time, z)

    # identify and characterize peaks
    print('Next step is to find peaks in each time-slice.')
    idx, height, fwhm = findpeaks(nm, time, z_smooth)

    print('Peak dynamics are shown below. .csv files are saved.')
    # classify peaks
    peak_dict = classify(nm, idx, height, fwhm)

    print('Thanks for using Peakaboo!')
