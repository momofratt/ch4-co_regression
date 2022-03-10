#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 15:11:39 2021

@author: Cosimo Fratticioli
"""
######################################################################################
######            Functions for the linear_regression.py script                 ######
######################################################################################

import matplotlib.pyplot as plt
import numpy as np
import scipy.odr as odr
from scipy.stats import linregress
from os import path
import formatting_functions as fmt
import config as conf
from math import isnan



from sklearn.linear_model import (
    LinearRegression,
    TheilSenRegressor,
    RANSACRegressor,
    HuberRegressor,
)
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline


def ortho_lin_regress(x, y, err_x, err_y):
    """
    Perform an Orthogonal Distance Regression  and Linear regression on the given data,
    
    Parameters
    ---------
    x, y: lists 
        x,y data to perform the fit
    
    Returns
    ---------
    out_odr, linreg: 
        results and statistical parameters of the orthogonal and linear regressions
        
    Uses standard ordinary least squares to estimate the starting parameters
    then uses the scipy.odr interface to the ODRPACK Fortran code to do the
    orthogonal distance calculations.
    """
    
    def f(p, x):
        """Basic linear regression 'model' for use with ODR"""
        return (p[0] * x) + p[1]

    linreg = linregress(x,y)
    mod = odr.Model(f)
    dat = odr.RealData(x, y, sx=err_x, sy=err_y)
    od  = odr.ODR(dat, mod, beta0=linreg[0:2])
    out_odr = od.run()
    
    thsen_model = make_pipeline(PolynomialFeatures(1), TheilSenRegressor(random_state=42))
    x = np.array(x)[:, np.newaxis]
    y = np.array(y)[:, np.newaxis]
    thsen_model.fit(x, y)
    #mse = mean_squared_error(thsen_model.predict(x), y)

    return out_odr, linreg, thsen_model


def fit_and_scatter_plot(df, year, month, wd, day_night, plot, non_bkg):
    """
    Perform orthogonal and linear fit on the FIRST and SECOND columns of df and returns scatter plot and best fit line

    Parameters
    ----------
    df: DataFrame
        input dataframe
    plot: bool
        enable or disable the scatter plot.
    wd: str
        string that describes the wind direction over which data have been (eventually) selected. The str format is 'min_wd-max_wd' (e.g. '20-70' for wind direction between 20 and 70 degrees)
    day_night: bool
        describes the day/night selection. True = daily selected data, False = nightime selected, None = no day/night selection
    non_bkg: bool
        wether to use all data (False) or only non-bkg data (True)
    Returns
    -------
    """


    # define columns and format titles and filenames

    species, suff = fmt.get_species_suffix(df)
    selection_string, plot_filenm, table_filenm = fmt.format_title_filenm(year, month, None,wd, day_night, suff, non_bkg)
    errors = ['Stdev_co','Stdev_ch4']


    ################ FIT #################
    ort_res, lin_res, thsen_res = ortho_lin_regress(df[species[0]], df[species[1]], df[errors[0]], df[errors[1]]) # perform orthogonal and linear regression
    poly = np.poly1d(ort_res.beta) # define fist order polynomials with the regression coefficients
    poly_lin = np.poly1d(lin_res[0:2])
    min_x, max_x = min( df[ df[species[0]].notna() ][species[0]] ), max( df[ df[species[0]].notna() ][species[0]] )
    xvals = np.arange(min_x, max_x, 1) # x array to plot the polynomials
    poly_thsen = thsen_res.predict(xvals[:, np.newaxis])


    ############## TEST FIT ROBUSTNESS THROUGH SUBSAMPLING ###################
    n_iter = 100
    fraction = 0.4
    if wd == None:
        #n_iter = 100
        fraction = 0.2

    threshold = 0.3
    monthly_check_array = np.empty(0)
    for i in range(n_iter):
        df_sub=df.sample(frac = fraction)
        ort_res_sub, lin_res_sub, thsen_res_sub = ortho_lin_regress(df_sub[species[0]], df_sub[species[1]], df_sub[errors[0]], df_sub[errors[1]])
        #monthly_check_array = np.append(monthly_check_array, ort_res_sub.beta[0]) # usa fit ortogonale
        monthly_check_array = np.append(monthly_check_array, lin_res_sub[0])
    if np.std(monthly_check_array)/np.mean(monthly_check_array) < threshold:
        robust = True
    else:
        robust = False

    ############## ############## ############## ############## ##############

    # write results on table
    if not path.exists('./'+conf.stat+'/res_fit/'+table_filenm): # write header only if the file does not already exist
        file = open('./'+conf.stat+'/res_fit/'+table_filenm, 'w')
        file.write('year month slope slope_sd red_chi2 mean_slope_sub slope_sd_sub r2 robust\n')
        file.close()
    if path.exists('./'+conf.stat+'/res_fit/'+table_filenm):
        file = open('./'+conf.stat+'/res_fit/'+table_filenm, 'r')
        for last_line in file:
            pass
        file.close()
        if (last_line[0:13] != '2020 December') | (last_line[0:7] != '2020 SON'): # append new data only if last line is different from 2020 December  WARNING: does not work for yearly data
            file = open('./'+conf.stat+'/res_fit/'+table_filenm, 'a')
            ## information about orthogonal fit (commented)
            # file.write(str(year) +' '+ fmt.get_month_str(month) +
            #             ' ' + str(round(ort_res.beta[0],2)) +  ' ' +
            #             str(round(ort_res.sd_beta[0],2)) +  ' ' +
            #             str(round(ort_res.res_var,3) ) + ' ' +
            #             str(round(np.mean(monthly_check_array),3) ) + ' ' +
            #             str(round(np.std(monthly_check_array),3) ) + ' ' +
            #             str(round(lin_res[2],3) ) + ' ' +
            #             str(robust) + '\n')
            # write linear fit results
            ## information about linear fit
            file.write(str(year) +' '+ fmt.get_month_str(month) +
                        ' ' + str(round(lin_res[0],2)) +  ' ' +
                        str(round(lin_res[4],2)) +  ' ' +
                        str(round(ort_res.res_var,3) ) + ' ' +
                        str(round(np.mean(monthly_check_array),3) ) + ' ' +
                        str(round(np.std(monthly_check_array),3) ) + ' ' +
                        str(round(lin_res[2],3) ) + ' ' +
                        str(robust) + '\n')

            file.close()

    ############## plotting ##############
    if plot:
        fig, ax=plt.subplots(1,1, figsize=(5,5))
        fig.suptitle(species[1].upper()+':'+species[0].upper()+' orthogonal and linear regression\n'+selection_string)
        ax.scatter(df[species[0]], df[species[1]], marker='o', facecolors='none', edgecolors='C'+str(year-conf.years[0]))
        ax.plot(xvals, poly(xvals), color ='r',label='orthogonal regression')
        ax.plot(xvals, poly_lin(xvals), color ='purple', label='linear regression')
        ax.plot(xvals, poly_thsen, color ='blue', label='Theil-Sen regression')
        ax.set_xlabel(species[0].upper()+' [ppb]')
        ax.set_ylabel(species[1].upper()+' [ppb]')
        ax.legend(loc='upper left')
        ax.grid()
        # add fit information:
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.7)           
        if not isnan(ort_res.beta[0] + ort_res.beta[1]  + lin_res[0] + lin_res[1]):
            f_string = '$f_{orth}(x)$ = ' +str(round(ort_res.beta[0],2))+ ' x + ' +str(round(ort_res.beta[1]))+ '\n' + '$f_{lin}(x)$ = ' +str(round(lin_res[0],2))+ ' x + ' +str(round(lin_res[1]))
            ax.text(0.55, 0.05, f_string, transform=ax.transAxes, bbox=props) 
        
        plt.savefig(plot_filenm, format='pdf')
