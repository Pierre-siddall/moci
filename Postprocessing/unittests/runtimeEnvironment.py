#!/usr/bin/env python2.7
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2015 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
'''

import os

# Standard Cylc Environment
os.environ['CYLC_SUITE_REG_NAME'] = 'suiteID'
os.environ['CYLC_SUITE_NAME'] = os.environ['CYLC_SUITE_REG_NAME']
os.environ['CYLC_SUITE_SHARE_DIR'] = os.environ['PWD']
os.environ['CYLC_TASK_WORK_DIR'] = os.environ['PWD']
os.environ['CYLC_TASK_LOG_ROOT'] = os.environ['PWD']

# Standard UM Setup Environment
os.environ['RUNID'] = 'testp'
os.environ['DATAM'] = os.environ['CYLC_TASK_WORK_DIR']
