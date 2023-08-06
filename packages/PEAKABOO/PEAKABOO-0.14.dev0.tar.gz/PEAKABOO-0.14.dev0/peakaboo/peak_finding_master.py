#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 08:59:44 2018

@author: demiliu
"""

from peakaboo.peak_character import peak_matrix


def findpeaks(nm, time, z):
    """fine peaks using user input as parameters

    Args:
        nm: wavelength, numpy array
        time: time, numpy array
        z: data, numpy array

    Returns:
        idx, height, fwhm: peak index, height and full-width half-max in pandas
        dataframe

    """

    peaks_ok = 'N'
    while peaks_ok == 'N':

        print('Please enter the parameters for finding peaks')
        default_parameter = input('Default parameters? Y/N ')

        assert default_parameter == str('Y') or (
            'N'), ('Response to "default parameters?" can only be Y or N.')

        if default_parameter == 'Y':
            # default parameters
            threshold = 0
            min_dist = 0

            # find peaks
            idx, height, fwhm = peak_matrix(nm, z, threshold, min_dist)

            # print result
            print('Peak position in index')
            print(idx)
            print('Peak height')
            print(height)
            print('Peak fwhm in wavelength (nm)')
            print(fwhm)
            peaks_ok = input('Are you satisfied with peak-finding? Y/N ')

            # make sure only Y or N is entered
            if peaks_ok != 'Y' or 'N':
                print(
                    """Please enter Y or N only for
                    "Are you satisfied with peak-finding?" """)
                peaks_ok = input('Are you satisfied with peak-finding? Y/N ')

            elif peaks_ok == 'Y' or 'N':
                peaks_ok = peaks_ok
            # check previous if's are guarding agains wrong input
            assert peaks_ok == 'Y' or 'N', ('Enter only Y or N')

        elif default_parameter == 'N':
            # Ask user for threshold and minimum distance between two peaks
            threshold = input('Threshold (0 to 100): ')
            min_dist = int(input('Minimum distance between peaks (integer): '))

            assert isinstance(
                threshold, int) or float, ('threshold must be int or float')

            # find peaks
            idx, height, fwhm = peak_matrix(nm, z, threshold, min_dist)

            # print result
            print('Peak position in index')
            print(idx)
            print('Peak height')
            print(height)
            print('Peak fwhm in wavelength (nm)')
            print(fwhm)
            peaks_ok = input('Are you satisfied with peak-finding? Y/N ')

            # make sure only Y or N is entered
            if peaks_ok != 'Y' or 'N':
                print(
                    """Please enter Y or N only for
                    "Are you satisfied with peak-finding?" """)
                peaks_ok = input('Are you satisfied with peak-finding? Y/N ')

            elif peaks_ok == 'Y' or 'N':
                peaks_ok = peaks_ok
            # check previous if's are guarding agains wrong input
            assert peaks_ok == 'Y' or 'N', ('Enter only Y or N')

        # Make sure only 'Y' or 'N' is acceptable
        elif default_parameter != 'Y' or 'N':
            print('Please enter Y or N only for "Default parameters?"')
            peaks_ok = 'N'
        # check previous if's are guarding agains wrong input
        assert default_parameter == 'Y' or 'N', 'Wrong input'

    return idx, height, fwhm
