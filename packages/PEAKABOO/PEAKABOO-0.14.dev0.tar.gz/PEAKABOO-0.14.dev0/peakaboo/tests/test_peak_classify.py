from peakaboo.peak_classify import data_grouping
from peakaboo.peak_classify import cluster_classifier
import numpy as np
import pandas as pd


def test_data_grouping():
    index_df = np.zeros((2, 2))
    height_df = pd.DataFrame([1, 2, 3])
    fwhm_df = pd.DataFrame([4, 5, 6])
    threshold = 1
    try:
        data_grouping(index_df, height_df, fwhm_df, threshold)
    except AttributeError:
        pass
    else:
        print('Incorrect data type passed', 'Check peak_finding_master output')

    index_df = pd.DataFrame()
    height_df = pd.DataFrame([1, 2, 3])
    fwhm_df = pd.DataFrame([4, 5, 6])
    threshold = 1
    t = data_grouping(index_df, height_df, fwhm_df, threshold)
    assert len(t) == 0, "Index data frame is empty"

    index_df = pd.DataFrame([1, 2, 3])
    height_df = pd.DataFrame()
    fwhm_df = pd.DataFrame([4, 5, 6])
    threshold = 1
    try:
        data_grouping(index_df, height_df, fwhm_df, threshold)
    except KeyError:
        pass
    else:
        print('Height data frame empty', 'Check peak_finding_master output')

    index_df = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    height_df = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    fwhm_df = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    threshold = 10
    t = data_grouping(index_df, height_df, fwhm_df, threshold)
    assert len(t) == 0, "Threshold is too high"


def test_cluster_classifier():
    index_df = pd.DataFrame([[1, 1, 5], [1, 2, 10], [1, 2, 6]])
    corrected_output = pd.DataFrame()
    try:
        cluster_classifier(index_df, corrected_output)
    except ValueError:
        pass
    else:
        print('ValueError not handled for empty input dataframe.')

    index_df = pd.DataFrame([[1, 1, 5], [1, 2, 10], [1, 2, 6]])
    corrected_output = pd.DataFrame([[1, 1, 1, 1], [1, 2, 1, 1], [5, 5, 5, 1],
                                     [1, 1, 2, 2], [2, 2, 1, 2], [10, 7, 6, 2],
                                     [1, 2, 2, 3], [2, 1, 3, 3], [6, 6, 6, 3]])
    t = cluster_classifier(index_df, corrected_output)
    assert len(t) == 0, \
        "Did not truncate sparse peaks"

    index_df = pd.DataFrame([[1, 1], [1, 2], [1, 2]])
    corrected_output = pd.DataFrame([[1, 1, 1, 1], [1, 2, 1, 1], [5, 5, 5, 1],
                                     [1, 1, 2, 2], [2, 2, 1, 2], [10, 7, 6, 2],
                                     [1, 2, 2, 3], [2, 1, 3, 3], [6, 6, 6, 3],
                                     [1, 2, 2, 3], [2, 1, 3, 3], [6, 6, 6, 3],
                                     [1, 2, 2, 3], [2, 1, 3, 3], [6, 6, 6, 3],
                                     [1, 2, 2, 3], [2, 1, 3, 3], [6, 6, 6, 3],
                                     [1, 2, 2, 3], [2, 1, 3, 3],
                                     [100, 100, 6, 3]])
    t = cluster_classifier(index_df, corrected_output)
    assert len(t) == 1, \
        "Did not properly classify peaks"
    assert len(t['peak_0']) or len(t['peak_1']) == 20, \
        "Dictionary did not populate properly"
