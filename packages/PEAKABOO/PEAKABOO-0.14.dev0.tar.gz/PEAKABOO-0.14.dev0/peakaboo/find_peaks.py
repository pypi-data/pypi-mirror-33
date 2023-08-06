#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 25 06:38:05 2018

@author: demiliu
"""

import numpy as np


def indexes(y, thres=0.3, min_dist=1):
    """
    Peak detection based on a gradient-method,
    adapted from peakutils.indexes


    Args:
    y : 1D data array, numpy array
    thres : lowest intensity to call a feature a peak,
    float between 0. and 1.
    min_dist : minimum distance between two peaks, int

    Returns:
    array of peak indices, numpy array

    """
    y_raw = y
    y = [abs(k) for k in y_raw]

    if isinstance(y, np.ndarray) and np.issubdtype(
            y.dtype, np.unsignedinteger):
        raise ValueError("y must be signed")

    thres = thres * (np.max(y) - np.min(y)) + np.min(y)
    min_dist = int(min_dist)

    assert isinstance(thres, (float, int)), 'TypeError'
    assert isinstance(min_dist, (float, int)), 'TypeError'
    # compute first order difference
    dy = np.diff(y)

    # propagate left and right values successively to fill all plateau pixels
    # (0-value)
    zeros, = np.where(dy == 0)

    # check if the singal is totally flat
    if len(zeros) == len(y) - 1:
        return np.array([])

    while len(zeros):
        # add pixels 2 by 2 to propagate left and right value onto the
        # zero-value pixel
        zerosr = np.hstack([dy[1:], 0.])
        zerosl = np.hstack([0., dy[:-1]])

        # replace 0 with right value if non zero
        dy[zeros] = zerosr[zeros]
        zeros, = np.where(dy == 0)

        # replace 0 with left value if non zero
        dy[zeros] = zerosl[zeros]
        zeros, = np.where(dy == 0)

    # find the peaks by using the first order difference
    peaks = np.where((np.hstack([dy, 0.]) < 0.)
                     & (np.hstack([0., dy]) > 0.)
                     & (y > thres))[0]

    # handle multiple peaks, respecting the minimum distance
    if peaks.size > 1 and min_dist > 1:
        highest = peaks[np.argsort(y[peaks])][::-1]
        rem = np.ones(y.size, dtype=bool)
        rem[peaks] = False

        for peak in highest:
            if not rem[peak]:
                sl = slice(max(0, peak - min_dist), peak + min_dist + 1)
                rem[sl] = True
                rem[peak] = False

        peaks = np.arange(y.size)[~rem]

    return peaks
