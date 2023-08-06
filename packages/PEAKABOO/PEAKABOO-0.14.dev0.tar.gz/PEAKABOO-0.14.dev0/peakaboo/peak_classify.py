import pandas as pd
from sklearn.cluster import KMeans


def data_grouping(index_df, height_df, fwhm_df, threshold):
    peak_list = []

    for i in range(index_df.shape[0]):
        for j in range(index_df.shape[1]):
            peak_list.append(
                [index_df.loc[i, j], height_df.loc[i, j],
                 fwhm_df.loc[i, j], i])

    all_points = pd.DataFrame(peak_list,
                              columns=['Position', 'Height', 'Width', 'Time'])
    fill_na = all_points.fillna(value=0)
    corrected_output = fill_na.drop(
        fill_na[abs(fill_na.Height) < threshold].index)
    corrected_output = corrected_output.reset_index(drop=True)

    return corrected_output


def cluster_classifier(index_df, corrected_output):
    found_peak = index_df.shape[1]
    cluster = KMeans(n_clusters=found_peak).fit(corrected_output.iloc[:, :-2])
    cluster_dict = {}

    for i in range(found_peak):
        cluster_dict['peak_%s' % i] = []

    for j in range(corrected_output.shape[0]):
        peak = cluster.predict([corrected_output.values[j, :-2]])
        for k in range(found_peak):
            if (peak == k):
                cluster_dict['peak_%s' % k].append(corrected_output.values[j])

    peak_dict = {k: v for k, v in cluster_dict.items() if len(v) >= 20}
    return peak_dict
