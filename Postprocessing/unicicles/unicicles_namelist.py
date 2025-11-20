#!/usr/bin/env python
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2025 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    unicicles_namelist.py

DESCRIPTION
   Unicicles post processing application

DESCRIPTION
    Default namelists for UniCiCles post processing control
'''

import os


class UniciclesNamelist(object):
    '''Default values for unicicles_pp namelist'''
    cycle_length = '1y'
    debug = False
    pp_run = False
    share_directory = os.getcwd()

NAMELISTS = {'unicicles_pp': UniciclesNamelist}
