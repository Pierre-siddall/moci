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
    lfric_driver.py
DESCRIPTION
    Driver for the LFRic component, called from link_drivers
'''

import os
import common
import dr_env_lib.lfric_def
import dr_env_lib.env_lib


def _setup_executable(common_envar, run_info):
    '''
    Setup the environment and any files required by the executable
    '''
    # Create the environment variable container
    lfric_envar = dr_env_lib.env_lib.LoadEnvar()
    # Load the environment variables required
    lfric_envar = dr_env_lib.env_lib.load_envar_from_definition(
        lfric_envar, dr_env_lib.lfric_def.LFRIC_ENVIRONMENT_VARS_INITIAL)

    common.remove_file(lfric_envar['LFRIC_LINK'])
    os.symlink(lfric_envar['LFRIC_EXEC'],
               lfric_envar['LFRIC_LINK'])
    return lfric_envar


def _set_launcher_command(launcher, lfric_envar):
    '''
    Setup the launcher command for the executable
    '''
    if lfric_envar['ROSE_LAUNCHER_PREOPTS_LFRIC'] == 'unset':
        ss = False
        lfric_envar['ROSE_LAUNCHER_PREOPTS_LFRIC'] = \
            common.set_aprun_options(lfric_envar['LFRIC_NPROC'], \
                lfric_envar['LFRIC_NODES'], lfric_envar['OMPTHR_LFRIC'], \
                    lfric_envar['LFRICHYPERTHREADS'], ss) \
                        if launcher == 'aprun' else ''

    launch_cmd = '%s ./%s %s' % \
                 (lfric_envar['ROSE_LAUNCHER_PREOPTS_LFRIC'], \
                  lfric_envar['LFRIC_LINK'],
                  lfric_envar['CONFIG_NL_PATH_LFRIC'])

    # Put in quotes to allow this environment variable to be exported as it
    # contains (or can contain) spaces
    lfric_envar['ROSE_LAUNCHER_PREOPTS_LFRIC'] = "'%s'" % \
        lfric_envar['ROSE_LAUNCHER_PREOPTS_LFRIC']

    return launch_cmd

def _sent_coupling_fields(exe_envar, run_info):
    '''
    Add the coupling fields sent from this executable.
    This function is only used when creating the namcouple at run time.
    '''
    model_snd_list = None
    return run_info, model_snd_list

def _finalize_executable(common_envar):
    '''
    Perform any tasks required after completion of model run
    '''

def run_driver(common_envar, mode, run_info):
    '''
    Run the driver, and return an instance of common.LoadEnvar and as string
    containing the launcher command for the LFRic component
    '''
    if mode == 'run_driver':
        exe_envar = _setup_executable(common_envar, run_info)
        launch_cmd = _set_launcher_command(
            common_envar['ROSE_LAUNCHER'], exe_envar)
        model_snd_list = None
        if not run_info['l_namcouple']:
            run_info, model_snd_list \
                = _sent_coupling_fields(exe_envar, run_info)
    elif mode == 'finalize':
        _finalize_executable(common_envar)
        exe_envar = None
        launch_cmd = None
        model_snd_list = None
    elif mode == 'failure':
        # subset of operations if the model fails
        exe_envar = None
        launch_cmd = None
        model_snd_list = None
    return exe_envar, launch_cmd, run_info, model_snd_list
