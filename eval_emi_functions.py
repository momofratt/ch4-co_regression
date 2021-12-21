#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 11:46:41 2021

@author: cosimo
"""
######################################################################################
######            Functions for the linear_regression.py script                 ######
######################################################################################

import matplotlib.pyplot as plt
import pandas as pd
import formatting_functions as fmt
from numpy import arange
import config as conf

def eval_ch4_emis(df, year, month, wd, day_night, region):
    """
    Evaluate CH4 emission using CO emissions and the fit results
    
    Parameters
    ----------
    year, month: bool
        define if yearly and month selection has been performed (True/False)
    wd: str
        string with wind directions (e.g. '20-70' for wd between 20 and 70 degrees). wd=None if no selection has been performed
    day_night: bool
        daytime (day==True) or nightime selection (day==False). day==None if no selection has been performed
    region: str
        region name to evaluate emissions ('ER'=Emilia Romagna, 'TOS'=Toscana)
    Returns
    ----
    None
    """
    co_emission_file  = './res_emission_selection/predicted_'+region+'_CO_yearly_emi.txt'
    ch4_emission_file = './res_emission_selection/predicted_'+region+'_CH4_yearly_emi.txt'
    species, suff = fmt.get_species_suffix(df)
    
    _,_,fit_table_nm = fmt.format_title_filenm(year=year, month=month, wd=wd, day_night=day_night, suff=suff)
    print('\nDATA AND PARAMETERS FOR CH4 ESTIMATION')
    print('fit result file = ' + fit_table_nm)
    fit_res_file = './'+conf.stat+'/res_fit/' + fit_table_nm
    plot_nm_suffix = fit_table_nm[11:(len(fit_table_nm)-4)]
    
    GWP = 25 # Global warming potential of greenhouse gases over 100-year
    Mch4 = 16.043 # methane molecular weight
    Mco = 28.010 # CO molecular weight
    emi_co_frame = pd.read_csv(co_emission_file, sep=' ')
    fit_frame = pd.read_csv(fit_res_file, sep=' ')
    years = [2018,2019,2020]
    ch4_emi = []
    print('year avg_slope')
    for year in years:
        avg_slope = fit_frame[(fit_frame['year']==year) & (fit_frame['slope']>0.)]['slope'].mean()
        print(year, round(avg_slope,2))
        ch4_emi.append( avg_slope * emi_co_frame[emi_co_frame['year']==year]['emi[t]'] * Mch4 / Mco )
    
    emi_ch4_frame = pd.read_csv(ch4_emission_file, sep=' ')
    fig, ax = plt.subplots(1,1, figsize = (9,5))
    fig.suptitle('EDGAR measured and predicted emissions for CH$_4$ plus CO-estimated emissions for region '+region+'\nPerformed selections:' + plot_nm_suffix.replace('_',' '))
    ax.errorbar(emi_ch4_frame['year'], emi_ch4_frame['emi[t]'], emi_ch4_frame['emi_err[t]'], fmt='.', elinewidth=1, capsize=3)
    ax.scatter(years, ch4_emi, c='C1')
    
    ax.set_xlabel('years')
    ax.set_ylim(0,max(emi_ch4_frame['emi[t]']+emi_ch4_frame['emi_err[t]'])*1.05)
    ax.set_ylabel('CH$_4$ total emission [t]')
    ax.grid()
    fig.savefig('./'+conf.stat+'/plot_estimated_emissions/CH4_CO_'+region+'_estimated_emissions'+plot_nm_suffix+'.pdf', format = 'pdf')
    
    print('output plot: CH4_CO_estimated_emissions'+plot_nm_suffix+'.pdf')
    fig1, ax1 = plt.subplots(1,1, figsize = (9,5))
    fig1.suptitle('Monthly mean slope from linear fit on CH$_4$ and CO data\nPerformed selections:' + plot_nm_suffix.replace('_',' '))
    mean_slope=[]
    mean_slope_r2=[]
    months = arange(1,13,1)
    for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August','September','October','November','December']:
        mean_slope.append(fit_frame[fit_frame['month']==month]['slope'].mean())
        #mean_slope_r2.append(fit_frame[(fit_frame['month']==month) & (fit_frame['r2']>0.6)]['slope'].mean())
    
    ax1.plot(months,mean_slope, marker='.', ls='-')
    #ax1.plot(months,mean_slope_r2, marker='.', ls='-', markersize=10,label='r$^2$>0.6')
    ax1.set_xticks(months)
    ax1.set_xticklabels(['jan','feb','mar','apr','may','jun','jul','aug','sept','oct','nov','dec'])
    ax1.grid()
    ax1.legend()
    fig1.savefig('./'+conf.stat+'/plot_estimated_emissions/CH4:CO_slope'+plot_nm_suffix+'.pdf', format = 'pdf')
    
    
def eval_ch4_monthly_emis(df, year, month, wd, day_night, region):
    """
    Evaluate CH4 emission using CO emissions and the fit results
    
    Parameters
    ----------
    year, month: bool
        define if yearly and month selection has been performed (True/False)
    wd: str
        string with wind directions (e.g. '20-70' for wd between 20 and 70 degrees). wd=None if no selection has been performed
    day_night: bool
        daytime (day==True) or nightime selection (day==False). day==None if no selection has been performed
    region: str
        region name to evaluate emissions ('ER'=Emilia Romagna, 'TOS'=Toscana)
    Returns
    ----
    None
    """
    co_emission_file  = './res_emission_selection/predicted_'+region+'_CO_monthly_emi.txt'
    ch4_emission_file = './res_emission_selection/predicted_'+region+'_CH4_monthly_emi.txt'
    species, suff = fmt.get_species_suffix(df)
    
    _,_,fit_table_nm = fmt.format_title_filenm(year=year, month=month, wd=wd, day_night=day_night, suff=suff)
    print('\nDATA AND PARAMETERS FOR CH4 ESTIMATION')
    print('fit result file = ' + fit_table_nm)
    
    fit_res_file = './'+conf.stat+'/res_fit/' + fit_table_nm
    plot_nm_suffix = fit_table_nm[11:(len(fit_table_nm)-4)]
    
    GWP = 25 # Global warming potential of greenhouse gases over 100-year
    Mch4 = 16.043 # methane molecular weight
    Mco = 28.010 # CO molecular weight
    emi_co_frame = pd.read_csv(co_emission_file, sep=' ')
    emi_ch4_frame = pd.read_csv(ch4_emission_file, sep=' ')
    fit_frame    = pd.read_csv(fit_res_file, sep=' ')
    years = [2018,2019,2020]
    print('year avg_slope')
    ch4_emi   = []
    date_list = []
    ch4_emi_meas = []
    slope_list = []
    for year in years:
        month_number = 1
        for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August','September','October','November','December']:
            
            monthly_slope    = (fit_frame[(fit_frame['year']==year) & 
                                      (fit_frame['month']==month)]['slope'].tolist()) # convert from pd.Series to list
            monthly_emi_co   = (emi_co_frame[(emi_co_frame['year']==year) & 
                                      (emi_co_frame['month']==month)]['emi[t]'].tolist())
            monthly_emi_ch4  = (emi_ch4_frame[(emi_ch4_frame['year']==year) & 
                                      (emi_ch4_frame['month']==month)]['emi[t]'].tolist())
            
            if (len(monthly_slope)>0) & (len(monthly_emi_co)>0): # check wether the monthly slope and emission data exist
                monthly_slope=monthly_slope[0]
                monthly_emi_co=monthly_emi_co[0]
                date_list.append(str(year)+'-'+str(month_number)+'-1')
                monthly_ch4 = monthly_slope * monthly_emi_co * Mch4 / Mco
                ch4_emi.append( monthly_ch4 )
                ch4_emi_meas.append(monthly_emi_ch4)
                slope_list.append(monthly_slope)
            month_number = month_number+1
#    date_list = [pd.to_datetime(date) for date in date_list]
   
    fig, ax = plt.subplots(1,1, figsize = (9,5))
    fig.suptitle('EDGAR measured and predicted emissions for CH$_4$ plus CO-estimated emissions for region '+region+'\nPerformed selections:' + plot_nm_suffix.replace('_',' '))
    #ax.errorbar(emi_ch4_frame['year'], emi_ch4_frame['emi[t]'], emi_ch4_frame['emi_err[t]'], fmt='.', elinewidth=1, capsize=3)
    ax.plot(date_list, ch4_emi_meas, c='C0', label ='$CH_4$ EDGAR emission')
    ax.plot(date_list, ch4_emi, c='C1', label ='$CH_4$ estimated emission')    
    fig.autofmt_xdate(rotation = 45)
    
    ax.set_xlabel('years')
    ax.set_ylabel('CH$_4$ total emission [t]')
    ax.grid()
    ax.axvline('2019-1-1', c='black')
    ax.axvline('2020-1-1', c='black')
    ax.legend(loc='lower left')
    ax.set_ylim(bottom=0)
 
    ax2=ax.twinx()
    ax2.plot(date_list, slope_list, c='C2', label = 'CH4:CO coeff')
    ax2.legend(loc='lower right')
    ax2.set_ylabel('CH4:CO coefficient [-]')
    
    fig.savefig('./'+conf.stat+'/plot_estimated_emissions/CH4_CO_'+region+'_monthly_estimated_emissions'+plot_nm_suffix+'.pdf', format = 'pdf')
    
    print('output plot: CH4_CO_'+region+'_estimated_emissions'+plot_nm_suffix+'.pdf')

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    