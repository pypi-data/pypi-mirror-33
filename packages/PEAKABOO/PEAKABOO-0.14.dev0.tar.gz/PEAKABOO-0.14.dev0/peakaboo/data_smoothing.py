import numpy as np
from pyearth import Earth
import pandas as pd


def find_nearest(array, value):
    """
    find the index of an item in an array that is closest to a given value

    Args:
        array: numpy array
        value: int or float

    Returns:
        int

    """

    idx = (np.abs(array - value)).argmin()
    return idx


# load .txt data
def load_data(data_filename, startnm, endnm, starttime):
    """
    load matrix data

    Args:
        data_filename: string

    Returns:
        data_nm: an array of wavelengths, numpy array
        data_time: an array of time-delay, numpy array
        data_z: a 2-way matrix, numpy matrix

    """
    assert isinstance(data_filename, str), 'TypeError'
    assert isinstance(startnm, float) or int, 'TypeError'
    assert isinstance(endnm, float) or int, 'TypeError'
    assert isinstance(starttime, float) or int, 'TypeError'

    data = np.genfromtxt(data_filename, delimiter='\t')
    data_nm = data[1:, 0]
    data_time = data[0, 1:]
    data_z = data[1:, 1:]

    assert starttime >= data_time[0] or data_time[-1], 'ValueError'
    assert startnm >= data_nm[0], 'ValueError'
    assert endnm <= data_nm[-1], 'ValueError'

    # trim wavelength array based on starting and ending wavlenth
    data_nm_use = data_nm[find_nearest(
        data_nm, startnm):find_nearest(data_nm, endnm)]

    # trim time array based on starting time
    data_time_use = data_time[find_nearest(data_time, starttime):]

    # trim data matrix accordingly
    data_z_use = data_z[find_nearest(data_nm, startnm):
                        find_nearest(data_nm, endnm),
                        find_nearest(data_time, starttime):]

    return data_nm_use, data_time_use, data_z_use


# load .csv data
def load_data_csv(data_filename, startnm, endnm, starttime):
    """load matrix data"""
    assert isinstance(data_filename, str), 'TypeError'
    assert isinstance(startnm, float) or int, 'TypeError'
    assert isinstance(endnm, float) or int, 'TypeError'
    assert isinstance(starttime, float) or int, 'TypeError'

    data = np.genfromtxt(data_filename, delimiter=',', skip_footer=20)
    data_nm = np.nan_to_num(data[1:, 0])  # wavelength in nm
    data_time = np.nan_to_num(data[0, 1:])
    data_z = np.nan_to_num(data[1:, 1:])

    assert starttime >= data_time[0] or data_time[-1], 'ValueError'
    assert startnm >= data_nm[0], 'ValueError'
    assert endnm <= data_nm[-1], 'ValueError'

    # trim wavelength array based on starting and ending wavlenth
    data_nm_use = data_nm[find_nearest(data_nm, startnm):
                          find_nearest(data_nm, endnm)]

    # trim time array based on starting time
    data_time_use = data_time[find_nearest(data_time, starttime):]

    # trim data matrix accordingly
    data_z_use = data_z[find_nearest(data_nm, startnm):
                        find_nearest(data_nm, endnm),
                        find_nearest(data_time, starttime):]

    return data_nm_use, data_time_use, data_z_use


def earth_smoothing(nm_array, y_array):
    """
    Smoothen noisy data using py-earth,
    based on multivariate adaptive regression spline

    Args:
        nm_array: wavelength array
        y-array: intensity array

    Returns:
        a smoothing curve from the original noise curve

    """
    # Fit an Earth model
    model = Earth(smooth=True)
    np.random.seed(42)
    model.fit(nm_array, y_array)

    # Get the predicted values and derivatives
    y_hat = model.predict(nm_array)

    return y_hat


def earth_smooth_matrix(nm_array, data_matrix):
    """
    Smoothen each time-slice in a data matrix

    Args:
        nm_array: wavelength array
        data_matrix: two-way data

    Returns:
        smooth_matx: smoothened data matrix

    """

    num_array = np.shape(data_matrix)[1]
    smooth_matx = pd.DataFrame(np.empty((len(nm_array), 1)), columns=['a'])

    for i in range(num_array):
        data_array = data_matrix[:, i]
        smooth_array = earth_smoothing(nm_array, data_array).tolist()

        # add smoothened timeslice data to the matrix
        df = pd.DataFrame(smooth_array, columns=[i])
        smooth_matx = smooth_matx.join(df)

    # drop the first columns in the matrix
    smooth_matx = smooth_matx.drop(columns='a')

    return smooth_matx
