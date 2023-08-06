from peakaboo.feature_visualizer import visualize
import numpy as np


def test_visualize():
    peak0 = np.random.rand(20, 4)
    peak1 = np.random.rand(20, 4)
    peak_dict = 'not a dict'
    data_nm = np.arange(1, 21, 1)
    try:
        visualize(peak_dict, data_nm)
    except TypeError:
        pass
    else:
        print('TypeError not handled', 'input it not dict')

    peak0 = np.array([[1, 2, 3, 1], [1, 2, 3, 2],
                      [1, 2, 3, 2], [1, 2, 3, 3],
                      [1, 2, 3, 4]])
    peak1 = np.array([[1, 2, 3, 1], [1, 2, 3, 2],
                      [1, 2, 3, 3], [1, 2, 3, 4]])
    peak_dict = {'peak_0': peak0, 'peak_1': peak1}
    data_nm = np.arange(1, 5, 1)
    t = visualize(peak_dict, data_nm)
    assert len(peak_dict) == 2, "Incorrect shape of peak_dict"
    assert t.shape[0] == 4, "DataFrame not constructed properly"
