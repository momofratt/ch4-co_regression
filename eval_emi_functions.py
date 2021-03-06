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
import selection_functions as sel
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn
import matplotlib.ticker as mticker
from matplotlib import rcParams, rcParamsDefault
import numpy as np
from scipy.optimize import curve_fit as cf
import lin_reg_functions as lrf
import datetime as dt

def get_ch4_emis_list(region, fit_frame, robustness, season, custom_years='', IPR=False):
    """
    Get list with ch4 emission values
    Parameters:
    -------
    custom_years: list
        list of int containing the years to analyze. The default is ''. If default then uses the variable years that is defined in the config file, otherwise uses custom_years
        for the analysis
    Returns
    -------
    None.
    """
    if IPR:
        co_emission_file  = './res_emission_selection/predicted_'+region+'_ISPRA_CO_yearly_emi.txt'
    else:
        co_emission_file  = './res_emission_selection/predicted_'+region+'_CO_yearly_emi.txt'
    
    GWP = 25 # Global warming potential of greenhouse gases over 100-year
    Mch4 = 16.043 # methane molecular weight
    Mco = 28.010 # CO molecular weight
    emi_co_frame = pd.read_csv(co_emission_file, sep=' ')
    if custom_years!='':
        years=custom_years
    else:
        years = conf.years
        
    ch4_emi = []
    print('year avg_slope')
    for year in years:
        #avg_slope = fit_frame[(fit_frame['year']==year)]['slope'].mean()
        #avg_slope = fit_frame[(fit_frame['year']==year) & (fit_frame['robust']==True)]['slope'].mean() # use only robust months
        
        if robustness:
            if not season:
                avg_slope = fit_frame[(fit_frame['year']==year) & (fit_frame['robust']==True) & (fit_frame['r2']>0.6)]['slope'].mean() # use only robust months
            else:
                avg_slope = fit_frame[(fit_frame['year']==year) & (fit_frame['robust']==True) & (fit_frame['r2']>0.6)]['slope'].mean() # use only robust months
        else: # should consider only seasonal fit with r2>0.6? In case you could loose one over 4 season each year!
            if not season:
                avg_slope = fit_frame[(fit_frame['year']==year) ]['slope'].mean()
                #avg_slope = fit_frame[(fit_frame['year']==year) & (fit_frame['r2']>0.6)]['slope'].mean()
            else:
                avg_slope = fit_frame[(fit_frame['year']==year) ]['slope'].mean() 
                #avg_slope = fit_frame[(fit_frame['year']==year) & (fit_frame['r2']>0.6)]['slope'].mean() 
        print(year, round(avg_slope,2))
        ch4_emi.append( avg_slope * (emi_co_frame[emi_co_frame['year']==year]['emi[t]']).iat[0] * Mch4 / Mco )
        
    return ch4_emi

def eval_ch4_emis(df, year, month, season, wd, day_night, region, bads_no_bkg, robustness):
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

    species, suff = fmt.get_species_suffix(df)
    
    if month:
        _,_,fit_table_nm = fmt.format_title_filenm(year=year, month=month, season=None,wd=wd, day_night=day_night, suff=suff, non_bkg=bads_no_bkg, robust=robustness)
    if season:
        _,_,fit_table_nm = fmt.format_title_filenm(year=year, month=season, season=season, wd=wd, day_night=day_night, suff=suff, non_bkg=bads_no_bkg, robust=robustness)
    
    print('\nDATA AND PARAMETERS FOR CH4 ESTIMATION')
    print('fit result file = ' + fit_table_nm)
    
    fit_res_file = './'+conf.stat+'/res_fit/' + fit_table_nm
    fit_frame = pd.read_csv(fit_res_file, sep=' ')

    plot_nm_suffix = fit_table_nm[11:(len(fit_table_nm)-4)]
    years = conf.years

    ch4_emi = get_ch4_emis_list(region, fit_frame, robustness, season)
    
    ch4_emission_file = './res_emission_selection/predicted_'+region+'_CH4_yearly_emi.txt'
    emi_ch4_frame = pd.read_csv(ch4_emission_file, sep=' ')
    
    # plot
    
    fig, ax = plt.subplots(1,1, figsize = (9,5))
    fig.suptitle('EDGAR measured and predicted emissions for CH$_4$ plus CO-estimated emissions for region '+region+'\nPerformed selections:' + plot_nm_suffix.replace('_',' '))
    ax.errorbar(emi_ch4_frame['year'], emi_ch4_frame['emi[t]'], emi_ch4_frame['emi_err[t]'], fmt='.', elinewidth=1, capsize=3)
    ax.scatter(years, ch4_emi, c='C1')
    ax.set_xlabel('years')
    ax.set_ylim(0,max(emi_ch4_frame['emi[t]']+emi_ch4_frame['emi_err[t]'])*1.05)
    ax.set_ylabel('CH$_4$ total emission [t]')
    ax.grid()
    fig.savefig('./'+conf.stat+'/plot_estimated_emissions/CH4_CO_'+region+'_estimated_emissions'+plot_nm_suffix+'.pdf', format = 'pdf')
    if month:
        print('output plot: CH4_CO_estimated_emissions'+plot_nm_suffix+'.pdf')
        fig1, ax1 = plt.subplots(1,1, figsize = (9,5))
        fig1.suptitle('Monthly mean slope from linear fit on CH$_4$ and CO data at '+conf.stat+'\nPerformed selections:' + plot_nm_suffix.replace('_',' '))
        mean_slope=[]
        mean_slope_weak=[]
        months = arange(1,13,1)
        for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August','September','October','November','December']:
            mean_slope.append(fit_frame[(fit_frame['month']==month) & (fit_frame['robust']==True) & (fit_frame['r2']>0.6)]['slope'].mean())
            mean_slope_weak.append(fit_frame[(fit_frame['month']==month)]['slope'].mean())
        
        ax1.plot(months,mean_slope, marker='.', ls='-', label='robust data', markersize=15)
        ax1.plot(months,mean_slope_weak, marker='.', ls='-',label='all data')
        ax1.set_xticks(months)
        ax1.set_xticklabels(['jan','feb','mar','apr','may','jun','jul','aug','sept','oct','nov','dec'])
        ax1.grid()
        ax1.legend()
        fig1.savefig('./'+conf.stat+'/plot_estimated_emissions/CH4:CO_slope'+plot_nm_suffix+'.pdf', format = 'pdf')
        
    
def eval_ch4_monthly_emis(df, year, month, wd, day_night, region, bads_no_bkg, robustness):
    """
    Evaluate CH4 emission on a monthly base using CO emissions and the fit results
    
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
    
    _,_,fit_table_nm = fmt.format_title_filenm(year=year, month=month, season=None, wd=wd, day_night=day_night, suff=suff, non_bkg=bads_no_bkg, robust=robustness)
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
    years = conf.years
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
    for year in conf.years:
	    ax.axvline(str(year)+'-1-1', c='black')
    ax.legend(loc='lower left')
    ax.set_ylim(bottom=0)
 
    ax2=ax.twinx()
    ax2.plot(date_list, slope_list, c='C2', label = 'CH4:CO coeff')
    ax2.legend(loc='lower right')
    ax2.set_ylabel('CH4:CO coefficient [-]')
    
    fig.savefig('./'+conf.stat+'/plot_estimated_emissions/CH4_CO_'+region+'_monthly_estimated_emissions'+plot_nm_suffix+'.pdf', format = 'pdf')
    
    print('output plot: CH4_CO_'+region+'_estimated_emissions'+plot_nm_suffix+'.pdf')

    
def boxplot(df, wd=None, bads_no_bkg=None):
    """
    create boxplot of monthly CH4, CO and CH4/CO values

    Parameters
    ----------
    df : DataFrame
        input dataframe.
    wd : str
        wind direction selection (e.g. 310-80). The default is None.
    bads_no_bkg : bool
        select between non-bkg (True), bkg (False) and all (None) conditions. The default is None.

    Returns
    -------
    None.

    """
    # df = df[['DateTime','co','ch4','WD','bkg']]
    df = sel.select_wd(df, wd)
    if (bads_no_bkg!=None) & (conf.stat=='CMN'):
       df = sel.select_non_bkg(df,bads_no_bkg) 
    df=df.set_index('DateTime')
    df = df[df['ch4']<4000]
    df.insert(3,'ch4_co', df['ch4']/df['co'])
    df=df.resample('1d').mean()
    df.index = df.index.date - pd.offsets.MonthBegin(1) # riporta tutto al primo giorno del mese
    df.insert(1,'month',df.index.strftime('%Y-%m')) # insert month column for the boxplot
    
    plt.style.use('seaborn-white')
    plt.rc('font', size=30) #controls default text size

    fig,ax = plt.subplots(3,1, figsize=(20,20))
    cols = ['ch4','co','ch4_co']
    colors = ['#70a1c2', '#aab16b', '#a17a8d']
    labels = ['CH$_4$ [ppb]', 'CO [ppb]', 'CH$_4$/CO [-]']
    myLocator = mticker.MultipleLocator(3)
    mylocator = mticker.MultipleLocator(1)

    for i in range(len(cols)):
        seaborn.boxplot(ax=ax[i],x='month', y = cols[i], data=df, color=colors[i], showfliers=True) 
        #seaborn.swarmplot(ax=ax[i],x='month', y = cols[i], data=df, color='.25') 

        ax[i].grid(which='both') 
        ax[i].set_ylabel(labels[i])
        ax[i].xaxis.set_major_locator(myLocator)
        ax[i].xaxis.set_minor_locator(mylocator)

    ax[2].set_xlabel('')       
    fig.autofmt_xdate(rotation=45)
    
    
    title = 'Monthly CH$_4$ and CO Concentrations and CH$_4$/CO Ratio at '+conf.stat+'\n'
    filename_str=''
    if wd!=None:
        title = title +'WD = '+wd
        filename_str=filename_str+'wd'+wd+'_'
    if (bads_no_bkg==True) & (conf.stat=='CMN'):
        title = title + '  during non-bkg conditions'
        filename_str=filename_str+'non-bkg'

    if (bads_no_bkg==False) & (conf.stat=='CMN'):
        title = title + '  during bkg conditions'
        filename_str=filename_str+'bkg'

    fig.subplots_adjust(hspace=0.1)
    fig.suptitle(title, fontsize=30)
    plt.savefig('./'+conf.stat+'/boxplot_'+conf.stat+'_'+filename_str+'.pdf', format = 'pdf')   
    rcParams.update(rcParamsDefault)

def fit_season_emissions(df, wd=None, bads_no_bkg=None):
    """
    Provide a plot with the mean seasonal cycle over the analyzed years plus results from a sinusoidal fit.
    Parameters
    ----------
    df : DataFrame
        input dataframe.
    wd : str
        wind direction selection (e.g. 310-80). The default is None.
    bads_no_bkg : bool
        select between non-bkg (True), bkg (False) and all (None) conditions. The default is None.
    Returns
    -------
    None
    """
    # select WD and bkg
    df = sel.select_wd(df, wd)
    if (bads_no_bkg!=None) & (conf.stat=='CMN'):
       df = sel.select_non_bkg(df,bads_no_bkg) 
    df=df.set_index('DateTime')
    df = df[df['ch4']<4000]
    df.insert(3,'ch4_co', df['ch4']/df['co'])
    
    df = df[(df.index.year >= conf.years[0]) & (df.index.year <= conf.years[-1])] # use only selected years (avoid eventual residual months that are present in the dataset)    
    
    mean_co   = []
    mean_ch4  = []
    mean_ratio= []
    df = df.resample('1d').mean().resample('1m').mean()
    months = np.arange(1,13)
    for i in months:
        mean_co.append(df[df.index.month==i]['co'].mean())
        mean_ch4.append(df[df.index.month==i]['ch4'].mean())
        mean_ratio.append(df[df.index.month==i]['ch4'].mean()/df[df.index.month==i]['co'].mean())
    
    
    # fit
    def sin_fun(x,a,b,c):
        return a*np.sin(b*x)+c
    p_opt = [[]for i in range(3)]
    p_cov = [[]for i in range(3)]

    i=0
    for ydata in [mean_co, mean_ch4,mean_ratio]:
        p_opt[i],p_cov[i]=cf(sin_fun,months,ydata, p0=(10, 0.5, 100))
        #print(p_opt[i])
        i=i+1
       
    # plot results
    
    fig,ax=plt.subplots(3,1, figsize=(7,7))
    point_size=30
    ax[0].scatter(months, mean_co, color='C0', s=point_size)
    ax[0].set_ylim(0.8*min(mean_co), 1.2*max(mean_co))
    ax[0].set_ylabel('CO [ppb]')
    ax[0].plot(months,sin_fun(months,*p_opt[0]), c='C0')
    
    ax[1].scatter(months, mean_ch4, color='C1', s=point_size)
    ax[1].set_ylim(0.99*min(mean_ch4), 1.01*max(mean_ch4))
    ax[1].set_ylabel('CH$_4$ [ppb]')
    ax[1].plot(months,sin_fun(months,*p_opt[1]), c='C1')

    ax[2].scatter(months, mean_ratio, color='C2', s=point_size)
    ax[2].set_ylim(0.8*min(mean_ratio), 1.2*max(mean_ratio))
    ax[2].set_ylabel('CH$_4$/CO [-]')
    ax[2].plot(months,sin_fun(months,*p_opt[2]), c='C2')

    xlabels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug','Sep','Oct','Nov','Dec']
    
    for axis in ax:
        axis.set_xticks(months)
        axis.grid()
    ax[2].set_xticklabels(xlabels)
    fig.autofmt_xdate(rotation=45)
    
    title = 'Monthly mean CH$_4$ and CO Concentrations and CH$_4$/CO Ratio at '+conf.stat+'\nover the period '+str(conf.years[0])+'-'+str(conf.years[-1])
    filename_str=''
    if wd!=None:
        title = title +'WD = '+wd
        filename_str=filename_str+'wd'+wd+'_'
    if (bads_no_bkg==True) & (conf.stat=='CMN'):
        title = title + '  during non-bkg conditions'
        filename_str=filename_str+'non-bkg'

    if (bads_no_bkg==False) & (conf.stat=='CMN'):
        title = title + '  during bkg conditions'
        filename_str=filename_str+'bkg'
    fig.suptitle(title)
    plt.savefig('./'+conf.stat+'/fit_'+conf.stat+'_'+filename_str+'.png')   
        


    
    
def eval_ch4_emi_compact(stations, regions, year, month, season, wd, day_night, bads_no_bkg, robustness, non_bkg_specie, ylims, IPR):
    
    stations_dict = {
        'CMN':{
            'years':[2018,2019],
            },
        'LMP':{
            'years':[2020],
            },
        'PUY':{
            'years':[2017,2018,2019,2020,2021],
            },
        'JFJ':{
            'years':[2017,2018,2019,2020,2021],
            },
        'HPB':{
            'years':[2017,2018,2019,2020,2021],
            },
        'OPE':{
            'years':[2017,2018,2019,2020,2021],
            }
        }
        
    plt.style.use('ggplot')
    fig, ax = plt.subplots(1,len(stations), figsize = (3*len(stations),5))
   
    for (stat, region, i) in zip(stations,regions, np.arange(0,len(stations))):
        
        if month[i]:
            _,_,fit_table_nm = fmt.format_title_filenm(year=year, month=month[i], season=None,wd=wd[i], day_night=day_night[i], suff='', non_bkg=bads_no_bkg[i], robust=robustness[i], custom_station=stat, non_bkg_specie=non_bkg_specie[i])
        if season[i]:
            _,_,fit_table_nm = fmt.format_title_filenm(year=year, month=season[i], season=season[i], wd=wd[i], day_night=day_night[i], suff='', non_bkg=bads_no_bkg[i], robust=robustness[i], custom_station=stat, non_bkg_specie=non_bkg_specie[i])
        
        print('\nDATA AND PARAMETERS FOR CH4 ESTIMATION')
        print('fit result file = ' + fit_table_nm)
        
        fit_res_file = './'+stat+'/res_fit/' + fit_table_nm
        fit_frame = pd.read_csv(fit_res_file, sep=' ')
        plot_nm_suffix = fit_table_nm[11:(len(fit_table_nm)-4)]
        years = stations_dict[stat]['years']
    
        ch4_emi     = get_ch4_emis_list(region, fit_frame, robustness[i], season[i], custom_years=stations_dict[stat]['years'])
        ch4_emi_IPR = get_ch4_emis_list(region, fit_frame, robustness[i], season[i], custom_years=[2018,2019],IPR=True)

        # read ch4 emissions from EDGAR inventories
        ch4_emission_file = './res_emission_selection/predicted_'+region+'_CH4_yearly_emi.txt'
        emi_ch4_frame = pd.read_csv(ch4_emission_file, sep=' ')
        emi_ch4_frame = emi_ch4_frame[emi_ch4_frame['year']>=years[0]]
        
        # read co emissions from EDGAR inventories
        co_emission_file = './res_emission_selection/predicted_'+region+'_CO_yearly_emi.txt'
        emi_co_frame = pd.read_csv(co_emission_file, sep=' ')
        emi_co_frame = emi_co_frame[emi_co_frame['year']>=years[0]]
        
        if stat=='CMN':
            emi_ch4_frame = emi_ch4_frame[emi_ch4_frame['year']<2020]
            emi_co_frame  = emi_co_frame[emi_co_frame['year']<2020]

            # read ch4 emissions from ISPRA inventories
            ch4_emission_file_IPR  = './res_emission_selection/predicted_'+region+'_ISPRA_CH4_yearly_emi.txt'
            emi_ch4_frame_ISPRA = pd.read_csv(ch4_emission_file_IPR, sep=' ')

            # read co emissions from ISPRA inventories
            co_emission_file_IPR  = './res_emission_selection/predicted_'+region+'_ISPRA_CO_yearly_emi.txt'
            emi_co_frame_ISPRA = pd.read_csv(co_emission_file_IPR, sep=' ')
            
            emi_ch4_frame_ISPRA = emi_ch4_frame_ISPRA[emi_ch4_frame_ISPRA['year']<2020]
            emi_co_frame_ISPRA  = emi_co_frame_ISPRA[ emi_co_frame_ISPRA['year']<2020]
            emi_ch4_frame_ISPRA = emi_ch4_frame_ISPRA[emi_ch4_frame_ISPRA['year']>=years[0]]
            emi_co_frame_ISPRA  = emi_co_frame_ISPRA[ emi_co_frame_ISPRA['year']>=years[0]]

        estimated_errorbar = ( np.array(ch4_emi)/emi_co_frame['emi[t]'].to_numpy() * emi_co_frame['emi_err[t]'].to_numpy() ).tolist()

        if stat=='CMN':
            emi_co_frame= emi_co_frame[emi_co_frame['year']<2020]
        # plot
        if IPR[i] == True:
            offset=0.2
        else:
            offset=0

        ax[i].errorbar(emi_ch4_frame['year'      ]-offset, 
                       emi_ch4_frame['emi[t]'    ], 
                       emi_ch4_frame['emi_err[t]'], 
                       fmt='o', elinewidth=5, capsize=8, markersize=8,color='#8e2e41', 
                       barsabove=True, label='EDGAR CH$_4$')
        
        ax[i].errorbar(np.array(years)-offset, 
                      ch4_emi[-len(years):len(ch4_emi)], 
                      estimated_errorbar, 
                      fmt='o', elinewidth=2, capsize=8, markersize=8,color='#eb5f63', 
                      barsabove=False, label='estimated EDGAR CH$_4$')
        
        #ax[i].scatter(np.array(years)-offset, ch4_emi[-len(years):len(ch4_emi)], c='red', label='estimated CH$_4$ EDGAR')
        
        if IPR[i] == True:
            
            # read IPR co emission from inventories
            
            estimated_errorbar_IPR = ( np.array(ch4_emi_IPR)/emi_co_frame_ISPRA['emi[t]'].to_numpy() *emi_co_frame_ISPRA['emi[t]'].to_numpy()* 0.4 ).tolist()

            ax[i].errorbar(emi_ch4_frame_ISPRA['year'      ]+offset, 
                        emi_ch4_frame_ISPRA['emi[t]'    ], 
                        emi_ch4_frame_ISPRA['emi[t]'    ]*0.4, 
                        fmt='o', elinewidth=5, capsize=8, markersize=8, color='#38761d', 
                        barsabove=True, label='ISPRA CH$_4$')
        
            ax[i].errorbar([2018+offset,2019+offset], 
                          ch4_emi_IPR, 
                          estimated_errorbar_IPR, 
                          fmt='o', elinewidth=2, capsize=8, markersize=8,color='#2dfc92', 
                          barsabove=False, label='estimated ISPRA CH$_4$')
            
            
            #ax[i].scatter([2018+offset,2019+offset], ch4_emi_IPR, c='C10',marker='^', label='estimated CH$_4$ ISPRA')

        
        ax[i].grid(True)
        ax[i].set_xlabel('years')
        ax[i].set_xlim(years[0]-1, years[-1]+1)
        ax[i].set_ylim(ylims[i][0],ylims[i][1])
        ax[i].ticklabel_format(style='sci', scilimits=(-3,4))
        ax[i].set_xticks(years)
        ax_title = '' 
        
        if day_night[i]==True:
            ax_title ='daytime'
        
        if wd[i]!=None:
            ax_title=ax_title+ 'WD:' +str(wd[i])
        if bads_no_bkg[i] == True:
            ax_title = ax_title+' non-bkg'
        elif bads_no_bkg[i] == False:
            ax_title = ax_title+' bkg'

        ax[i].set_title(ax_title, fontdict={'fontsize': 10})
        
        # props = dict(boxstyle='round', facecolor='wheat', alpha=0.7)           
        # ax[i].text(0.5, 0.05, regions[i], horizontalalignment='center',
        #            verticalalignment='center', transform=ax[i].transAxes, bbox=props) 
        
    ax[0].set_ylabel('CH$_4$ total emission [t]')
    ax[-1].legend(loc = 'upper right',bbox_to_anchor=(2.1, 1))
    fig.autofmt_xdate()
    fig.suptitle('EDGAR measured and predicted emissions for CH$_4$ plus CO-estimated emissions at different stations')
    fig.subplots_adjust(wspace=0.3, hspace=0.4)
    plt.tight_layout()
    fig.savefig('./results_all_stat/CH4_CO_compact_estimated_emissions'+plot_nm_suffix+'.pdf', format = 'pdf',bbox_inches='tight')

            
        
def daily_ratio(df):
    days = df['DateTime'].dt.date.drop_duplicates()
    coeff_frame = pd.DataFrame({'DateTime':[],'coeff':[],'intercept':[]})

    for today in days[1:-1]:
        yesterday = today-dt.timedelta(days=1)
        df_daily = df[(df['DateTime'].dt.date == today) | (df['DateTime'].dt.date == yesterday)].copy()

        df_daytime   =  df_daily[(df_daily['DateTime'].dt.date==today) & (df_daily['DateTime'].dt.hour>=8) & (df_daily['DateTime'].dt.hour<20)] # daily time of day
        df_nighttime =  df_daily[((df_daily['DateTime'].dt.date==yesterday) & (df_daily['DateTime'].dt.hour>=20) & (df_daily['DateTime'].dt.hour<24) )| 
                                 ((df_daily['DateTime'].dt.date==today) &(df_daily['DateTime'].dt.hour>=0) & (df_daily['DateTime'].dt.hour<8))]
        for frame in [df_nighttime, df_daytime]:
            if (len(df_daytime)>10) & (len(df_nighttime)>10):
                _, _, thsen_res = lrf.ortho_lin_regress(frame['co'], frame['ch4'], frame['Stdev_co'], frame['Stdev_ch4'])

                coeff_frame.loc[len(coeff_frame.index)] = [frame['DateTime'].iat[0], 
                                                               thsen_res.coef_[0], thsen_res.intercept_]
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
