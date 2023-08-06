from peakaboo.peak_classify import data_grouping, cluster_classifier
from peakaboo.feature_visualizer import visualize


def classify(data_nm, index_df, height_df, fwhm_df):
    classify_ok = 'N'
    while classify_ok == 'N':
        threshold = input
        print('Please enter the threshold for peak classification')
        default_parameter = input('Default parameters? Y/N ')

        assert default_parameter == str('Y') or (
            'N'), ('Response to "default parameters?" can only be Y or N.')

        if default_parameter == 'Y':
            threshold = 0.001
            corrected_output = data_grouping(
                index_df, height_df, fwhm_df, threshold)
            corrected_output.describe()
            peak_dict = cluster_classifier(index_df, corrected_output)
            print(str(len(peak_dict)) + ' peaks are classified.')

            visualize(peak_dict, data_nm)
            classify_ok = input(
                'Are you satisfied with peak classification? Y/N ')

            # make sure only Y or N is entered
            if classify_ok != 'Y' or 'N':
                print("""Please enter Y or N only
                      for "Are you satisfied with
                      peak classification?" """)
                classify_ok = input(
                    'Are you satisfied with peak classification? Y/N ')

            elif classify_ok == 'Y' or 'N':
                classify_ok = classify_ok
            # check previous if's are guarding agains wrong input
            assert classify_ok == 'Y' or 'N', ('Enter only Y or N')

        elif default_parameter == 'N':
            threshold = int(
                input("""Threshold
                      (smaller than absolute value of the
                       max / min signal): """))
            corrected_output = data_grouping(
                index_df, height_df, fwhm_df, threshold)
            corrected_output.describe()
            peak_dict = cluster_classifier(index_df, corrected_output)
            print(str(len(peak_dict)) + ' peaks are classified.')

            visualize(peak_dict, data_nm)
            classify_ok = input(
                'Are you satisfied with peak classification? Y/N ')

            # make sure only Y or N is entered
            if classify_ok != 'Y' or 'N':
                print("""Please enter Y or
                      N only for "Are you satisfied
                      with peak classification?" """)
                classify_ok = input(
                    'Are you satisfied with peak classification? Y/N ')

            elif classify_ok == 'Y' or 'N':
                classify_ok = classify_ok
            # check previous if's are guarding agains wrong input
            assert classify_ok == 'Y' or 'N', ('Enter only Y or N')

        # Make sure only 'Y' or 'N' is acceptable
        elif default_parameter != 'Y' or 'N':
            print('Please enter Y or N only for "Default parameters?"')
            classify_ok = 'N'
        # check previous if's are guarding agains wrong input
        assert default_parameter == 'Y' or 'N', 'Wrong input'

    return peak_dict
