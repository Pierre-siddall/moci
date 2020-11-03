#!/usr/bin/env python3
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2020 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    params.py

DESCRIPTION
    Paramaters to control the HPC metric generation
'''

import datetime

# Paramaters
DB_URL = "postgresql://pbs_ext_ro:WfuPbV7jgURV655g@xctrh00/accounting"
XCSR_ALLOC_NODES = 2590
XCEF_ALLOC_NODES = 2634
XCEF_HASWELL_NODES = 365

# Date Range
START_DATE = False           #date object, or false
END_DATE = False             #date object, or false
PAST_N_DAYS = 7              #previos number of days

# Reporting
GROUP_E_F = False
MAKE_HTML = True
MAKE_PLOT = True

# Which Metrics
USE_VS_BUDGET = True
DAILY_QUEUE_AVES = True
NODE_USE_SUMMARY = True
HASWELL_USE_SUMMARY = True
BROADWELL_USE_SUMMARY = True

# Variables for Individual Metrics
# NODE_USE_SUMMARY
NUG_LIMITS_FILE = '/home/h03/moci/Public/NUG/Limits/current.lm'
RESOURCE_USED_EXE = '/home/h03/moci/bin/NUG/NUG_utils/resource_used'
# BUDGETARY CALCULATIONS
FAIRSHARE_FRACTION = 0.8




############## NOT FOR USER EDIT ######################################
############## CALCULATED PARAMATERS BELOW THIS LINE ##################

if not START_DATE:
    END_DATE = datetime.date.today()
    START_DATE = END_DATE - datetime.timedelta(days=PAST_N_DAYS)
    NDAYS = PAST_N_DAYS
else:
    NDAYS = (START_DATE - END_DATE).days

if GROUP_E_F:
    HOST_SYSTEMS = [['xce', 'xcf'], ['xcs-r']]
else:
    HOST_SYSTEMS = [['xce'], ['xcf'], ['xcs-r']]
