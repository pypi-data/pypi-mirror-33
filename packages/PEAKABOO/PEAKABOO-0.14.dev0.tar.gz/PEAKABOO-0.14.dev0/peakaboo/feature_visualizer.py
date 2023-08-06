import matplotlib.pyplot as plt
import pandas as pd


def save_df(df, filename):
    """save peak info to .csv file

    Args:
        df: panda dataframe
        filename: string

    """

    assert isinstance(filename, str), 'Filename needs to be str'
    assert isinstance(df, pd.core.frame.DataFrame), \
        'Filetype needs to be pandas DataFrame'

    # save dataframs as csv
    df.to_csv(
        filename,
        sep=',',
        columns=[
            'Position',
            'Height',
            'Width',
            'Time'])

    return


def visualize(peak_dict, data_nm):
    """visualize peak intensity, height and fwhm dynamics
    save peak info into .csv file

    Args:
        peak_dict: dictionary of peak index, height and fwhm
        data_nm: wavelength array

    """

    nm = pd.DataFrame(data_nm)
    for i in range(len(peak_dict)):
        # convert index to nm
        nm_list = []
        df = pd.DataFrame(peak_dict['peak_%s' % i],
                          columns=['Position', 'Height', 'Width', 'Time'])
        df = df.drop_duplicates(subset='Time')
        df = df.reset_index(drop=True)
        for j in df['Position']:
            nm_list.append(nm.loc[j].values[0])

        return df

        df['Position'] = nm_list
        # plot peak position, intensity and width over time
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8))

        ax1.plot(df['Time'], df['Height'], '.')
        ax1.set_title(
            'Peak %s Dynamics' %
            (i + 1), fontsize=18, fontweight='bold')
        ax1.set_ylabel('Intensity', fontsize=18, fontweight='bold')
        ax1.grid()

        ax2.plot(df['Time'], df['Position'], '.')
        ax2.set_ylabel('Position', fontsize=18, fontweight='bold')
        ax2.grid()

        ax3.plot(df['Time'], df['Width'], '.')
        ax3.set_ylabel('Width', fontsize=18, fontweight='bold')
        ax3.set_xlabel('Time', fontsize=18, fontweight='bold')
        ax3.grid()

        plt.show()

        filename = 'peak_%s' % i + '.csv'
        save_df(df, filename)

    return
