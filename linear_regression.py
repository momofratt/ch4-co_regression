#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 10:46:14 2021

@author: Cosimo Fratticioli
"""
import pandas as pd
import selection_functions as sel
import formatting_functions as fmt
import eval_emi_functions as evem
import config as conf
import numpy as np
from os import sys
######################################################################################
######            Read data and merge into single DataFrame                     ######
######################################################################################
CH4_frame     = fmt.read_L2_ICOS(conf.L2_ICOS_path,  conf.L2_name_prefix     + '.CH4')
CO_frame      = fmt.read_L2_ICOS(conf.L2_ICOS_path,  conf.L2_name_prefix     + '.CO')
MET_frame     = fmt.read_L2_ICOS(conf.L2_ICOS_path,  conf.L2_met_name_prefix     + '.MTO')

CH4_nrt_frame = fmt.read_L2_ICOS(conf.L2_ICOS_path,  conf.L2_nrt_name_prefix + conf.gas_inst+'.CH4')
CO_nrt_frame  = fmt.read_L2_ICOS(conf.L2_ICOS_path,  conf.L2_nrt_name_prefix + conf.gas_inst+'.CO')
MET_nrt_frame = fmt.read_L2_ICOS(conf.L2_ICOS_path,  conf.L2_nrt_met_name_prefix + conf.met_inst+'.MTO')

CH4_frame = pd.concat([CH4_frame,CH4_nrt_frame], ignore_index=True)
CO_frame = pd.concat([CO_frame,CO_nrt_frame], ignore_index=True)
MET_frame = pd.concat([MET_frame,MET_nrt_frame], ignore_index=True)

# conversion to datetime is needed since the MET files decimal date differs from the CO and CH4 ones
fmt.insert_datetime_col(CH4_frame,     3, 'Year', 'Month', 'Day', 'Hour', 'Minute')
fmt.insert_datetime_col(CO_frame,      3, 'Year', 'Month', 'Day', 'Hour', 'Minute')
fmt.insert_datetime_col(MET_frame,     3, 'Year', 'Month', 'Day', 'Hour', 'Minute')

if (conf.stat=='CMN') & (conf.years[0] ==2018):
    CH4_frame, CO_frame, MET_frame = fmt.append_2018(CH4_frame, CO_frame, MET_frame)


do_not_duplicate_cols = ['#Site', 'SamplingHeight'] # avoid duplicating these cols while merging dataframes
data_frame = pd.merge(CH4_frame , CO_frame[CO_frame.columns.difference(do_not_duplicate_cols)]  , on='DateTime', suffixes=('_ch4','_co'))
data_frame = pd.merge(data_frame, MET_frame[MET_frame.columns.difference(do_not_duplicate_cols)], on='DateTime', suffixes=('','_met'))
if conf.stat=='CMN':
    BADS_frame = fmt.read_BADS_frame()
    data_frame = pd.merge(data_frame, BADS_frame, on='DateTime', suffixes=('','_met'))
    bg_cols = ['bkg']
else:
    bg_cols = []

# add ICOS NRT data to the dataset
data_nrt_frame = pd.merge(CH4_nrt_frame, CO_nrt_frame[CO_nrt_frame.columns.difference(do_not_duplicate_cols)], on='DateTime', suffixes=('_ch4','_co'))
data_nrt_frame = pd.merge(data_nrt_frame, MET_nrt_frame[MET_nrt_frame.columns.difference(do_not_duplicate_cols)], on='DateTime', suffixes=('','_met'))

# select only valid data
flags = ['Flag_ch4', 'Flag_co', 'WD-Flag'] # flags to perform the selection
for i in range(len(flags)):
    data_frame = data_frame[(data_frame[flags[i]]!='N') & (data_frame[flags[i]]!='K')]
    data_nrt_frame = data_nrt_frame[data_nrt_frame[flags[i]]=='O']

##### Baseline section
# get baselines for ch4 and co and add them to data_frame
ch4_baseline_frame = fmt.get_baseline('ch4')
co_baseline_frame = fmt.get_baseline('co')
data_frame = data_frame.merge(ch4_baseline_frame, on='DateTime')
data_frame = data_frame.merge(co_baseline_frame, on='DateTime')

# add cols with differences between measured values and baselines to data_frame
data_frame.insert(len(data_frame.columns), 'ch4_baseline_delta', data_frame['ch4'] - data_frame['ch4_baseline'])
data_frame.insert(len(data_frame.columns), 'co_baseline_delta',  data_frame['co']  - data_frame['co_baseline'] )

data_frame['ch4_baseline_delta'] = data_frame['ch4_baseline_delta'].replace(0., np.nan) # replace zeros with 'nan'
data_frame['co_baseline_delta']  = data_frame['co_baseline_delta'].replace(0., np.nan)

# #### PLOT baseline
fig,ax=plt.subplots(1,1, figsize = (9,4))
ax.plot(data_frame['DateTime'], data_frame['ch4'] - data_frame['interp_ch4_baseline'], lw=1)
ax.plot(data_frame['DateTime'], data_frame['ch4'] - data_frame['ch4_baseline'], lw=1)
ax.set_xlim([dt.date(2020,1,1), dt.date(2020,1,30)])
ax.set_ylim([1850, 2000])
ax.grid()
fig.autofmt_xdate()

######################################################################################
######   Perform fit, plot and CH4 estimation on different selections           ######
######################################################################################

####### #######             Linear regression over absolute co and ch4 values                            ####### #######
####### ####### select this frame and comment the "delta" lines below to perform fit using absolute values #######
co_ch4_frame = data_frame[['co', 'ch4','Stdev_co','Stdev_ch4','DateTime', 'WD'] + bg_cols]
#### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### 

####### ####### Linear regression over delta (i.e. difference respect to the baseline) co and ch4 values ####### #######
####### ####### select this frame and comment the "absolute value" lines above to perform fit using delta values #######
# co_ch4_frame = data_frame[['co_baseline_delta', 'ch4_baseline_delta', 'Stdev_co','Stdev_ch4', 'DateTime', 'WD']]
# co_ch4_frame = co_ch4_frame[(co_ch4_frame['co_baseline_delta'].notna()) & (co_ch4_frame['ch4_baseline_delta'].notna())] # retain only non nan delta values

#### #### #### #### #### #### #### #### #### #### #### #### #### #### #### #### ####  
co_ch4_frame = co_ch4_frame[co_ch4_frame['co'].notna()]
co_ch4_frame = co_ch4_frame[co_ch4_frame['ch4'].notna()]

##################       monthly boxplot     ##################
evem.boxplot(co_ch4_frame, wd=None, bads_no_bkg=None)
evem.boxplot(co_ch4_frame, wd=None, bads_no_bkg=False)
evem.boxplot(co_ch4_frame, wd='310-80', bads_no_bkg=False)
evem.boxplot(co_ch4_frame, wd='310-80', bads_no_bkg=True)

evem.fit_season_emissions(co_ch4_frame, wd=None, bads_no_bkg=None)
evem.fit_season_emissions(co_ch4_frame, wd=None, bads_no_bkg=False)
evem.fit_season_emissions(co_ch4_frame, wd='310-80', bads_no_bkg=False)
evem.fit_season_emissions(co_ch4_frame, wd='310-80', bads_no_bkg=True)

evem.daily_ratio(co_ch4_frame)



######          SEASON REGRESSIONS        ###############
el.select_and_fit(co_ch4_frame, year=True, month=False, season=True, wd=None, day_night=None, plot=True, bads_no_bkg=None, robustness=True)
vem.eval_ch4_emis(co_ch4_frame, year=True, month=False, season=True, wd=None, day_night=None, region='PUY', bads_no_bkg=None, robustness=True)

######         MONTHLY REGRESSIONS       ###############
sel.select_and_fit(co_ch4_frame, year=True, month=True, season=False, wd=None    , day_night=True,  plot=True, bads_no_bkg=None, robustness=True)

evem.eval_ch4_emis(co_ch4_frame, year=True, month=True, season=False, wd=None, day_night=None, region='GER', bads_no_bkg=None, robustness=True)

# # #######         MONTHLY REGRESSIONS  WD 310-80   ###############

sel.select_and_fit(co_ch4_frame, year=True, month=True, season=False, wd='310-80', day_night=None, plot=True, bads_no_bkg=True, robustness=True)
evem.eval_ch4_emis(co_ch4_frame, year=True, month=True, season=False, wd='310-80', day_night=None, region='PO', bads_no_bkg=True, robustness=True)

################# eval emissions compact ##################

evem.eval_ch4_emi_compact(['CMN','CMN','CMN','CMN','CMN','CMN'],
                          ['PO','PO','PO','PO','PO','PO'], year=True, 
                          month=       [True,True,True,True,True,True], 
                          season=      [False,False,False,False,False,False], 
                          wd=          [None,None,'310-80','110-180',None,'310-80'], 
                          day_night=   [None,True,None,None,None,None], 
                          bads_no_bkg= [None,None,None,None,True,True], 
                          robustness = [True,True,True,True,True,True],
                          non_bkg_specie=['','','','','','co2','co2'],
                          ylims=[[0,1e6],[0,1e6],[0,1e6],[0,1e6],[0,1e6],[0,1e6]],
                          IPR=[True,True,True,True,True,True])





