#!/usr/bin/env python3
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2020-2025 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    mct_validate.py

DESCRIPTION
    Validate coupling paramaters in the MCT driver
'''




import re
import sys


def to_seconds(hours, minutes, seconds):
    '''
    Take in time in hours, minutes, seconds and return a value in seconds
    '''
    return hours*3600 + minutes*60 + seconds


def get_coupling_fields():
    '''
    Get the coupling fields from the namcouple. Only ocean to atmos and
    atmos to ocean
    '''
    read = False
    # The following two regexes work within a namcouple TRANSDEF definition
    # the definition regex searches the line which contains the source and
    # destination fields, and matches (using groups) the source, destination
    # and coupling frequencies.
    definition_regex = r'\s*(\w+)\s+(\w+)\s+\d+\s+(\d+)\s+\d+\s+[\w.]+\s+\w+'
    # The grids regex searches the line containing the source and destination
    # resolution and grid names, and matches the the source and dest names
    grids_regex = r'\s*\d+\s+\d+\s+\d+\s+\d+\s+(\w+)\s+(\w+)'
    a2ofields = []
    o2afields = []
    field_dict = {}
    with open('namcouple', 'r') as namcouple_h:
        for line in namcouple_h.readlines():
            if re.match(definition_regex, line):
                read_info = re.search(definition_regex, line)
                field_dict['src_field'] = read_info.group(1)
                field_dict['dest_field'] = read_info.group(2)
                field_dict['freq_s'] = int(read_info.group(3))
                read = True
            if re.match(grids_regex, line) and read:
                src_grid = re.search(grids_regex, line).group(1)
                dest_grid = re.search(grids_regex, line).group(2)
                if src_grid[0] == 'a':
                    a2ofields.append(field_dict)
                elif dest_grid[0] == 'a':
                    o2afields.append(field_dict)
                else:
                    sys.stderr.write('Can not determine source and destination'
                                     ' for field %s\n' % field_dict['src_field'])
                field_dict = {}
                read = False
    return {'a2o': a2ofields, 'o2a': o2afields}

def get_nemo_ts():
    '''
    Get the nemo timestep length in seconds
    '''
    ts_regex = r'\s*rn_rdt=(\d*.\d*),'
    with open('namelist_cfg', 'r') as nlcfg_h:
        for line in nlcfg_h.readlines():
            if re.match(ts_regex, line):
                timestep = re.search(ts_regex, line).group(1)
                try:
                    timestep = float(timestep)
                except ValueError:
                    pass
    return timestep


def get_um_ocean_coupling_freq(um_ts=None):
    '''
    Get the UM-OCEAN coupling frequencies in seconds from SHARED namelist,
    and also the river routing if applicable
    '''
    um_ocean_coupling_s = {}
    a2o_re = r'oasis_couple_freq_ao=(\d*),(\d*),'
    o2a_re = r'oasis_couple_freq_oa=(\d*),(\d*),'
    rrouting_re = r'nstep_rivers=(\d*),'
    with open('SHARED', 'r') as shared_h:
        for line in shared_h.readlines():
            if re.match(a2o_re, line):
                hour = int(re.search(a2o_re, line).group(1))
                minute = int(re.search(a2o_re, line).group(2))
                um_ocean_coupling_s['a2o'] = to_seconds(hour, minute, 0.)
            if re.match(o2a_re, line):
                hour = int(re.search(o2a_re, line).group(1))
                minute = int(re.search(o2a_re, line).group(2))
                um_ocean_coupling_s['o2a'] = to_seconds(hour, minute, 0.)
            if re.match(rrouting_re, line):
                river_routing_s = int(re.search(rrouting_re, line).group(1)) * \
                                  um_ts
                um_ocean_coupling_s['rr'] = river_routing_s
    return um_ocean_coupling_s


def get_um_ts():
    '''
    Get the UM timestep length in seconds
    '''
    periodlen_re = r'secs_per_periodim=(\d*),'
    periodsteps_re = r'steps_per_periodim=(\d*),'
    with open('ATMOSCNTL', 'r') as atmoscntl_h:
        for line in atmoscntl_h.readlines():
            if re.match(periodlen_re, line):
                periodlen = int(re.search(periodlen_re, line).group(1))
            if re.match(periodsteps_re, line):
                periodsteps = int(re.search(periodsteps_re, line).group(1))
    return periodlen / periodsteps


def get_coupling_timeprofiles_strs():
    '''
    Get the coupling time profiles used in this configuration. We assume
    their names contain COUP. This is a list of lists of strings read from
    the file
    '''
    is_buff = False
    time_profile_strs = []
    buf = []
    with open('STASHC', 'r') as stashc_h:
        for line in stashc_h.readlines():
            if 'umstash_time' in line:
                is_buff = True
            if '/' in line and is_buff:
                time_profile_strs.append(buf)
                is_buff = False
                buf = []
            if is_buff:
                if 'tim_name' in line and 'COUP' not in line:
                    #we don't care about these profiles
                    is_buff = False
                    buf = []
                else:
                    buf.append(line)
    return time_profile_strs


def timeprofiles_str_2_dict(time_profile_strs):
    '''
    Take a list of timeprofile strings and return a list of dictionaries
    '''
    profiles = []
    # Match a variable=value, (using groups to pull out the variable and
    # value) from the timeprofile list.
    # variable names must start with a letter, then can have zero or more
    # word characters
    # a variable might be surrounded by optional single or double quotes
    # if it is a number it may be negative
    # its value will be word characters
    # the line will end with a comma (,)
    var_regex = r'([a-zA-Z]{1}\w*)=[\'\"]?(-?\w+)[\'\"]?,.*'
    for tps in time_profile_strs:
        profile = {}
        for i_tps in tps:
            if re.match(var_regex, i_tps):
                var_name = re.search(var_regex, i_tps).group(1)
                var_value = re.search(var_regex, i_tps).group(2)
                try:
                    var_value = int(var_value)
                except ValueError:
                    pass
                profile[var_name] = var_value
        profiles.append(profile)
    return profiles


def check_um_vs_namcouple(couple_freq_from_um, namcouple_fields):
    '''
    Check the coupling frequences prescribed by the UM namelist and check
    they match with those from the namcouple files
    '''
    rcode = 0
    for direction, i_freq in couple_freq_from_um.items():
        if direction not in ('a2o', 'o2a'):
            continue
        for i_field in namcouple_fields[direction]:
            if i_freq != i_field['freq_s']:
                error_msg = 'Source field %s in direction %s:\n' \
                            '  UM expects coupling frequency to be %d\n' \
                            '  namcouple expects frequency to be %d\n\n' % \
                            (i_field['src_field'], direction,
                             i_freq, i_field['freq_s'])
                sys.stderr.write(error_msg)
                rcode = 1
    return rcode


def check_timestep_choice(couple_freq_from_um, um_ts, nemo_ts):
    '''
    Check the timestep and coupling frequency choice match
    '''
    rcode = 0
    um_ts = int(um_ts)
    nemo_ts = int(nemo_ts)
    for direction, i_freq in couple_freq_from_um.items():
        i_freq = int(i_freq)
        if direction == 'a2o':
            if i_freq % um_ts != 0:
                sys.stderr.write('Atmosphere timestemps must be an exact' \
                                 ' divisor of Atmosphere -> Ocean coupling' \
                                 ' timesteps:\n' \
                                 '  Atmos timestep %d s\n' \
                                 '  Coupling timestep %d s\n\n' %
                                 (um_ts, i_freq))
                rcode = 1
            # Test the river routing matches
            try:
                if i_freq != couple_freq_from_um['rr']:
                    sys.stderr.write('River routing coupling and Atmosphere ->' \
                                     ' Ocean coupling frequencies must be' \
                                     ' identical:\n' \
                                     '  Atmosphere coupling every %d s\n' \
                                     '  River routing every %d s\n' %
                                     (i_freq, couple_freq_from_um['rr']))
                    rcode = 1
            except KeyError:
                # No river routing information
                pass
        if direction == 'o2a':
            if i_freq % nemo_ts != 0:
                sys.stderr.write('Ocean timesteps must be an exact divisor of' \
                                 ' Ocean -> Atmosphere coupling timesteps:\n' \
                                 '  Ocean timestep %d s\n' \
                                 '  Coupling timestep %d s\n\n' %
                                 (nemo_ts, i_freq))
                rcode = 1

    return rcode


def human_readable_stash(stash_profiles, um_timestep):
    '''
    Take in a list of stash profile dictionaries and turn them into something
    human readable
    '''
    out_profiles = []
    # Stash codes for sampling units. We ignore code 4 (dumping frequency)
    # as it has no relevance to coupling (hopefully!).
    codes = {1: um_timestep,
             2: 3600, #hours
             3: 86400, #days
             5: 60, #minutes
             6: 1} #seconds
    for i_profile in stash_profiles:
        if i_profile['ityp'] == 1:
            i_profile['type'] = 'instantaneous'
        elif i_profile['ityp'] == 3:
            i_profile['type'] = 'timemean'
        else:
            sys.stderr.write('Unable to validate stash type (ityp) %i\n' %
                             i_profile['ityp'])
            continue
        # determine processing time in seconds if this is a mean
        if i_profile['type'] == 'timemean':
            meaning_freq = i_profile['intv'] * codes[i_profile['unt1']]
            offset = i_profile['ioff'] * codes[i_profile['unt2']]
            i_profile['freq'] = meaning_freq
            i_profile['offset'] = offset
            out_profiles.append(i_profile)
        elif i_profile['type'] == 'instantaneous' and i_profile['iopt'] == 1:
            i_profile['start'] = i_profile['istr'] *  codes[i_profile['unt3']]
            i_profile['freq'] = i_profile['ifre'] *  codes[i_profile['unt3']]
            out_profiles.append(i_profile)
    return out_profiles


def verify_stash_profiles(stash_profiles, um_coupling_freq, um_ts):
    '''
    Verify the choice of stash time profiles used for coupling. Take in a
    list of human readable stash profiles, the um coupling freq in seconds and
    the UM timestep in seconds
    '''
    rcode = 0
    for profile in stash_profiles:
        if profile['type'] == 'timemean':
            # this profile should start at zero or on a coupling timestep
            if profile['offset'] != 0:
                sys.stderr.write('Timemean profile %s not valid. Should have'
                                 ' an offset of zero\n'
                                 '  offset %i s\n\n' %
                                 (profile['tim_name'], profile['offset']))
                rcode = 1
        elif profile['type'] == 'instantaneous':
            # this is likely a river routing profile, must start on coupling
            # timestep - 1
            if profile['start'] != um_coupling_freq - um_ts:
                sys.stderr.write('Instantaneous (river routing) profile %s not'
                                 ' valid. Should start on the timestep before'
                                 ' the first coupling timestep\n'
                                 '  Expected value %i s\n'
                                 '  Actual value %i s\n\n'
                                 % (profile['tim_name'],
                                    um_coupling_freq - um_ts, profile['start']))
                rcode = 1
        if profile['freq'] != um_coupling_freq:
            # all profiles should have a frequency equal to um coupling
            # frequency
            sys.stderr.write('Time profile %s not valid. Needs to have a'
                             ' frequency identical to UM coupling frequency\n'
                             '  coupling frequency %i s\n'
                             '  stash profile frequency %i s\n\n' %
                             (profile['tim_name'], um_coupling_freq,
                              profile['freq']))
            rcode = 1
    return rcode


def finalise(iserror):
    '''
    Write a conclusion and exit depending on how the validation has gone.
    Is error=0 for success, > 0 for failure
    '''
    if iserror == 0:
        sys.stdout.write('This coupling configuration has been successfully'
                         ' validated\n')
    else:
        sys.stdout.write('This coupling configuration has problems in its'
                         ' validation. Please see stderr for details\n')
    sys.exit(iserror)


def validate():
    '''
    String together the functions to perform the validation
    '''
    # Set up return code, 0 for succeeded
    iserror = 0
    # Gather timesteps
    um_ts = get_um_ts()
    nemo_ts = get_nemo_ts()
    # Gather coupling frequencies from the UM
    coupling_frequency = get_um_ocean_coupling_freq(um_ts)
    # Get fields from namcouple
    coupling_fields = get_coupling_fields()
    # Gather stash profiles and make them human readable
    stash_profiles = get_coupling_timeprofiles_strs()
    stash_profiles = timeprofiles_str_2_dict(stash_profiles)
    stash_profiles = human_readable_stash(stash_profiles, um_ts)
    # Perform the checks
    rcode = check_timestep_choice(coupling_frequency, um_ts, nemo_ts)
    iserror += rcode
    rcode = check_um_vs_namcouple(coupling_frequency, coupling_fields)
    iserror += rcode
    rcode = verify_stash_profiles(stash_profiles,
                                  coupling_frequency['a2o'], um_ts)
    iserror += rcode
    finalise(iserror)


if __name__ == '__main__':
    validate()
