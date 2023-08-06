#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 16:20:47 2018

@author: demiliu
"""
from peakaboo.peak_character import find_nearest, peakchar, peak_matrix
import numpy as np
import pandas as pd


def test_find_nearest():
    array = 'string'
    value = 1
    try:
        find_nearest(array, value)
    except TypeError:
        pass
    else:
        print('TypeError not handled')


def test_peakchar():
    data_nm = 'string'
    data_z = np.zeros((5, 5))
    peak_idx = pd.DataFrame([[1, 2, 3], [1, 2, 3],
                             [1, 2, 3], [1, 2, 3],
                             [1, 2, 3]])
    try:
        peakchar(data_nm, data_z, peak_idx)
    except TypeError:
        pass
    else:
        print('TypeError not handled', 'Check peak_finding output')

    data_nm = np.random.rand(144)
    data_z = np.random.rand(144)
    peak_idx = [5, 50]
    height, fwhm = peakchar(data_nm, data_z, peak_idx)

    if isinstance(height, list):
        pass
    else:
        raise Exception('Bad type', 'Height is not np array')

    if isinstance(fwhm, np.ndarray):
        pass
    else:
        raise Exception('Bad type', 'Fwhm is not np array')


def test_peak_matrix():
    data_nm = np.random.rand(144)
    data_z = pd.DataFrame(np.random.rand(144, 700))
    threshold = 'z'
    mindist = 10
    try:
        peak_matrix(data_nm, data_z, threshold, mindist)
    except TypeError:
        pass
    else:
        print('TypeError not handled', 'Check threshold or mindist type')

    if isinstance(data_z, pd.core.frame.DataFrame):
        pass
    else:
        raise Exception('TypeError', 'Check smoothing function output type')
    return
