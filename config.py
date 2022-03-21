#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 10:19:48 2021

@author: cosimo
"""

######################################################################################
######                          Parameters                                      ######
######################################################################################
L2_ICOS_path = './L2_ICOS_data/'

######################################################################
################            CIMONE              ######################
L2_name_prefix = 'ICOS_ATC_L2_L2-2021.1_CMN_8.0_CTS'
L2_nrt_name_prefix =  'ICOS_ATC_NRT_CMN_2021-02-01_2021-08-09_8.0_'
stat= 'CMN'
gas_inst = '590'
met_inst = '1156'
years=[2018, 2019, 2020]
non_bkg_specie = 'co+ch4' # specie(s) to perform non-bkg selection using BaDSfit results

######################################################################
################            LAMPEDUSA           ######################
# L2_name_prefix = 'ICOS_ATC_L2_L2-2021.1_LMP_8.0_CTS'
# L2_nrt_name_prefix =  'ICOS_ATC_NRT_LMP_2021-02-01_2021-11-28_8.0_'
# stat= 'LMP'
# years=[2020, 2021 ]
# gas_inst = '268'
# met_inst = '1042'
#bads_filenm = './BaDS_baseline/LMP_2018-2021_co2_BaDSfit_annual_selection_mar22.csv'

######################################################################
################         HOHENPEISSENBERG       ######################

# L2_name_prefix = 'ICOS_ATC_L2_L2-2021.1_HPB_50.0_CTS'
# stat= 'HPB'
# years=[2017,2018,2019,2020]
