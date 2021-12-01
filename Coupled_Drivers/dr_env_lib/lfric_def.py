#!/usr/bin/env python
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2021 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    lfric_def.py

DESCRIPTION
    Definition of the environment variables required for an lfric model
    run
'''

LFRIC_ENVIRONMENT_VARS_INITIAL = {
    'CONFIG_NL_PATH_LFRIC': {},
    'LFRIC_EXEC': {},
    'LFRIC_LINK': {},
    'ROSE_LAUNCHER_PREOPTS_LFRIC': {'default_val': 'unset',
                                    'triggers': [
                                        [lambda my_val: my_val == 'unset',
                                         ['LFRIC_NODES', 'OMPTHR_LFRIC',
                                          'LFRIC_NPROC',
                                          'LFRICHYPERTHREADS']]]},
    'LFRIC_NPROC': {},
    'LFRIC_NODES': {},
    'OMPTHR_LFRIC': {},
    'LFRICHYPERTHREADS': {}
    }
