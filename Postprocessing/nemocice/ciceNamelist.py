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
NAME
    ciceNamelist.py

DESCRIPTION
    Default namelists for CICE post processing control
'''
import os


class ciceNamelist:
    pp_run = False
    restart_directory = os.environ['DATAM']
    archive_restarts = False
    archive_timestamps = '06-01', '12-01'
    buffer_archive = 5
    means_directory = os.environ['CYLC_TASK_WORK_DIR'] + '/../coupled'
    means_cmd = '/projects/ocean/hadgem3/nco/nco-3.9.5_clean/bin/ncra --64bit -O'
    create_means = False
    archive_means = False
    archive_set = os.environ['CYLC_SUITE_NAME']
    debug = False

NAMELISTS = {'cicepostproc': ciceNamelist}
