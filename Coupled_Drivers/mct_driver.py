#!/usr/bin/env python
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2019 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    mct_driver.py

DESCRIPTION
    Driver for OASIS3-MCT
'''

#The from __future__ imports ensure compatibility between python2.7 and 3.x
from __future__ import absolute_import
import os
import sys
import glob
import common
import error
import update_namcouple
import cpmip_controller
try:
    import f90nml
except ImportError:
    pass

def _multiglob(*args):
    '''
    Takes in a list of globbable strings, and returns a single list of
    filenames matching those strings
    '''
    filenames = []
    for arg in args:
        filenames += glob.glob(arg)
    return filenames

def _setup_nemo_cpld(common_envar, mct_envar):
    '''
    Setup NEMO for coupled configurations
    '''
    nemo_cpld_envar = common.LoadEnvar()
    _ = nemo_cpld_envar.load_envar('OCEAN_LINK', 'ocean.exe')
    nemo_debug_files = glob.glob('*%s*.nc' % nemo_cpld_envar['OCEAN_LINK'])
    for nemo_debug_file in nemo_debug_files:
        common.remove_file(nemo_debug_file)


def _setup_um_cpld(common_envar, mct_envar):
    '''
    Setup UM for coupled configurations
    '''
    # Remove potential UM debug netcdf files. If this isn't done MCT will
    # just append details to existing files
    um_cpld_envar = common.LoadEnvar()
    _ = um_cpld_envar.load_envar('ATMOS_LINK', 'atmos.exe')
    um_debug_files = glob.glob('*%s*.nc' % um_cpld_envar['ATMOS_LINK'])
    for um_debug_file in um_debug_files:
        common.remove_file(um_debug_file)


def _setup_jnr_cpld(common_envar, mct_envar):
    '''
    Setup Jnr UM for coupled configurations.
    This function is only used when creating the namcouple at run time.
    '''
    # Remove potential UM debug netcdf files. If this isn't done MCT will
    # just append details to existing files
    um_cpld_envar = common.LoadEnvar()
    _ = um_cpld_envar.load_envar('ATMOS_LINK_JNR', 'atmos-jnr.exe')
    um_debug_files = glob.glob('*%s*.nc' % um_cpld_envar['ATMOS_LINK_JNR'])
    for um_debug_file in um_debug_files:
        common.remove_file(um_debug_file)


def _setup_rmp_dir(mct_envar, run_info):
    '''
    Set up link to the remapping weights files.
    This function is only used when creating the namcouple at run time.
    '''
    # It's only when the namcouple file doesn't exist that we're
    # anticipating needing more than one remapping directory.
    if run_info['l_namcouple']:
        # Organise the remapping files
        remap_files = glob.glob('%s/rmp_*' % mct_envar['RMP_DIR'])
        for remap_file in remap_files:
            linkname = os.path.split(remap_file)[-1]
            os.symlink(remap_file, linkname)
    else:
        # Need to be precise about order of components
        comp_names = {'um':'ATM', 'jnr':'JNR', 'nemo':'OCN'}
        comp_order = ['um', 'jnr', 'nemo']
        comp_list = []
        for component in comp_order:
            if component in mct_envar['COUPLING_COMPONENTS'].split():
                comp_list.append(comp_names[component])

        # Links to areas.nc, grids.nc and masks.nc
        core_dir_str = None
        for comp in comp_order:
            grid = comp_names[comp] + '_grid'
            if grid in run_info:
                grid_name = run_info[grid]
            else:
                grid_name = "*"
            if core_dir_str:
                core_dir_str = ('%s_%s' % (core_dir_str, grid_name))
            else:
                core_dir_str = grid_name
        core_dir_str = mct_envar['RMP_DIR'] + '/' + core_dir_str

        # Find the core remapping directory and link the core
        # remapping files
        core_dirs = glob.glob(core_dir_str)
        if len(core_dirs) < 1:
            sys.stderr.write('[FAIL] failed to find core remapping '
                             'directory %s\n' % core_dir_str)
            sys.exit(error.MISSING_CORE_RMP_DIR)
        for core_file in ['areas.nc', 'grids.nc', 'masks.nc']:
            core_file2 = core_dirs[0] + '/' + core_file
            if os.path.isfile(core_file2):
                # Remove link if it already exists
                common.remove_file(core_file)
                # Create symbolic link
                os.symlink(core_file2, core_file)
            else:
                sys.stderr.write('[FAIL] failed to find %s' % core_file2)
                sys.exit(error.MISSING_CORE_RMP_FILE)

        # Links to the remapping weight files
        for comp1 in comp_list:
            for comp2 in comp_list:
                if comp2 == comp1:
                    break
                # Create the links for remapping file between these
                # components
                grid1 = comp1 + '_grid'
                grid2 = comp2 + '_grid'
                if not grid1 in run_info or not grid2 in run_info:
                    sys.stderr.write('[FAIL] either %s or %s is missing '
                                     'from run_info.\n' % (grid1, grid2))
                    sys.exit(error.MISSING_GRID_IN_RUN_INFO)
                rmp_dir = mct_envar['RMP_DIR'] + '/' + run_info[grid2] +\
                    '_' + run_info[grid1]
                # Check that directory exists
                if not os.path.isdir(rmp_dir):
                    sys.stderr.write('[FAIL] failed to find remapping '
                                     'directory %s\n.' % rmp_dir)
                    sys.exit(error.MISSING_RMP_DIR)
                # Create the links
                remap_files = glob.glob('%s/rmp_*' % rmp_dir)
                for remap_file in remap_files:
                    linkname = os.path.split(remap_file)[-1]
                    os.symlink(remap_file, linkname)


def _setup_executable(common_envar, run_info):
    '''
    Setup the environment and any files required by the executable
    '''
    # Load the environment variables required
    mct_envar = common.LoadEnvar()

    if mct_envar.load_envar('COUPLING_COMPONENTS') != 0:
        sys.stderr.write('[FAIL] Environment variable COUPLING_COMPONENTS'
                         ' containing a list of components to be coupled is'
                         ' not set, however the MCT driver has been run\n')
        sys.exit(error.MISSING_EVAR_ERROR)
    if mct_envar.load_envar('RMP_DIR') != 0:
        sys.stderr.write('[FAIL] Environment variable RMP_DIR containing'
                         ' remapping weights files not defined in the'
                         ' environment\n')
        sys.exit(error.MISSING_EVAR_ERROR)
    _ = mct_envar.load_envar('CPMIP_ANALYSIS', 'False')

    # Tidyup our OASIS files before the setup process is started
    files_to_tidy = _multiglob('nout.*', 'debug.*root.*', 'debug.??.*',
                               'debug.???.*', '*fort*', 'rmp_*')
    for f_to_tidy in files_to_tidy:
        common.remove_file(f_to_tidy)

    # Organise the remapping files
    _setup_rmp_dir(mct_envar, run_info)

    # Are we expecting a namcouple file
    if run_info['l_namcouple']:
        # Does the namcouple file exist
        if not os.path.exists('namcouple'):
            sys.stderr.write('[FAIL] Could not find a namcouple file in the'
                             ' working directory. This file should originate'
                             ' in the Rose app\'s file directory\n')
            sys.exit(error.MISSING_MODEL_FILE_ERROR)

        # Create transient field namelist (note if we're creating a
        # namcouple on the fly, this will have to wait until after
        # the namcouple have been created).
        _, _ = common.exec_subproc('./OASIS_fields')

    for component in mct_envar['COUPLING_COMPONENTS'].split():
        if not component in common_envar['models']:
            sys.stderr.write('[FAIL] Attempting to couple component %s,'
                             ' however this component is not being run in'
                             ' this configuration\n' % component)
            sys.exit(999)
        if not component in list(SUPPORTED_MODELS.keys()):
            sys.stderr.write('[FAIL] The component %s is not supported by the'
                             ' mct driver\n' % component)
            sys.exit(999)
        # Setup coupling for individual component
        sys.stdout.write('[INFO] MCT driver setting up %s component\n' %
                         component)
        SUPPORTED_MODELS[component](common_envar, mct_envar)

    # Update the general, non-component specific namcouple details
    if run_info['l_namcouple']:
        update_namcouple.update('mct')

    # Run the CPMIP controller if appropriate
    # Check for the presence of t (as in TRUE, True, or true) in the
    # CPMIP_ANALYSIS value
    if mct_envar['CPMIP_ANALYSIS'].lower().startswith('t'):
        controller_mode = "run_controller"
        sys.stdout.write('[INFO] mct_driver: CPMIP analyis will be performed\n')
        cpmip_controller.run_controller(controller_mode, common_envar)

    return mct_envar


def _set_launcher_command(_):
    '''
    Setup the launcher command for the executable. MCT does not require a
    call to the launcher as it runs as a library
    '''
    launch_cmd = ''
    return launch_cmd


def _sent_coupling_fields(mct_envar, run_info):
    '''
    Read the SHARED file to get the coupling frequencies.
    This function is only used when creating the namcouple at run time.
    '''

    # Dictionary for the component names
    component_names = {'um':'ATM', 'nemo':'OCN', 'jnr':'JNR'}
    # Dictionary for the coupling frequencies
    # (Note that for now, we're assuming that coupling frequencies
    # for JNR<->OCN are the same as ATM<->OCN)
    couple_freqs = {'ATM2OCN_freq': ['oasis_couple_freq_ao'],
                    'OCN2ATM_freq': ['oasis_couple_freq_oa'],
                    'ATM2JNR_freq': ['oasis_couple_freq_aj',
                                     'oasis_couple_freq_aj_stats'],
                    'JNR2ATM_freq': ['oasis_couple_freq_ja',
                                     'oasis_couple_freq_ja_stats'],
                    'JNR2OCN_freq': ['oasis_couple_freq_ao'],
                    'OCN2JNR_freq': ['oasis_couple_freq_oa']}

    # Check that SHARED exists
    if not os.path.isfile(run_info['SHARED_FILE']):
        sys.stderr.write('[FAIL] not found SHARED file.\n')
        sys.exit(error.NOT_FOUND_SHARED)

    # Read the namelist file SHARED
    shared_nml = f90nml.read(run_info['SHARED_FILE'])
    for component1 in mct_envar['COUPLING_COMPONENTS'].split():
        for component2 in mct_envar['COUPLING_COMPONENTS'].split():
            if component2 != component1:
                # Check component names exist
                if not component1 in component_names or \
                        not component2 in component_names:
                    sys.stderr.write('[FAIL] %s or %s is unrecognised as '
                                     'a component name\n' % (component1,
                                                             component2))
                    sys.exit(error.UNRECOGNISED_COMP)

                # Determine the variable which stores the coupling frequency
                cpl_var = component_names[component1] + '2' + \
                    component_names[component2] + '_freq'

                # Check the coupling frequency/ies exist
                if not cpl_var in couple_freqs:
                    sys.stderr.write('[FAIL] %s is not recognised\n' %
                                     cpl_var)
                    sys.exit(error.UNRECOGNISED_CPL_VAR)
                nml_cpl_vars = couple_freqs[cpl_var]
                if not 'coupling_control' in shared_nml:
                    sys.stderr.write('[FAIL] failed to find coupling_control '
                                     'in SHARED namelist.\n')
                    sys.exit(error.MISSING_CPL_CONTROL)

                # Loop across the coupling variables
                for nml_cpl_entry in nml_cpl_vars:
                    if not nml_cpl_entry in shared_nml['coupling_control']:
                        sys.stderr.write('[FAIL] failed to find %s in '
                                         'namelist coupling_control\n' %
                                         nml_cpl_entry)
                        sys.exit(error.MISSING_CPL_FREQ)

                    # Store coupling frequency
                    if not cpl_var in run_info:
                        run_info[cpl_var] = []
                    cpl_freq = 3600 * \
                        shared_nml['coupling_control'][nml_cpl_entry][0] + \
                        60 * shared_nml['coupling_control'][nml_cpl_entry][1]
                    run_info[cpl_var].append(cpl_freq)

    return run_info


def _finalize_executable(common_envar):
    '''
    Perform any tasks required after completion of model run
    '''
    # Load the environment variables required
    mct_envar = common.LoadEnvar()
    _ = mct_envar.load_envar('CPMIP_ANALYSIS', 'False')
    # run the cpmip controller if appropriate
    # check for the presence of t (as in TRUE, True, or true) in the
    # CPMIP_ANALYSIS value
    if mct_envar['CPMIP_ANALYSIS'].lower().startswith('t'):
        controller_mode = "finalize"
        sys.stdout.write(
            '[INFO] mct_driver: CPMIP analyis is being performed\n')
        cpmip_controller.run_controller(controller_mode, common_envar)


def run_driver(common_envar, mode, run_info):
    '''
    Run the driver, and return an instance of common.LoadEnvar and as string
    containing the launcher command for the MCT component
    '''
    if mode == 'run_driver':
        exe_envar = _setup_executable(common_envar, run_info)
        launch_cmd = _set_launcher_command(exe_envar)
        model_snd_list = None
        if not run_info['l_namcouple']:
            run_info = _sent_coupling_fields(exe_envar, run_info)
    elif mode == 'finalize':
        _finalize_executable(common_envar)
        exe_envar = None
        launch_cmd = None
        model_snd_list = None
    return exe_envar, launch_cmd, run_info, model_snd_list


# Dictionary containing the supported models and their assosicated setup
# function within the driver
SUPPORTED_MODELS = {'nemo': _setup_nemo_cpld,
                    'um': _setup_um_cpld,
                    'jnr': _setup_jnr_cpld}
