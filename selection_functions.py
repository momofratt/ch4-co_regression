#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 11:39:17 2021

@author: cosimo
"""
######################################################################################
######            Functions for the linear_regression.py script                 ######
######################################################################################

import datetime as dt
from suntime import Sun
import numpy as np 
import lin_reg_functions as lrf
import formatting_functions as fmt
import os
import config as conf

def select_year(df, year):
    """ select one year of data
    
    Parameters
    df: DataFrame
        input dataframe 
    year: int 
        year to perform the selection
    
    Returns
    out_df:
        output dataframe
    """
    out_df = df[(df['DateTime'].dt.year==year)]
    return out_df
    
def select_month(df, year, month):
    """ select one month of data
    
    Parameters
    ----------
    df: dataframe 
    year, month: year and month to perform the selection
    
    Returns
    -------
    out_df
    """
    
    out_df = df[(df['DateTime'].dt.year==year) & (df['DateTime'].dt.month==month)]
    return out_df

def select_season(df, year, seas):
    """ select one season of data

    Parameters
    ----------
    df: dataframe 
    year, month: year and month to perform the selection

    Returns
    -------
    out_df
    """

    if seas == 'MAM':
        out_df = df[(df['DateTime'].dt.year==year) & ((df['DateTime'].dt.month==3)|(df['DateTime'].dt.month==4)|(df['DateTime'].dt.month==5))]
    if seas == 'JJA':
        out_df = df[(df['DateTime'].dt.year==year) & ((df['DateTime'].dt.month==6)|(df['DateTime'].dt.month==7)|(df['DateTime'].dt.month==8))]
    if seas == 'SON':
        out_df = df[(df['DateTime'].dt.year==year) & ((df['DateTime'].dt.month==9)|(df['DateTime'].dt.month==10)|(df['DateTime'].dt.month==11))]
    if seas == 'DJF':
        out_df = df[(df['DateTime'].dt.year==year) & (df['DateTime'].dt.month==12)]
        out_df = out_df.append(df[ (df['DateTime'].dt.year==year+1) & ((df['DateTime'].dt.month==1)|(df['DateTime'].dt.month==2))])

    return out_df


def select_wd(df, wd):
    """ select data for wind from a given wind direction
    
    Parameters
    ----------
    df: input dataframe 
    wd: str
        string that contains min and max wind directions to perform the selection. The string is formatted as 'wd_min-wd_max', 
        where wd_min and wd_max are the min and max wd to perform the selecion. NB: the angle is selected starting from wd_min 
        and going clockwise to wd_max. wd==None if no selection has to be performed
    
    Returns
    -------
    out_df: selected dataframe
    """
    if wd!=None:
        wd_min = int(wd.split('-')[0]) # split input string to get min and max wind directions
        wd_max = int(wd.split('-')[1])
        if wd_min < wd_max:
            out_df = df[(df['WD']>wd_min) & (df['WD']<wd_max)]
        else: # that is wd_min < 360 and wd_max > 360 (i.e >0)
            out_df = df[(df['WD']>wd_min) | (df['WD']<wd_max)]
        return out_df
    else:
        return df

def select_daytime(df, day):
    """
    add a bool column ('day?') to the input dataframe. Values are set to True if correspond to daytime, False otherwise

    Parameters
    ----------
    df : input dataframe
    day: select daytime (day==True) or nighttime (day==False) data. day==None to avoid data selection
    Returns
    -------
    out_frame: selected frame
    """
    if day!=None:
        lon_CMN, lat_CMN   = 10.70111, 44.19433 # coordinates of the station
        sun = Sun(lat_CMN, lon_CMN) # use suntime module to get sunrise and sustet times for each day
        day_list = [] # bool list that contains the values of the new 'day?' column 
        for datetime in df['DateTime']:
            date    = dt.date(datetime.year, datetime.month, datetime.day)
            sunrise = sun.get_sunrise_time(date).timestamp() # convert to timestamp in order to compare to datetime.timestamp(). This is done to avoid problems with the time offset that is provided by get_sunrise_time() but is not present in datetime
            sunset  = sun.get_sunset_time(date).timestamp()
            if (datetime.timestamp() > sunrise) & (datetime.timestamp() < sunset):
                day_list.append(True)
            else:
                day_list.append(False)
        df.insert(3,'day?', day_list) # insert new column in the dataframe
        if day==True:
            out_frame = df[ df['day?']==True ]
        elif day ==False:
            out_frame = df[ df['day?']==False ]
        else: # print erro message
            print('ERROR: select_daytime(df, day): wrong day value')
        del out_frame['day?'], df['day?'] # remove inserted columns
        return out_frame
    else:
        return df

def select_non_bkg(df, non_bkg):
    if non_bkg:
        #df = df[(df['co_bg']==False) & (df['ch4_bg']==False)]
        df = df[(df['bkg']==False)]
    
    #select only non bkg conditions that last for at least 2 hours
    df.insert(3, 'diff_p1', df['DateTime'].diff(periods=1))
    df.insert(4, 'diff_m1', df['DateTime'].diff(periods=-1))
    df = df[ (df['diff_p1']>dt.timedelta(hours=1)) | (df['diff_m1']<dt.timedelta(hours=-1)) ]
    
    return df

def select_and_fit(df, year, month, season, wd, day_night, plot, bads_no_bkg):
    """
    Select data in dataframe and run the fit_and_scatter_plot() function according to the input parameters
    
    Parameters
    ----------
    df : DataFrame
        dataframe to perform selection
    year, month: bool
        define if perform monthly/yearly selection on data. == None to avoid selection 
    wd: str
        define wd selecion. == None to avoid selection 
    day_night: bool
        define daytime (day_night==True) or nightime (day_night==False) selection. day_night==None to avoid selection 
    plot : bool
        plot or not the scatterplot and fit results
    bads_bkg: bool
        wether to select only non-bkg data (True) or all data (False) 

    Returns
    -------
    None
    """
    # get the name of older fit results files
    species, suff = fmt.get_species_suffix(df) 
    _, _, table_filenm = fmt.format_title_filenm(year, month, season, wd, day_night, suff, bads_no_bkg)

    if os.path.exists('./'+conf.stat+'/res_fit/'+table_filenm): # remove older fit results 
        os.remove('./'+conf.stat+'/res_fit/'+table_filenm)
    
    if month & season:
            print('ERROR: both month and season selected\n')
            os.sys.exit()
    
    if year:
        for year in conf.years:
            if month:  # if month == True performs for loop over months, otherwise performs loop over years
                if (year == 2018) & (conf.stat=='CMN'): # skip missing first months in 2018 at CMN
                    months = np.arange(5,13,1)
                else:
                    months = np.arange(1,13,1)

                for mth in months:
                    frame = select_month(df, year, mth)                    
                    frame = select_daytime(frame, day=day_night)
                    frame = select_wd(frame, wd=wd)
                    frame = select_non_bkg(frame, bads_no_bkg)
                    if len(frame) > 1:
                        lrf.fit_and_scatter_plot(frame, year=year, month=mth, wd=wd, day_night=day_night, plot=plot, non_bkg = bads_no_bkg)
            elif season:
                if (year == 2018) & (conf.stat=='CMN'): # skip missing first months in 2018 at CMN
                    seasons =['JJA','SON']
                else:
                    seasons =['DJF','MAM','JJA','SON']

                for seas in seasons:
                    
                    frame = select_season(df, year, seas)
                    frame = select_daytime(frame, day=day_night)
                    frame = select_wd(frame, wd=wd)
                    frame = select_non_bkg(frame, bads_no_bkg)
                    if len(frame) > 1:
                        lrf.fit_and_scatter_plot(frame, year=year, month=seas, wd=wd, day_night=day_night, plot=plot, non_bkg = bads_no_bkg)


            else:
                frame = select_year(df, year)
                lrf.fit_and_scatter_plot(frame, year=year, month=month, wd=wd, day_night=day_night, plot=plot, non_bkg = bads_no_bkg)
