#!/usr/bin/env python
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2015-2017 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    cice_namelist.py

DESCRIPTION
    Default namelists for CICE post processing control
'''
import template_namelist


class TopLevel(template_namelist.TopLevel):
    ''' Default values for cice_pp namelist '''


class Processing(template_namelist.Processing):
    ''' Default values for cice_processing namelist '''

    means_cmd = \
        '/projects/ocean/hadgem3/nco/nco-3.9.5_clean/bin/ncra --64bit -O'
    chunking_arguments = 'time/1,nc/1,ni/288,nj/204'
    cat_daily_means = False


class Archiving(template_namelist.Archiving):
    ''' Default values for cice_archiving namelist '''


NAMELISTS = {'cice_pp': TopLevel,
             'cice_processing': Processing,
             'cice_archiving': Archiving}
