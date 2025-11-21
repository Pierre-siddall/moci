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
    mct_def.py

DESCRIPTION
    Definition of the environment variables required for using OASIS3-MCT in
    a coupled model run
'''

MCT_ENVIRONMENT_VARS_COMMON = {
    'CPMIP_ANALYSIS' : {'default_val': 'False'}}

MCT_ENVIRONMENT_VARS_INITIAL = {
    'COUPLING_COMPONENTS' : {'desc': ('Space separated list of components'
                                      ' to be coupled')},
    'RMP_DIR': {'desc': 'Directory containing remapping weights files'},
    'NAMCOUPLE_STATIC': {'default_val': ''}}

MCT_ENVIRONMENT_VARS_INITIAL = {**MCT_ENVIRONMENT_VARS_COMMON,
                                **MCT_ENVIRONMENT_VARS_INITIAL}
MCT_ENVIRONMENT_VARS_FINAL = MCT_ENVIRONMENT_VARS_COMMON
