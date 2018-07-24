#!/usr/bin/env python
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2017 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    template_namelist.py

DESCRIPTION
    Default namelists for MODELTEMPLATE post processing control
'''
import os


class TopLevel(object):
    '''Default Values for template pp namelist'''

    pp_run = False
    debug = False
    restart_directory = os.environ['DATAM']
    work_directory = os.environ['CYLC_TASK_WORK_DIR'] + '/../coupled'


class Processing(object):
    ''' Default values for template processing namelist '''

    means_cmd = 'path/to/meaning_utility args'
    create_means = False
    create_monthly_mean = False
    create_seasonal_mean = False
    create_annual_mean = False
    create_decadal_mean = False
    base_component = '10d'

    compress_netcdf = 'nccopy'
    compression_level = 0
    chunking_arguments = 'time/1,nc/1,ni/288,nj/204'

    correct_time_variables = False
    correct_time_bounds_variables = False
    time_vars = 'time'


class Archiving(object):
    '''Default Values for template archiving namelist'''

    archive_restarts = False
    archive_restart_timestamps = '06-01', '12-01'
    archive_restart_buffer = None

    archive_means = False
    means_to_archive = None
