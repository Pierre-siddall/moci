#!/usr/bin/env python3
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2021-2025 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    cice_def.py

DESCRIPTION
    Definition of the environment variables required for a CICE model
    run
'''

CICE_ENVIRONMENT_VARS_INITIAL = {
    'CICE_GRID': {'desc': 'The input grid file'},
    'CICE_KMT': {'desc': 'The land sea mask file'},
    'CICE_NPROC': {},
    'CICE_START': {'default_val': False},
    'SHARED_FNAME': {'default_val': 'SHARED'},
    'ATM_DATA_DIR': {'default_val': 'unknown_atm_data_dir'},
    'OCN_DATA_DIR': {'default_val': 'unknown_ocn_data_dir'},
    'CICE_RESTART': {'default_val': 'ice.restart_file'},
    'CICE_OCEAN_DATA': {'default_val': ''},
    'CICE_ATMOS_DATA': {'default_val': ''},
    'TASK_START_TIME': {'default_val': 'unavaliable'},
    }
