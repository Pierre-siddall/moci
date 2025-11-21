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
    um_def.py

DESCRIPTION
    Definition of the environment variables required for a UM model
    run
'''

UM_ENVIRONMENT_VARS_INITIAL = {
    'UM_ATM_NPROCX': {'desc': 'Number of UM processors in the X direction'},
    'UM_ATM_NPROCY': {'desc': 'Number of UM processors in the Y direction'},
    'VN': {'desc': 'UM version'},
    'UMDIR': {},
    'ATMOS_EXEC': {},
    'ATMOS_LINK': {'default_val': 'atmos.exe'},
    'DR_HOOK': {'default_val': '0'},
    'DR_HOOK_OPT': {'default_val': 'noself'},
    'PRINT_STATUS': {'default_val': 'PrStatus_Normal'},
    'UM_THREAD_LEVEL': {'default_val': 'MULTIPLE'},
    'HISTORY': {'default_val': 'atmos.xhist'},
    'STASHMASTER': {'default_val': ''},
    'STASHMSTR': {'default_val': ''},
    'SHARED_NLIST': {'default_val': 'SHARED'},
    'FLUME_IOS_NPROC': {'default_val': '0'},
    'HOUSEKEEP': {'default_val': 'hkfile'},
    'STASHC': {'default_val': 'STASHC'},
    'ATMOSCNTL': {'default_val': 'ATMOSCNTL'},
    'IDEALISE': {'default_val': 'IDEALISE'},
    'IOSCNTL': {'default_val': 'IOSCNTL'},
    'ATMOS_STDOUT_FILE': {'default_val': 'pe_output/atmos.fort6.pe'},
    'ROSE_LAUNCHER_PREOPTS_UM': {'default_val': 'unset',
                                 'triggers': [
                                     [lambda my_val: my_val == 'unset',
                                      ['ATMOS_NODES', 'OMPTHR_ATM',
                                       'HYPERTHREADS']]]},
    'ATMOS_NODES': {},
    'OMPTHR_ATM': {},
    'HYPERTHREADS': {}}

UM_ENVIRONMENT_VARS_FINAL = {
    'NPROC': {},
    'STDOUT_FILE': {'desc': 'Path to the UM standard out file'},
    'ATMOS_KEEP_MPP_STDOUT': {'default_val': 'false'}}
