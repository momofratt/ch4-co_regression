#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 11:41:45 2021

@author: cosimo
"""
######################################################################################
######            Functions for the linear_regression.py script                 ######
######################################################################################

import pandas as pd
import datetime as dt
import config as conf
def get_month_str(month_number):
    """ get month string from a given month number """
    if not type(month_number)==str: #if month is a string containing the season name, return only the string (e.g. DJF, MAM etc)
        if month_number != False: # return empty string if month=='None'
            months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September','October', 'November', 'December']
            return months[month_number-1]
        else:
            return ''
    else:
        return month_number

def read_L2_ICOS(file_path, file_name):
    """ read L2 ICOS data returning a dataframe """
    file = open(file_path+file_name, 'r')
    for i in range(5): 
        line = file.readline() # read the 5th line to get the header lines number
    head_nlines = int(line.split(' ')[3]) # get the number of header lines
    file.close()
    out_frame = pd.read_csv(file_path+file_name, sep=';', skiprows = head_nlines-1)
    return out_frame

def get_baseline(spec):
    """ 
    read baseline for a given spec from data file 
    
    Parameters
    ---------
    spec: str
        chem specie to extract the baselin. 'co' or 'ch4'
        
    Returns
    out_frame: DataFrame
        frame containing the datetime and the baseline columns
    ---------
    """    
    bsl_col_name = spec+'_cmn_mm' # name of the baseline column
    df = pd.read_csv('./BaDS_baseline/2018-2021_co2_BaDSfit_annual_selection_var_intermedie_5_5_5_flag5.csv', sep = ',', usecols = ['date', bsl_col_name])
    df.insert(1,'DateTime', pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')) # add datetime column
    del df['date']  # remove old date column
    df = df[df['DateTime'] < dt.datetime(2021,1,1,0,0,0)] # remove data from 2021
    df = df.rename(columns={bsl_col_name:spec+'_baseline'}) # rename baseline column

    return df

def read_BADS_frame(filenm):
    bkg_cols = ['co_bg2', 'ch4_bg2'] # name of the background column
    df = pd.read_csv(filenm, sep = ',', usecols = ['date'] + bkg_cols, parse_dates = {'DateTime' : ['date']}, na_values='NA')    
    df = df[df['DateTime'] < dt.datetime(2021,1,1,0,0,0)] # remove data from 2021
    df.insert(3, 'ch4_bg', False)
    df.insert(4, 'co_bg', False)
    df.loc[ df['co_bg2'] >0 , 'co_bg'] = True
    df.loc[ df['ch4_bg2']>0 , 'ch4_bg']= True
    
    return df[['DateTime', 'co_bg', 'ch4_bg']]     


def insert_datetime_col(df, pos,Y,M,D,h,m):
    """ 
    Insert a datetime column in a dataframe and removes the old year, month, day, hour and min columns 
    
    Parameters
    ---------
    df: DataFrame
        input dataframe
    pos: int
        position where to insert the DateTime column
    Y,M,D,h,m: int
        names of the Year, Month, Day, hour and minutes columns
    
    Returns
    ---------
    """
    df.insert(pos, 'DateTime', pd.to_datetime(df[[Y,M,D,h,m]]) )
    del(df[Y], df[M], df[D], df[h], df[m] )
    
def format_title_filenm(year, month, wd, day_night, suff, non_bkg):
    """
    create string where are reported the performed selections (used in the scatterplot titles) and the 
    filenames for the results of the performed selection

    Parameters
    ----------
    year, month : int
        year and month of the performed selection. year==None if no year selection has been performed. month==False if no month selection has been performed
    wd: str
        string with wind direction selection informations (format: 'wd_min-wd_max' e.g. '20-70') 
    day_night: bool
        daynight selection. ==True for day selection, ==False for night selection, ==None if no selection has been performed
    suff : str
        suffix for file and plot names.
    Returns
    -------
    selection_string, plot_filenm, table_filenm: str
        descriptive strings defining the scatterplot title (selection_string) and filenames for the scatterplot and fit results table
    """

    if day_night==True: # define day_night_str string according to the day_night bool value
        day_night_str='day'
    elif day_night==False:
        day_night_str='night'
    elif day_night == None:
        day_night_str=''

    stat=conf.stat
    selection_string = ''
    selection_filenm = ''
    dir_nm = ''
    table_filenm = 'fit_results'
    if suff!='':
        table_filenm=table_filenm+'_'+suff

    if year != None:
        selection_string = selection_string + str(year) + ', '
        selection_filenm = selection_filenm + '_' + str(year)
        dir_nm = dir_nm +stat+'/'+ str(year)+'/'
    if (month != False) | (type(month)==str):
        selection_string = selection_string + get_month_str(month) + ', '
        selection_filenm = selection_filenm + '_' + str(month)
        if (type(month)==str):
            table_filenm = table_filenm +'_season'
        else:
            table_filenm = table_filenm +'_monthly'
    if wd != None:
        selection_string = selection_string + 'WD ' + wd + '°, '
        selection_filenm = selection_filenm + '_WD' + wd
        table_filenm = table_filenm + '_WD' + wd 
        dir_nm = dir_nm + '/WD' + wd +'/'
    if day_night_str != '': #day_night_str == '' if no selection has been performed
        selection_string = selection_string + day_night_str + 'time, '
        selection_filenm = selection_filenm + '_' + day_night_str
        table_filenm = table_filenm + '_' + day_night_str 
        dir_nm = dir_nm + day_night_str +'/'
    if non_bkg:
        selection_filenm = selection_filenm + '_non-bkg'
        table_filenm = table_filenm + '_non-bkg'

    table_filenm = table_filenm +'.txt'
    plot_filenm  = dir_nm+'scatter_fit_'+suff+selection_filenm+'.pdf'

    return selection_string, plot_filenm, table_filenm

def get_species_suffix(df):
    """
     Generate string suffix for file and plot names. The suffix is equal to the last word of the 'co' column name, where words are separated by '_'. 
     e.g. 'co_delta'->suff=='delta', 'co'->suff=='', 'co_delta_pippo'->suff=='pippo'

    Parameters
    ----------
    species : str list
        columns names to perform the fit.
    Returns
    -------
    suff : str
        suffix for file and plot names
    """
    species = df.columns[[0,1]] # get columns names
    spec=species[0].split('_')  # take name of the first column (i.e. the 'co' column)
    suff=''
    for sp in spec:  # define suff. It is used to define the file and plot names (see fmt.format_title_filenm() documentation)
        if (sp!='co') & (sp!='ch4'):
            suff=sp
    
    return species, suff
