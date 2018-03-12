#!/usr/bin/env python2.7
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2018 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    cpmip_controller.py

DESCRIPTION
    Controller for the generation of CPMIP metrics
'''

import math
import re
import sys
import common
import error


CORES_PER_NODE_UKMO_XC40 = {'broadwell': 36,
                            'haswell': 32}

def get_allocated_cpus(cpmip_envar):
    '''
    Grab the allocated nproc for the UM XC40
    '''
    models = ['UM', 'NEMO', 'XIOS']
    allocated_cpu = {}
    mpi_tasks = {}
    for model in models:
        preopt_string = 'ROSE_LAUNCHER_PREOPTS_%s' % model
        if cpmip_envar.contains(preopt_string):
            preopts = cpmip_envar[preopt_string]
            preopts = preopts.split(' ')
            # must have -n for total number MPI tasks
            n_mpi = float(preopts[preopts.index('-n') + 1])
            mpi_tasks[model] = int(n_mpi)
            try:
                strides = float(preopts[preopts.index('-d') + 1])
            except ValueError:
                strides = 1.0
            try:
                hyperthreads = float(preopts[preopts.index('-j') + 1])
            except ValueError:
                hyperthreads = 1.0
            cores = int((n_mpi * strides) / hyperthreads)
            allocated_cpu[model] = cores
        else:
            allocated_cpu[model] = 0
            mpi_tasks[model] = 0
    return allocated_cpu, mpi_tasks


def chsy_metric(allocated_cpus, run_cpus, years_run_cycle, cycle_runtime_hr):
    '''
    Core hours per simulated year metric. This is the product of the model
    runtime for 1 simulated year, and the number of cores allocated. Note
    that these are the allocated cores, which may be a greater number than
    the cores used when considering non fully populated nodes. Returns a
    string of the message for this metric to be written to stdout/output file
    '''

    cpus_used_percentage = (float(run_cpus) / float(allocated_cpus)) * 100.
    cpus_message = 'This run uses %.2f percent of the allocated CPUS ' \
        '(%i/%i)\n' % (cpus_used_percentage, run_cpus, allocated_cpus)

    total_corehours = float(allocated_cpus) * float(cycle_runtime_hr)
    corehours_per_year = total_corehours / float(years_run_cycle)
    chsy_message = 'Corehours per simulated year (CHSY): %.2f\n' % \
        corehours_per_year
    return '%s%s' % (cpus_message, chsy_message)


def tasklength_to_years(tasklength):
    '''
    Takes in a tasklength variable (string of form Y,M,D,h,m,s) and returns
    an integer value of the equivalent number of years for a 360 day
    calendar.
    '''
    length = map(int, tasklength.split(','))
    to_years = (1, 1./30., 1./360., 1./(360.*24.),
                1./(360.*24.*60.), 1./(360.*24.*3600.))
    years = sum([x*y for x, y in zip(to_years, length)])
    return years


def seconds_to_days(time_secs):
    '''
    Takes in an integer value in units of seconds, and returns a floating point
    value of that time in days
    '''
    time_days = time_secs / (24.*3600.)
    return time_days


def __get_jobfile_info(jobfile):
    '''
    Takes in a path to the jobfile and returns a dictionary containing
    all the directives set by PBS -l. This code is specific to the PBS
    load scheduler present on the Cray systems
    '''
    job_f = common.open_text_file(jobfile, 'r')
    pbs_l_dict = {}

    for line in job_f.readlines():
        # Grab key value pairs of the PBS variables. The pairs are delimited
        # by colons in the PBS directive. Times are also however defined using
        # colons (for example on hour is 01:00:00).
        if line.strip().startswith('#PBS -l'):
            for item in re.findall(r'(\w+)=(\w+(:\d+)*)', line):
                pbs_l_dict[item[0]] = item[1]
    job_f.close()
    return pbs_l_dict


def __get_um_info(pe0_output):
    '''
    Grab the UM output. Returns the UM CPU time (sans coupling), and the time
    spent in the UMs coupling routines
    '''
    get_times = False
    geto2a_regex = re.compile(r"\d+\s*oasis3_geto2a\s*(\d+.\d+)")
    puta2o_regex = re.compile(r"\d+\s*oasis3_puta2o\s*(\d+.\d+)")
    inita2o_regex = re.compile(r"\d+\s*oasis3_inita2o\s*(\d+.\d+)")
    um_shell_regex = re.compile(r"\d+\s*UM_SHELL\s*(\d+.\d+)")
    with open(pe0_output, 'r') as f_pe0:
        for line in f_pe0:
            if 'MPP : Non Inclusive timer summary' in line:
                get_times = True
            if 'CPU TIMES (sorted by wallclock times)' in line:
                get_times = False
            # Pull out the average times for the coupling routines
            if get_times:
                geto2a_match = geto2a_regex.search(line)
                puta2o_match = puta2o_regex.search(line)
                inita2o_match = inita2o_regex.search(line)
                um_shell_match = um_shell_regex.search(line)
                if geto2a_match:
                    geto2a_time = float(geto2a_match.group(1))
                if puta2o_match:
                    puta2o_time = float(puta2o_match.group(1))
                if inita2o_match:
                    inita2o_time = float(inita2o_match.group(1))
                if um_shell_match:
                    um_shell_time = float(um_shell_match.group(1))
    try:
        coupling_time = geto2a_time + puta2o_time + inita2o_time
        model_time = um_shell_time - coupling_time
    except NameError:
        sys.stderr.write('[FAIL] Unable to determine Oasis timings from'
                         ' the UM standard output\n')
        sys.exit(error.MISSING_CONTROLLER_FILE_ERROR)
    return model_time, coupling_time


def __get_nemo_info(nemo_timing_output='timing.output'):
    '''
    Grab NEMO timing output. Takes an optional argument, the path to the NEMO
    timing.output file for NEMO/CICE. Returns the time spent in the NEMO
    model, less the time spent in the coupling routines, and the time spent
    in the coupling routines themselves, as well as the (inclusive) time in
    CICE.
    '''
    # There are three coupling routines we need to remove from the total time
    # sbc_cpl_rcv, sbc_cpl_init, and sbc_cpl_snd.
    # Compile the regular expressions needed to pull out the timings. Use the
    # elapsed times
    # This searches for a time
    total_time_regex = re.compile(r"\s*Total\s*\|\s*(\d+.\d+)")
    # These regexes will pull out a percentage
    sbc_cpl_rcv_regex = re.compile(r"\s*sbc_cpl_rcv\s*\d+.\d+\s*(\d+.\d+)")
    sbc_cpl_init_regex = re.compile(r"\s*sbc_cpl_init\s*\d+.\d+\s*(\d+.\d+)")
    sbc_cpl_snd_regex = re.compile(r"\s*sbc_cpl_snd\s*\d+.\d+\s*(\d+.\d+)")
    sbc_ice_cice_regex = re.compile(r"\s*sbc_ice_cice\s*\d+.\d+\s*(\d+.\d+)")

    with common.open_text_file(nemo_timing_output, 'r') as nemo_timing_handle:
        for line in nemo_timing_handle.readlines():
            tot_match = total_time_regex.search(line)
            cpl_rcv_match = sbc_cpl_rcv_regex.search(line)
            cpl_init_match = sbc_cpl_init_regex.search(line)
            cpl_snd_match = sbc_cpl_snd_regex.search(line)
            sbc_ice_cice_match = sbc_ice_cice_regex.search(line)
            if tot_match:
                total_time = float(tot_match.group(1))
            if cpl_rcv_match:
                rcv_percentge = float(cpl_rcv_match.group(1))
            if cpl_init_match:
                init_percentge = float(cpl_init_match.group(1))
            if cpl_snd_match:
                snd_percentge = float(cpl_snd_match.group(1))
            if sbc_ice_cice_match:
                cice_percentage = float(sbc_ice_cice_match.group(1))

    try:
        model_time = total_time * \
            (100.0 - rcv_percentge - init_percentge - snd_percentge) * 0.01
        coupling_time = total_time * \
            (rcv_percentge + init_percentge + snd_percentge) * 0.01
        cice_time = total_time * cice_percentage * 0.01
    except NameError:
        sys.stderr.write('[FAIL] Unable to determine Oasis timings from'
                         ' the NEMO standard output\n')
        sys.exit(error.MISSING_CONTROLLER_FILE_ERROR)

    return model_time, coupling_time, cice_time


def __update_namelists_for_timing(cpmip_envar):
    '''
    Update the UM and NEMO namelists to ensure that the timers are set
    to be running
    '''
    mod_shared_nl = common.ModNamelist('SHARED')
    try:
        num_version = float(cpmip_envar['VN'])
    except ValueError:
        sys.stderr.write('Expecting a numerical value for UM Version in'
                         ' environment variable VN. Instead got %s\n' %
                         cpmip_envar['VN'])
        sys.exit(error.INVALID_EVAR_ERROR)
    # For versions of UM prior to 10.7 the oasis timers can not be run
    # independently from the general UM timers
    if num_version < 10.7:
        mod_shared_nl.var_val('ltimer', '.true.')
    else:
        mod_shared_nl.var_val('ltimer', '.false.')
    mod_shared_nl.var_val('l_oasis_timers', '.true.')
    mod_shared_nl.replace()

    # Let the UM only write out on the first task (rank 0) to attempt to
    # avoid too much skewing of load balancing information. prnt_writers
    # takes integer values: 1 - all tasks, 2 - rank 0, 3 - rank 0 and head
    # IO servers
    mod_ioscntl_nl = common.ModNamelist('IOSCNTL')
    mod_ioscntl_nl.var_val('prnt_writers', 2)
    mod_ioscntl_nl.replace()

    mod_namelist_cfg = common.ModNamelist(cpmip_envar['NEMO_NL'])
    mod_namelist_cfg.var_val('nn_timing', 1)
    mod_namelist_cfg.replace()


def _load_environment_variables(cpmip_envar):
    '''
    Load the CPMIP environment variables required for the model run
    into the cpmip_envar container
    '''
    if cpmip_envar.load_envar('VN') != 0:
        sys.stderr.write('[FAIL] Environment variable VN containing the '
                         'UM version is not set\n')
        sys.exit(error.MISSING_EVAR_ERROR)
    _ = cpmip_envar.load_envar('NEMO_NL', 'namelist_cfg')

    return cpmip_envar


def _load_environment_variables_finalise(cpmip_envar):
    '''
    Load the CPMIP environment variables required for the model finalize
    into the cpmip_envar container
    '''

    # Get the number of processors the components run on
    # UM
    if cpmip_envar.load_envar('UM_ATM_NPROCX') != 0:
        sys.stderr.write('[FAIL] Environment variable UM_ATM_NPROCX containing '
                         'the number of UM processors in the X direction '
                         'is not set\n')
        sys.exit(error.MISSING_EVAR_ERROR)
    if cpmip_envar.load_envar('UM_ATM_NPROCY') != 0:
        sys.stderr.write('[FAIL] Environment variable UM_ATM_NPROCY containing '
                         'the number of UM processors in the Y direction '
                         'is not set\n')
        sys.exit(error.MISSING_EVAR_ERROR)
    _ = cpmip_envar.load_envar('FLUME_IOS_NPROC', '0')
    # NEMO
    if cpmip_envar.load_envar('NEMO_NPROC') != 0:
        sys.stderr.write('[FAIL] Environment variable NEMO_NPROC containing '
                         'the number of NEMO processors not set\n')
        sys.exit(error.MISSING_EVAR_ERROR)
    # XIOS (If applicable)
    _ = cpmip_envar.load_envar('XIOS_NPROC', '0')

    # Get the preopts for the various components
    if cpmip_envar.load_envar('ROSE_LAUNCHER_PREOPTS_UM') != 0:
        sys.stderr.write('[FAIL] Environment variable '
                         'ROSE_LAUNCHER_PREOPTS_UM is not set\n')

    if cpmip_envar.load_envar('ROSE_LAUNCHER_PREOPTS_NEMO') != 0:
        sys.stderr.write('[FAIL] Environment variable '
                         'ROSE_LAUNCHER_PREOPTS_NEMO is not set\n')

    if cpmip_envar['XIOS_NPROC'] != '0':
        if cpmip_envar.load_envar('ROSE_LAUNCHER_PREOPTS_XIOS') != 0:
            sys.stderr.write('[FAIL] Environment variable '
                             'ROSE_LAUNCHER_PREOPTS_XIOS is not set\n')

    # Get the time spent in aprun
    if cpmip_envar.load_envar('time_in_aprun') != 0:
        sys.stderr.write('[FAIL] Environment variable time_in_aprun '
                         'containing the time spent in the aprun command '
                         'not set\n')
        sys.exit(error.MISSING_EVAR_ERROR)

    # Get the tasklength variable so we can work out years per day of
    # simulation performed
    if cpmip_envar.load_envar('TASKLENGTH') != 0:
        sys.stderr.write('[FAIL] Environment variable TASKLENGTH not set\n')
        sys.exit(error.MISSING_EVAR_ERROR)

    # Get the UM stdout file
    if cpmip_envar.load_envar('STDOUT_FILE') != 0:
        sys.stderr.write('[FAIL] Environment variable STDOUT_FILE containing '
                         'the path to the UM standard out is not set\n')
        sys.exit(error.MISSING_EVAR_ERROR)

    # Get the task jobfile
    if cpmip_envar.load_envar('CYLC_TASK_LOG_ROOT') != 0:
        sys.stderr.write('[FAIL] Environment variable CYLC_TASK_LOG_ROOT  is '
                         'not set\n')
        sys.exit(error.MISSING_EVAR_ERROR)

    return cpmip_envar


def _setup_cpmip_controller():
    '''
    Setup the environment and any files required by the executable
    '''
    # Create the environment variable container
    cpmip_envar = common.LoadEnvar()
    # Load the environment variables required
    cpmip_envar = _load_environment_variables(cpmip_envar)

    # Make sure we keep the standard out
    cpmip_envar['ATMOS_KEEP_MPP_STDOUT'] = 'true'

    __update_namelists_for_timing(cpmip_envar)

    return cpmip_envar


def _set_launcher_command(_):
    '''
    Setup launcher command
    '''
    launch_cmd = ''
    return launch_cmd


def _finalize_cpmip_controller():
    '''
    Finalize the CPMIP controller.
    '''
    secs_to_hours = 1./3600.
    # Create the environment variable container
    cpmip_envar = common.LoadEnvar()
    # Load the environment variables required
    cpmip_envar = _load_environment_variables_finalise(cpmip_envar)

    cpus, mpi_tasks = get_allocated_cpus(cpmip_envar)
    # Processor resource for all components
    um_cpus = cpus['UM']
    nemo_cpus = cpus['NEMO']
    xios_cpus = cpus['XIOS']
    total_cpus = um_cpus + nemo_cpus + xios_cpus

    # Determine the name of the UM pe0 output file.
    pe0_suffix = '0'*(len(str(mpi_tasks['UM'] - 1)))
    um_pe0_stdout_file = '%s%s' % (cpmip_envar['STDOUT_FILE'],
                                   pe0_suffix)

    # Time resource for all components
    # UM time is for one processor
    um_time, um_coupling_time = __get_um_info(um_pe0_stdout_file)
    # NEMO time is integrated over all processors when returned from
    # __get_nemo_info()
    nemo_time, nemo_coupling_time, cice_time = __get_nemo_info()
    nemo_time /= nemo_cpus
    nemo_coupling_time /= nemo_cpus
    cice_time /= nemo_cpus
    # Get the arguments from the -l PBS directive
    pbs_l_dict = __get_jobfile_info(cpmip_envar['CYLC_TASK_LOG_ROOT'])

    # Determine the total number of CPUS ALLOCATED for the run. If the
    # coretype can not be determined we can not calculate this value
    # and so allocated_cpus will be set to zero. If we cant pick up a
    # coretype, override the allocated figures for the components to the
    # number of cpus used per component to allow the CPMIP coupling metric
    # to be calculated, albiet with a slightly reduced accuracy.
    number_nodes = int(pbs_l_dict['select'])
    plat_cores_per_node = \
        CORES_PER_NODE_UKMO_XC40[pbs_l_dict['coretype'].lower()]
    if pbs_l_dict.has_key('coretype'):
        allocated_cpus = number_nodes * plat_cores_per_node
        allocated_um = int(math.ceil(um_cpus/float(plat_cores_per_node))) \
            * plat_cores_per_node
        allocated_nemo = int(math.ceil(nemo_cpus/float(plat_cores_per_node))) \
            * plat_cores_per_node
        allocated_xios = int(math.ceil(xios_cpus/float(plat_cores_per_node))) \
            * plat_cores_per_node
    else:
        allocated_cpus = 0
        sys.stdout.write('[INFO] Can not determine coretype, unable to '
                         'calculate CHSY metric\n')
        allocated_um = um_cpus
        allocated_nemo = nemo_cpus
        allocated_xios = xios_cpus

    # calculate the CPMIP coupling
    # metric. This provides a fractional value
    # of the resource wasted. We assume that we can encapuslate the resource
    # used by a model run in units of (number cores * time). Where possible
    # use allocated cores to ensure consistancy with the definition of the
    # metric
    total_resource = float(allocated_cpus * int(cpmip_envar['time_in_aprun']))
    um_resource = float(allocated_um * um_time)
    nemo_resource = float(allocated_nemo * nemo_time)
    # we assume that XIOS takes the whole length of the model run. If XIOS
    # is not used, or used in attatched mode xios_cpus will be 0, so this
    # line still makes sense
    xios_resource = float(allocated_xios * int(cpmip_envar['time_in_aprun']))

    coupling_metric = (total_resource - um_resource - nemo_resource
                       - xios_resource) / total_resource

    # Run in years per day (as measured by APRUN)
    years_run = tasklength_to_years(cpmip_envar['TASKLENGTH'])
    runtime_days = seconds_to_days(int(cpmip_envar['time_in_aprun']))
    years_per_day = years_run / runtime_days

    aprun_time_message = 'Time in APRUN: %s s\n' % cpmip_envar['time_in_aprun']
    um_time_message = 'Time in UM model code: %i s\nTime in UM coupling' \
        ' code: %i s\n' % (um_time, um_coupling_time)
    nemo_time_message = 'Time in NEMO model code: %i s\n   Including' \
        ' %is in CICE\nTime in NEMO coupling code: %i s\n' % \
        (nemo_time, cice_time, nemo_coupling_time)
    ypd_message = 'This equates to %.2f years per day run (SYPD)\n' % \
        years_per_day

    # Other metrics
    if allocated_cpus:
        chsy_message = chsy_metric(allocated_cpus, total_cpus, years_run, \
                                       int(cpmip_envar['time_in_aprun']) * \
                                       secs_to_hours)
        cores_message = 'Cores per node: %s\n' % plat_cores_per_node
    else:
        chsy_message = ''
        cores_message = 'Cores per node: Unable to determine cores per node' \
            ' the CPMIP metric will be\ncalculated with USED cores rather' \
            ' than ALLOCATED cores, so will be slightly\ninconsistent\n'

    coupling_metric_message = 'The CPMIP coupling metric for this run is ' \
        '%.3f\n' % coupling_metric


    # Produce a nice summary of the coupling metric and various information
    sys.stdout.write('\nSUMMARY FROM CPMIP CONTROLLER\n')
    sys.stdout.write('%s\n' % ('-'*80,))
    sys.stdout.write(cores_message)
    sys.stdout.write('%s\n' % ('-'*80,))
    sys.stdout.write(aprun_time_message)
    sys.stdout.write(um_time_message)
    sys.stdout.write(nemo_time_message)
    if xios_cpus:
        sys.stdout.write('It is assumed that XIOS takes the same time as '
                         'APRUN\n')
    sys.stdout.write(ypd_message)
    sys.stdout.write('\nResource for components in units of core hours\n')
    sys.stdout.write('  UM Resource %.2f\n' % (um_resource * secs_to_hours,))
    sys.stdout.write('  NEMO Resource %.2f\n' %
                     (nemo_resource * secs_to_hours,))
    if xios_cpus:
        sys.stdout.write('  XIOS Resource %.2f\n' %
                         (xios_resource * secs_to_hours,))
    sys.stdout.write('\n%s' % coupling_metric_message)
    sys.stdout.write('\nThis implies that %.2f core hours are wasted in this'
                     ' run\n' %
                     (coupling_metric * total_resource * secs_to_hours,))
    sys.stdout.write(chsy_message)
    sys.stdout.write('%s\n' % ('-'*80,))

    # Write an output file containing runtime and processor number information
    # gleaned from the model output file to enable further analysis on this
    # data that can not be performed by the drivers for reasons of performance
    # (MOM node restrictiions in the case of the UKMO Cray XC40
    output_file = 'cpmip.output'
    with common.open_text_file(output_file, 'w') as cpmip_f:
        if allocated_cpus:
            cpmip_f.write('%s' % cores_message)
        cpmip_f.write('%s%s%s%s%s%s' % (aprun_time_message, um_time_message,
                                        nemo_time_message, ypd_message,
                                        chsy_message, coupling_metric_message))
        cpmip_f.write('UM Processors: %i\n' % um_cpus)
        cpmip_f.write('NEMO Processors: %i\n' % nemo_cpus)
        if xios_cpus:
            cpmip_f.write('XIOS Processors: %i\n' % xios_cpus)



def run_controller(mode):
    '''
    Run the CPMIP controller.
    '''
    if mode == 'run_controller':
        exe_envar = _setup_cpmip_controller()

        launch_cmd = _set_launcher_command(exe_envar)
    elif mode == 'finalize':
        _finalize_cpmip_controller()
        exe_envar = None
        launch_cmd = None

    return exe_envar, launch_cmd
