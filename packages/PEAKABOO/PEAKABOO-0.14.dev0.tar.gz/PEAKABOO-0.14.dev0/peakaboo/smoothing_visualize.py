#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 10:27:03 2018

@author: demiliu
"""
from peakaboo.data_smoothing import earth_smooth_matrix
import numpy as np
import matplotlib.pyplot as plt


def twodcontourplot(tadata_nm, tadata_timedelay, tadata_z_corr):
    """
    make contour plot

    Args:
        tadata_nm: wavelength array
        tadata_timedelay: time delay array
        tadata_z_corr: matrix of z values

    """

    timedelayi, nmi = np.meshgrid(tadata_timedelay, tadata_nm)

    # find the maximum and minimum
    # these are used for color bar
    z_min = np.amin(np.amin(tadata_z_corr, axis=1))
    z_max = np.amax(np.amax(tadata_z_corr, axis=1))

    return [nmi, timedelayi, z_min, z_max]


def smoothing(nm, time, z):
    """Reduce noise in data, then visualize data before and
    after smoothening in contour plot.

    Args:
        nm: wavelength array, numpy array
        time: time array, numpy array
        z: data matric, numpy array

    Returns:
        z_smooth: data after reducing noise, numpy array
    """

    # smoothing data
    z_smooth = earth_smooth_matrix(nm, z)

    # check data shape doesn't change
    assert np.shape(z_smooth) == np.shape(z), \
        'ShapeError'

    # contour plot of original data BEFORE smoothing
    original_contour = twodcontourplot(nm, time, z)
    nm_contour, time_contour, min_contour, max_contour = original_contour[
        0], original_contour[1], original_contour[2], original_contour[3]

    fig, (ax1, ax2) = plt.subplots(1, 2, dpi=100)
    ax1.set_title('Raw data', fontsize=20, fontweight='bold')
    ax1.set_xlabel('Wavelength (nm)', fontsize=20, fontweight='bold')
    ax1.set_ylabel('Time delay (ps)', fontsize=20, fontweight='bold')
    plt.xlabel('Wavelength (nm)', fontsize=20, fontweight='bold')
    ax1.pcolormesh(
        nm_contour,
        time_contour,
        z,
        cmap='PiYG',
        vmin=min_contour /
        2.5,
        vmax=max_contour /
        10)

    # contour plot of data AFTER smoothing
    smooth_contour = twodcontourplot(nm, time, z_smooth)
    nm_contour, time_contour, min_contour, max_contour = smooth_contour[
        0], smooth_contour[1], smooth_contour[2], smooth_contour[3]

    ax2.set_title('Smooth data', fontsize=20, fontweight='bold')
    ax2.pcolormesh(
        nm_contour,
        time_contour,
        z_smooth,
        cmap='PiYG',
        vmin=min_contour / 2.5,
        vmax=max_contour / 10)
    plt.tight_layout(pad=0.25, h_pad=None, w_pad=None, rect=None)
    plt.show()

    return z_smooth
