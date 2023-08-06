#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 09:17:40 2018

@author: demiliu
"""
import numpy as np
from scipy.optimize import differential_evolution
import matplotlib.pyplot as plt


def abs_data(data):
    abs_array = np.abs(data)

    return abs_array


def singleexpfunc(t, params):
    exp_array = params[0] * np.exp((-1.0 / params[1]) * t)

    return exp_array


def fit_single_exp_diffev(t, data):
    a1_bounds = (0, 1)
    tau1_bounds = (0, 1000)
    bounds = [a1_bounds, tau1_bounds]
    time_array = t
    data_array = abs_data(data)

    def fit(params):
        decaymodel = singleexpfunc(time_array, params[:])
        cost = np.sum(((data_array - decaymodel) ** 2.0))
        return cost
    bestfit = differential_evolution(fit, bounds=bounds, polish=True)
    bestfit_params = bestfit.x

    def bestfit_decay(params):
        decaymodel = singleexpfunc(time_array, params[:])
        return decaymodel
    bestfit_model = bestfit_decay(bestfit_params)

    return bestfit_params, bestfit_model, data_array, time_array


def fitting_vis(df, data_nm):
    """fit peak intensity array to monoexponential,
    then visualize peak intensity overlaid with best-fit,
    height and fwhm dynamics

    Args:
        peak_dict: dictionary of peak index, height and fwhm
        data_nm: wavelength array

    """

    fit_exp = fit_single_exp_diffev(df['Time'], df['Height'])
    bf = fit_exp[1]
    bf_params = fit_exp[0]

    # add best-fit to dataframe
    # multiply by -1 because previous data
    # was taken absolute value
    df['Fit'] = -1 * bf

    # plot peak position, intensity and width over time
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8))

    ax1.plot(df['Time'], df['Height'], '.', label='Height')
    ax1.plot(df['Time'], df['Fit'], label='Mono-exponential fit')
    x_pos = int(np.array(df['Time'])[-1] * 3 / 5)
    y_pos = np.max(df['Fit'])
    plt.annotate('Tau' + ' = ' + '%.1f' %
                 (bf_params[1]) + ' ps', (x_pos, y_pos))
    ax1.set_title('Peak Dynamics', fontsize=18, fontweight='bold')
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

    return
