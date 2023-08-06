import numpy as np
import pandas as pd
import peakaboo.find_peaks as findpeak


def find_nearest(array, value):
    idx = (np.abs(array - value)).argmin()
    return idx


def peakchar(data_nm, data_z_array, peak_index):
    """
    find the peak height and width

    Args:
        data_nm: wavelength array, numpy array
        data_z_array: data array
        peak_index: index of the peaks identified

    Returns:
        height: peak intensity, numpy array
        fwhm: widths pf peaks defined as full-width half-max, numpy array

    """
    num_peaks = len(peak_index)

    # array of peak height
    height = [data_z_array[idx] for idx in peak_index]

    # array of peak width
    half_height = [ht / 2 for ht in height]

    fwhm_idx_1 = np.empty_like(half_height)
    fwhm_idx_2 = np.empty_like(fwhm_idx_1)
    fwhm_nm_1 = np.empty_like(fwhm_idx_1)
    fwhm_nm_2 = np.empty_like(fwhm_idx_1)

    for i in range(num_peaks):
        # find the index and nm corresponding to half of the peak intensity
        # on the left side of the peak
        if i == 0:
            fwhm_idx_1[i] = find_nearest(
                data_z_array[0:peak_index[i]], half_height[i])
        else:
            fwhm_idx_1[i] = find_nearest(
                data_z_array[peak_index[i - 1]:peak_index[i]],
                half_height[i]) + peak_index[i - 1]

        fwhm_nm_1[i] = data_nm[int(fwhm_idx_1[i])]

        # find the index and nm corresponding to half of the peak intensity
        # on the right side of the peak
        fwhm_idx_2[i] = find_nearest(
            data_z_array[peak_index[i]:], half_height[i]) + peak_index[i]
        fwhm_nm_2[i] = data_nm[int(fwhm_idx_2[i])]

    # calculate fwhm as the difference between the index/nm's on the left and
    # right side of the peak
    fwhm = fwhm_nm_2 - fwhm_nm_1

    return height, fwhm


def convert_to_nm(nm, matrix):
    """convert index to nm

    Args:
        nm: wavelength array
        matrix: index matrix

    Returns:
        nm_matrix: matrix in nm
    """

    nm_matrix = np.empty_like(matrix)
    matrix_nonan = np.nan_to_num(matrix)
    print(np.shape(matrix_nonan))
    for i in range(np.shape(matrix_nonan)[1]):
        nm_array = nm_matrix[:, i]
        for j in range(np.shape(matrix_nonan)[0]):
            nm_array[j] = nm[int(matrix_nonan[j, i])]

    return nm_matrix


def peak_matrix(nm_array, data_matrix, threshold, mindist):
    """
    find peaks in a data matrix
    and calculate the height and width of the peaks

    Args:
        nm_array: wavelength array
        data_matrix: two-way matrix
        threshold: threshold of normalized peak intensity to be identified
            as a peak, float between 0. and 1.
        mindist: minimum distance between two peaks, int

    Returns:
        three matrice that contains arrays of peak indices,
        peak heights and peak fwhm of each time-slice

    """

    peak_idx_matx = []
    peak_height_matx = []
    peak_fwhm_matx = []

    num_timeslice = np.shape(data_matrix)[1]

    for i in range(num_timeslice):
        data_timeslice = data_matrix.values[:, i]

        peak_idx = findpeak.indexes(
            data_timeslice, threshold, mindist).tolist()
        peak_idx_matx.append(peak_idx)

        peak_height, peak_fwhm = peakchar(nm_array, data_timeslice, peak_idx)

        peak_height_matx.append(peak_height)
        peak_fwhm_matx.append(peak_fwhm)

        # convert index to nm
        peak_idx_nm = peak_idx_matx
        peak_fwhm_nm = peak_fwhm_matx

        # transfer to dataframe
        peak_idx_df = pd.DataFrame(peak_idx_nm)
        peak_height_df = pd.DataFrame(peak_height_matx)
        peak_fwhm_df = pd.DataFrame(peak_fwhm_nm)

    return peak_idx_df, peak_height_df, peak_fwhm_df
