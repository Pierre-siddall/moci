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
    create_namcouple.py

DESCRIPTION
    Code for creating the namcouple at run time.
'''
#The from __future__ imports ensure compatibility between python2.7 and 3.x
from __future__ import absolute_import
import os
import sys
import common
import error
import default_couplings

# The part of name used in namcouple to identify the component
NAM_COMP_NAMES = {'ATM':'atm', 'JNR':'jnr', 'OCN':'model01_O'}

# Dictionary containing the RMP mappings
RMP_MAPPING = {'Bi':'BILINEA',
               'CD':'CONSERV_DESTAREA',
               'CF':'CONSERV_FRACAREA',
               '1D':'OneD',
               'NB':'nomask_BILINEA',
               'Sc':'Scalar',
               'remove':'remove'}

# The long names and units used in cf_name_table.txt
CF_ATTR = {'_OCurx1':['surface_grid_eastward_sea_water_velocity', 'm s-1'],
           '_OCury1':['surface_grid_northward_sea_water_velocity', 'm s-1'],
           '_QnsOce':['surface_downward_non_shortwave_heat_flux', 'W m-2'],
           '_QsrOce':['surface_net_downward_shortwave_flux', 'W m-2'],
           '_OTaux1':['surface_downward_grid_eastward_stress', 'Pa'],
           '_OTauy1':['surface_downward_grid_northward_stress', 'Pa'],
           '_Runoff':['water_flux_into_ocean_from_rivers', 'kg m-2 s-1'],
           '_SSTSST':['sea_surface_temperature', 'K'],
           '_Wind10':['wind_speed_at_10m', 'm s-1'],
           'Antmass':['Antarctica_ice_mass', 'kg'],
           'ATMDUST':['Total_dust_deposition_rate', 'kg m-2 s-1'],
           'ATMPCO2':['Surface_level_of_CO2_tracer', 'mmr'],
           'BioChlo':['Ocean_near_surface_chlorophyll', 'kg m-3'],
           'BioCO2':['CO2_ocean_flux', 'kg m-2 s-1'],
           'BioDMS':['DMS_concentration_in_seawater', 'umol m-3'],
           'BotMlt':['Multi-category_Fcondtop', 'W m-2'],
           'Grnmass':['Greenland_ice_mass', 'kg'],
           'IceEvp':['Multi-category_water_evaporation_flux_where_sea_ice',
                     'kg m-2 s-1'],
           'IceFrc':['sea_ice_area_fraction', '1'],
           'IceFrd':['sea_ice-1st_order_regridded_ice_conc', '1'],
           'IceKn':['Multi-category sfc ice layer effective conductivity',
                    'W m-2 deg-1'],
           'IceTck':['Multi-category_ice_thickness', 'm'],
           'PndFrc':['Melt_pond_fraction', '1'],
           'PndTck':['Mean_melt_pond_depth', 'Pa'],
           'Runff1D':['water_flux_into_ocean_from_rivers', 'kg m-2 s-1'],
           'SnwTck':['surface_snow_amount', 'kg m-2'],
           'TepIce':['Multi-category_sfc_ice_layer_temperature', 'K'],
           'TopMlt':['Multi-category_Topmelt', 'W m-2'],
           'TotEvap':['water_evaporation_flux', '1'],
           'TotRain':['rainfall_flux', 'kg m-2 s-1'],
           'TotSnow':['snow_fall_flux', 'kg m-2 s-1'],
           'TsfIce':['Sea_ice_surface_skin_temperature', 'C']}

# The grid names for a ATMOS<->OCN coupling
ATM2OCN_GRIDS = {'ATM':{'u':'aum3', 'v':'avm3', 't':'atm3',
                        'r':'riv3', 's':'scal'},
                 'JNR':{'u':'jum3', 'v':'jvm3', 't':'jtm3',
                        'r':'riv3', 's':'scal'},
                 'OCN':{'u':'uor1', 'v':'vor1', 't':'tor1',
                        'r':'riv3', 's':'scal'}}

class NamcoupleEntry(object):
    '''
    Container to hold the information for one namcouple entry
    '''

    def __init__(self, name_out, field_id, grid, origin, dest, nlev, l_soil,
                 mapping, mapping_order, weight, l_hybrid, n_cpl_freq):
        self.name_out      = name_out
        self.field_id      = field_id
        self.grid          = grid
        self.origin        = origin
        self.dest          = dest
        self.nlev          = nlev
        self.l_soil        = l_soil
        self.mapping       = mapping
        self.mapping_order = mapping_order
        self.weight        = weight
        self.l_hybrid      = l_hybrid
        self.n_cpl_freq    = n_cpl_freq

    def __repr__(self):
        return repr((self.name_out, self.field_id, self.grid, self.origin,
                     self.dest, self.nlev, self.l_soil, self.mapping,
                     self.mapping_order, self.weight, self.l_hybrid,
                     self.n_cpl_freq))

class CfNameTableEntry(object):
    '''
    Container to hold the information for one entry in cf_name_table.txt
    '''

    def __init__(self, longname, unit):
        self.longname = longname
        self.unit     = unit

    def __repr__(self):
        return repr((self.longname, self.unit))

class StashInfo(object):
    '''
    For a given stash entry, this contains all the information we need here
    '''

    def __init__(self, longname, grid, level_f, level_l):
        self.longname = longname
        self.grid     = grid
        self.level_f  = level_f
        self.level_l  = level_l

    def __repr__(self):
        return repr((self.longname, self.grid, self.level_f, self.level_l))

def add_to_cpl_list(origin, l_hybrid, n_cpl_freq, send_list_raw):
    '''
    Add a new set of couplings to model_snd_list
    '''
    mapping   = None
    weighting = None
    model_snd_list = []
    if not isinstance(send_list_raw, list):
        send_list_raw = [send_list_raw]

    # Loop across the raw entries
    for cpl_entry_raw in send_list_raw:
        if cpl_entry_raw == 'default':
            # Entry will later be filled with the default options
            model_snd_list.append(
                NamcoupleEntry('default', '?', '?', origin, '?', '?', '?',
                               '?', '?', '?', l_hybrid, n_cpl_freq))
        else:
            # Default options
            nlev = 1
            mapping_order = -99

            if isinstance(cpl_entry_raw, str) and \
               cpl_entry_raw.find(';') > -1:
                # Split the input
                parts = cpl_entry_raw.split(';')
                # Check we have enough compulsory input
                if len(parts) < 6:
                    sys.stderr.write('[FAIL] Insufficent information in %s\n' %
                                     cpl_entry_raw)
                    sys.exit(error.MISSING_NAMCOUPLE_INPUT)
                # Set the fields we should know
                name_out = parts[0]
                field_id = int(parts[1])
                grid     = parts[2]
                dests    = parts[3].split('&')
                # Check if number of level are provided
                if len(parts) > 4:
                    nlev = int(parts[4])
                # Check if a mapping is provided
                if len(parts) > 5:
                    sub_parts = parts[5].split('&')
                    if sub_parts[0] in RMP_MAPPING:
                        mapping = RMP_MAPPING[sub_parts[0]]
                    else:
                        sys.stderr.write("[FAIL] Don't recognise this "
                                         "mapping: %s.\n" % parts[5])
                        sys.exit(error.UNRECOGNISED_MAPPING)
                    if len(sub_parts) > 1:
                        mapping_order = int(sub_parts[1])
                else:
                    if not mapping:
                        sys.stderr.write('[FAIL] Need to specify a mapping '
                                         'for first entry %s\n' %
                                         cpl_entry_raw)
                        sys.exit(error.MISSING_MAPPING)
                # Check if we have a coupling weighting
                if len(parts) > 6:
                    weighting = int(parts[6])
                else:
                    if not weighting:
                        sys.stderr.write('[FAIL] Need to specify a weighting '
                                         'for first entry.\n')
                        sys.exit(error.MISSING_WEIGHTING)

                # Loop over the destinations
                for dest in dests:
                    model_snd_list.append(
                        NamcoupleEntry(name_out, field_id, grid, origin,
                                       dest, nlev, '?', mapping, mapping_order,
                                       weighting, l_hybrid, n_cpl_freq))
                    # Just add to the default weighting
                    weighting += 2
            else:
                sys.stderr.write('[FAIL] the following coupling entry looks '
                                 'to be in the wrong format: %s\n' %
                                 cpl_entry_raw)
                sys.exit(error.WRONG_CPL_FORMAT)

    return model_snd_list

def print_run_info(run_info):
    '''
    Print the information in run_info
    '''
    sys.stdout.write('[INFO] Display the contents of run_info:\n')
    sys.stdout.write('[INFO] -------- Resolutions -------- \n')
    if 'ATM_grid' in run_info:
        sys.stdout.write('[INFO] Atmosphere:        %s (%d, %d)\n' %
                         (run_info['ATM_grid'], run_info['ATM_resol'][0],
                          run_info['ATM_resol'][1]))
    if 'JNR_grid' in run_info:
        sys.stdout.write('[INFO] Junior atmosphere: %s (%d, %d)\n' %
                         (run_info['JNR_grid'], run_info['JNR_resol'][0],
                          run_info['JNR_resol'][1]))
    if 'OCN_grid' in run_info:
        # If running ATM<->JNR coupling we can have an ocean resolution
        # without an ocean.
        if 'OCN_resol' in run_info:
            sys.stdout.write('[INFO] Ocean:             %s (%d, %d)\n' %
                             (run_info['OCN_grid'], run_info['OCN_resol'][0],
                              run_info['OCN_resol'][1]))
        else:
            sys.stdout.write('[INFO] Ocean:             %s\n' %
                             run_info['OCN_grid'])
    if 'riv3' in run_info:
        if run_info['riv3'] > 0:
            sys.stdout.write('[INFO] Number of rivers:  %d\n' %
                             run_info['riv3'])

    sys.stdout.write('[INFO] -------- Coupling frequencies (in mins) '
                     '-------- \n')
    comp_order = ['ATM', 'JNR', 'OCN']
    comp_list = []
    for component in comp_order:
        key = component + '_resol'
        if key in run_info:
            comp_list.append(component)
    for component1 in comp_list:
        for component2 in comp_list:
            if component2 == component1:
                break
            key=component2 + '2' + component1 + '_freq'
            sys.stdout.write('[INFO] %s -> %s:           %0.1f\n' %
                             (component2, component1,
                              (run_info[key][0]/60.0)))
            key2='l_hyb_stats_' + component2 + '2' + component1
            if key2 in run_info:
                if run_info[key2]:
                    sys.stdout.write('[INFO] %s -> %s for stats: %0.1f\n' %
                                     (component2, component1,
                                      (run_info[key][1]/60.0)))
            key=component1 + '2' + component2 + '_freq'
            sys.stdout.write('[INFO] %s -> %s:           %0.1f\n' %
                             (component1, component2,
                              (run_info[key][0]/60.0)))
            key2='l_hyb_stats_' + component1 + '2' + component2
            if key2 in run_info:
                if run_info[key2]:
                    sys.stdout.write('[INFO] %s -> %s for stats: %0.1f\n' %
                                     (component2, component1,
                                      (run_info[key][1]/60.0)))
    if 'ATM_grid' in run_info:
        sys.stdout.write('[INFO] -------- Atmosphere information -------- \n')
        sys.stdout.write('[INFO] Atmosphere levels:     %d\n' %
                         run_info['ATM_model_levels'])
        sys.stdout.write('[INFO] Soil levels:           %d\n' %
                         run_info['ATM_soil_levels'])
        sys.stdout.write('[INFO] STASHmaster directory: %s\n' %
                         run_info['STASHMASTER'])
    sys.stdout.write('[INFO] -------- Namcouple settings -------- \n')
    sys.stdout.write('[INFO] nlogprt: %d' % run_info['nlogprt'][0])
    if len(run_info['nlogprt']) == 2:
        sys.stdout.write(' %d\n' % run_info['nlogprt'][1])
    else:
        sys.stdout.write('\n')
    sys.stdout.write('[INFO] Executable list:\n')
    for execut in run_info['exec_list']:
        sys.stdout.write('[INFO]    - %s\n' % execut)
    if 'expout' in run_info:
        sys.stdout.write('[INFO] Fields with EXPOUT argument:\n')
        for field in run_info['expout']:
            sys.stdout.write('[INFO]    - %s\n' % field)
    if 'rmp_create' in run_info:
        sys.stdout.write('[INFO] Fields where remapping files will be '
                         'created are:\n')
        for field in run_info['rmp_create']:
            sys.stdout.write('[INFO]    - %s\n' % field)
    sys.stdout.write('[INFO] -------- Files -------- \n')
    sys.stdout.write('[INFO] File containing coupling frequencies: %s\n' %
                     run_info['SHARED_FILE'])
    if 'nemo_nl' in run_info:
        sys.stdout.write('[INFO] Default couplings determined from:    %s\n' %
                         run_info['nemo_nl'])

def _determine_grid(grid_num):
    '''
    Determine the grid type
    '''
    if grid_num < 6:
        grid = 't'
    elif grid_num == 18:
        grid = 'u'
    elif grid_num == 19:
        grid = 'v'
    elif grid_num == 21:
        # Land points will be put onto a T-grid
        grid = 't'
    else:
        sys.stderr.write('[FAIL] unrecognised grid=%d.\n' % grid_num)
        grid = None

    return grid

def _determine_levels(model_levels, soil_levels, grid_num, level_f, level_l):
    '''
    Determine the number of vertical levels
    '''
    # Determine if this field is in the soil/land
    if grid_num == 21:
        # This field is in the soil/land.
        l_soil = True
        # Determine if 1 level or soil levels
        if level_f == -1 and level_l == -1:
            # Only one level
            return 1, l_soil
        elif level_f == 8 and level_l == 9:
            # A soil field
            return soil_levels, l_soil
        else:
            sys.stderr.write('[FAIL] land-only field with level_f=%d and '
                             'level_l=%d is not recognised.\n' %
                             (level_f, level_l))
            return -99, l_soil
    else:
        # This field is in the atmosphere.
        l_soil = False
        # Determine if this is a 2d field
        if level_f == -1:
            # Only one level for 2d fields
            return 1, l_soil
        else:
            # Determine the first level
            if level_f in (10, 38, 40):
                first_lev = 0
            elif level_f == 1:
                first_lev = 1
            else:
                sys.stderr.write('[FAIL] unrecognised levelF=%d.\n' % level_f)
                first_lev = -99

            # Determine the last level
            if level_l in (2, 3, 11, 14):
                last_lev = model_levels
            elif level_l == 19:
                last_lev = model_levels + 1
            else:
                sys.stderr.write('[FAIL] unrecognised levelL=%d.\n' % level_l)
                last_lev = -99

            # Return the total number of levels
            if first_lev < 0 or last_lev < 0:
                return -99, l_soil
            else:
                return (last_lev - first_lev + 1), l_soil

def _coupling_freq(nam_entry, run_info):
    '''
    Determine the coupling frequency
    '''
    # Find the coupling frequency in run_info
    cpl_var = nam_entry.origin + '2' + nam_entry.dest + '_freq'
    if not cpl_var in run_info:
        sys.stderr.write('[FAIL] %s is not found in run_info for %s.\n' %
                         (cpl_var, nam_entry.name_out))
        sys.exit(error.NOT_FOUND_CPL_VAR)
    if len(run_info[cpl_var]) < nam_entry.n_cpl_freq:
        sys.stderr.write('[FAIL] not enough coupling frequencies '
                         'for %s.\n' % cpl_var)
        sys.exit(error.NOT_ENOUGH_CPL_FREQ)
    cpl_freq = run_info[cpl_var][nam_entry.n_cpl_freq]

    return cpl_freq

def _read_stashmaster(stashmaster_dir):
    '''
    Read the stashmaster file and store the information we need
    '''
    # Check that STASHmaster_A file exists
    stashmaster_a = stashmaster_dir + '/STASHmaster_A'
    if not os.path.exists(stashmaster_a):
        sys.stderr.write('[FAIL] failed to find STASHmaster_A at %s.\n' %
                         stashmaster_a)
        sys.exit(error.MISSING_STASHMASTER_A)

    # Open file and read it
    with common.open_text_file(stashmaster_a, 'r') as stashmaster_file:
        nline = 0
        grid_line = -99
        stashmaster_info = {}
        for line in stashmaster_file.readlines():
            if '1|' in line[0:2]:
                # Extract the section, item and name
                section = int(line[9:15])
                item    = int(line[16:22])
                name    = line[23:59].rstrip()
                # The stash code
                stash_code = 1000 * section + item
                # Determine the grid line I want to read
                grid_line = nline + 1
            if nline == grid_line:
                # Grid the grid information
                grid_num = int(line[23:29])
                level_f  = int(line[37:43])
                level_l  = int(line[44:50])
                # Store all the information in stashmaster_info
                stashmaster_info[stash_code] = StashInfo(name, grid_num,
                                                         level_f, level_l)
            # Move to next line
            nline += 1

    return stashmaster_info

def _snr2jnr_field_info(nam_entry, model_levels, soil_levels,
                        stashmaster_info):
    '''
    Field information for Snr<->Jnr hybrid coupling
    '''
    # Determine the name_in
    if nam_entry.dest == 'JNR':
        dest_ident = 'j'
    else:
        dest_ident = 's'
    name_in = nam_entry.name_out[0:5] + dest_ident + \
        nam_entry.name_out[6:9]

    # Determine if stash code is in stashmaster_info
    stash_code = int(nam_entry.name_out[0:5])
    if stash_code in stashmaster_info:
        # Determine which grid we're on
        grid = _determine_grid(stashmaster_info[stash_code].grid)
        if not grid:
            # There has been error
            sys.stderr.write('[FAIL] failure for stash code %d.\n' %
                             stash_code)
            sys.exit(error.UNRECOGNISED_GRID)
        # Determine the number of vertical levels and if field is
        # found in the atmosphere or the land/soil.
        nlev, l_soil = _determine_levels(model_levels, soil_levels,
                                         stashmaster_info[stash_code].grid,
                                         stashmaster_info[stash_code].level_f,
                                         stashmaster_info[stash_code].level_l)
        if nlev < 0:
            # There has been error
            sys.stderr.write('[FAIL] failure for stash code %d.\n' %
                             stash_code)
            sys.exit(error.UNRECOGNISED_LEVEL)
    else:
        sys.stderr.write('[FAIL] not found stash code %d in '
                         'STASHmaster information.\n' % stash_code)
        sys.exit(error.NOT_FOUND_STASH_CODE)

    return name_in, stashmaster_info[stash_code].longname, grid, nlev, l_soil

def _atm2ocn_field_info(nam_entry, cf_names, cf_table_num, n_cf_table):
    '''
    Field information for ATM<->OCN coupling
    '''
    # Determine the name_in
    name_in_comp = NAM_COMP_NAMES[nam_entry.origin]
    name_out_comp = NAM_COMP_NAMES[nam_entry.dest]
    name_in = nam_entry.name_out.replace(name_in_comp, name_out_comp)

    # Determine the cf_name_table.txt attributes
    cf_code = \
        nam_entry.name_out.replace(name_in_comp, '').split('_cat')[0]
    if cf_code in CF_ATTR:
        longname = CF_ATTR[cf_code][0]
        unit     = CF_ATTR[cf_code][1]
    else:
        sys.stdout.write('[WARNING] full name and units unknown for %s.\n'
                         % nam_entry.name_out)
        longname = "unknown_name"
        unit = "unknown_unit"

    # See if we already have this entry in CF table
    if cf_code in cf_table_num:
        cf_table_number = cf_table_num[cf_code]
    else:
        cf_names.append(CfNameTableEntry(longname, unit))
        n_cf_table += 1
        cf_table_num[cf_code] = n_cf_table
        cf_table_number = n_cf_table

    return name_in, cf_names, cf_table_number, cf_table_num, n_cf_table

def _checks_on_run_info(run_info):
    '''
    Run some checks on the data in run_info
    '''
    # If coupling contains both hybrid components, check the model_levels
    # are the same for both.
    if 'ATM_model_levels' in run_info and 'JNR_model_levels' in run_info:
        if run_info['ATM_model_levels'] != run_info['JNR_model_levels']:
            sys.stderr.write('[FAIL] model_levels for Snr (=%d) and Jnr '
                             '(=%d) are different.\n' %
                             (run_info['ATM_model_levels'],
                              run_info['JNR_model_levels']))
            sys.exit(error.DIFFERENT_MODEL_LEVELS)
    if 'ATM_soil_levels' in run_info and 'JNR_soil_levels' in run_info:
        if run_info['ATM_soil_levels'] != run_info['JNR_soil_levels']:
            sys.stderr.write('[FAIL] soil levels for Snr (=%d) and Jnr '
                             '(=%d) are different.\n' %
                             (run_info['ATM_soil_levels'],
                              run_info['JNR_soil_levels']))
            sys.exit(error.DIFFERENT_SOIL_LEVELS)

    # If stats are turned on, we want to sample the core fields for
    # stats at least as often as the stat fields.
    if 'l_hyb_stats_ATM2JNR' in run_info:
        if run_info['ATM2JNR_freq'][0] > run_info['ATM2JNR_freq'][1]:
            sys.stdout.write('[INFO] matching the main coupling frequency '
                             'between ATM->JNR to the stats frequency\n')
            run_info['ATM2JNR_freq'][0] = run_info['ATM2JNR_freq'][1]
    if 'l_hyb_stats_JNR2ATM' in run_info:
        if run_info['JNR2ATM_freq'][0] > run_info['JNR2ATM_freq'][1]:
            sys.stdout.write('[INFO] matching the main coupling frequency '
                             'between JNR->ATM to the stats frequency\n')
            run_info['JNR2ATM_freq'][0] = run_info['JNR2ATM_freq'][1]

    return run_info

def _write_header(common_env, nam_file, run_info, n_fields):
    '''
    Write the namcouple header
    '''
    # Create the header
    nam_file.write('#===================================================\n'
                   '# Control file for OASIS-MCT\n'
                   '# This file is created automatically using the drivers.\n'
                   '#---------------------------------------------------\n'
                   ' $NFIELDS\n'
                   '# This is the total number of fields being exchanged.\n'
                   '# For the definition of the fields, see under '
                   '$STRINGS keyword\n'
                   '#\n')
    nam_file.write('  %d\n' % n_fields)
    nam_file.write(' $END\n'
                   '#---------------------------------------------------\n'
                   ' $NBMODEL\n')
    arg1_list = ''
    arg2_list = ''
    for exec_name in run_info['exec_list']:
        arg1_list = arg1_list + ' ' + exec_name
        arg2_list = arg2_list + ' 99'
    nam_file.write('   %d%s%s\n' % (len(run_info['exec_list']), arg1_list,
                                    arg2_list))
    nam_file.write(' $END\n'
                   '#---------------------------------------------------\n'
                   ' $RUNTIME\n')
    nam_file.write('  %d\n' % common.setup_runtime(common_env))
    nam_file.write(' $END\n'
                   '#---------------------------------------------------\n'
                   ' $INIDATE\n'
                   '# This is the initial date of the run. This is '
                   'important only if\n'
                   '# FILLING analysis is used for a coupling field in '
                   'the run.\n'
                   '# The format is YYYYMMDD.\n'
                   '#\n'
                   '# RH: This may become important in all cases if we '
                   'want to\n'
                   '#     cross check to ensure all components start at '
                   'the same\n'
                   '#     date/time.\n'
                   '#\n'
                   '  00010101\n'
                   ' $END\n'
                   '#---------------------------------------------------\n'
                   ' $MODINFO\n'
                   '# Indicates if a header is encapsulated within the '
                   'field brick\n'
                   '# in binary restart files for all communication '
                   'techniques,\n'
                   '# (and for coupling field exchanges for PIPE, SIPC '
                   'and GMEM.\n'
                   '# (YES or NOT)\n'
                   '  NOT\n'
                   ' $END\n'
                   '#---------------------------------------------------\n'
                   ' $NLOGPRT\n'
                   '# Index of printing level in output file cplout: '
                   '0 = no printing\n'
                   '#  1 = main routines and field names when treated, '
                   '30 = complete output\n')
    if len(run_info['nlogprt']) == 2:
        # Time statistics information is on
        nam_file.write('  %d %d\n' % (run_info['nlogprt'][0],
                                      run_info['nlogprt'][1]))
    else:
        nam_file.write('  %d\n' % run_info['nlogprt'][0])
    nam_file.write(' $END\n'
                   '#---------------------------------------------------\n'
                   ' $CALTYPE\n'
                   '# Calendar type :  0      = 365 day calendar (no '
                   'leap years)\n'
                   '#                  1      = 365 day, or 366 days '
                   'for leap years, calendar\n'
                   '#                  n (>1) = n day month calendar\n'
                   '# This is important only if FILLING analysis is '
                   'used for a coupling\n'
                   '# field in the run.\n'
                   '#\n'
                   '  30\n'
                   ' $END\n'
                   '#===================================================\n'
                   '# Start of transient definitions\n'
                   '#---------------------------------------------------\n'
                   ' $STRINGS\n'
                   '#\n'
                   '# The above variables are the general parameters '
                   'for the experiment.\n'
                   '# Everything below has to do with the fields being '
                   'exchanged.\n')

def _write_transdef(nam_file, nam_entry, cpl_freq, n_field, longname):
    '''
    Write the TRANSDEF information
    '''
    # Choice sensible units to display the coupling frequency
    # (129,600s is 1.5 days, and 5,400s is 1.5 hours)
    if cpl_freq > 129600:
        # Display in units of days
        display_freq = int(cpl_freq / 86400 + 0.5)
        display_unit = 'days'
    elif cpl_freq > 5400:
        # Display in units of hours
        display_freq = int(cpl_freq / 3600 + 0.5)
        display_unit = 'hrs'
    else:
        # Display in units of minutes
        display_freq = int(cpl_freq / 60 + 0.5)
        display_unit = 'mins'

    # Information for coupling
    nam_file.write('#---------------------------------------------------\n')
    nam_file.write('# %s' % longname)
    if nam_entry.l_hybrid:
        nam_file.write(' (stash %s,%s)' % (nam_entry.name_out[0:2],
                                           nam_entry.name_out[2:5]))
    nam_file.write(' (weighting %d)\n' % nam_entry.weight)
    nam_file.write('# %s --> %s every %d%s (%ds)' %
                   (nam_entry.origin, nam_entry.dest, display_freq,
                    display_unit, cpl_freq))
    if nam_entry.nlev == 1:
        nam_file.write(', 1 level\n')
    else:
        nam_file.write(', %d levels\n' % nam_entry.nlev)
    nam_file.write('#---------------------------------------------------\n')

    # For scalar field the grid is not specified
    if nam_entry.mapping == 'Scalar':
        grid = '0'
    elif nam_entry.mapping == 'OneD':
        grid = '1'
    else:
        grid = nam_entry.grid.upper()

    # TRANSDEF line
    nam_file.write('# TRANSDEF: %s%s %s%s %d %d ' %
                   (nam_entry.origin, grid, nam_entry.dest, grid,
                    n_field, nam_entry.field_id))
    if nam_entry.mapping_order > 0:
        nam_file.write('%d ' % nam_entry.mapping_order)
    nam_file.write('###\n')

def _write_main_line(nam_file, nam_entry, cpl_freq, name_in,
                     cf_table_number, n_trans, cpl_restart_file,
                     run_info):
    '''
    Write the main namcouple line which contains the sent and
    received fields and the coupling frequency
    '''
    # See if this should be EXPOUT
    exp_type = 'EXPORTED'
    if 'expout' in run_info:
        if nam_entry.l_hybrid:
            name_match_str = nam_entry.name_out[0:6]
        else:
            name_match_str = nam_entry.name_out
        for expout_entry in run_info['expout']:
            if expout_entry == name_match_str:
                exp_type = 'EXPOUT'

    # Create the name_out string for all levels
    name_out_str = nam_entry.name_out
    name_in_str  = name_in
    if nam_entry.nlev > 1:
        for level in range(2, nam_entry.nlev+1):
            name_out_str = name_out_str + ':' + nam_entry.name_out[0:6] + \
                '{:03d}'.format(level)
            name_in_str  = name_in_str  + ':' + name_in[0:6] + \
                '{:03d}'.format(level)
    # The fields out and in
    nam_file.write(' %s %s ' % (name_out_str, name_in_str))
    # The cf_name_table.txt index, the frequency, number of
    # transformation, coupling restart file and EXPORTED/EXPOUT
    nam_file.write('%d %d %d %s  %s\n' % \
                       (cf_table_number, cpl_freq, n_trans,
                        cpl_restart_file, exp_type))

def _write_grid_info(nam_file, ocn_abrev, nam_entry, seq,
                     run_info, l_rmp_create):
    '''
    Write the grid information to namcouple file
    '''

    # Determine the grid names
    if nam_entry.origin == 'OCN' or nam_entry.dest == 'OCN':
        # We'll need a land-sea mask for this
        origin_grid = ATM2OCN_GRIDS[nam_entry.origin][nam_entry.grid]
        dest_grid   = ATM2OCN_GRIDS[nam_entry.dest][nam_entry.grid]
        if nam_entry.origin == 'OCN':
            origin_overlap = 2
            dest_overlap   = 0
        else:
            origin_overlap = 0
            dest_overlap   = 2
    else:
        # SNR<->JNR coupling
        origin_overlap = 0
        dest_overlap   = 0
        if nam_entry.origin == 'JNR':
            origin_start = 'j'
            dest_start   = 's'
        else:
            origin_start = 's'
            dest_start   = 'j'

        # Soil/land fields require a mask
        if nam_entry.l_soil:
            mid_name = ocn_abrev
        else:
            mid_name = 'nr'

        # Put parts of the grid names together
        origin_grid = origin_start + mid_name + nam_entry.grid
        dest_grid   = dest_start   + mid_name + nam_entry.grid

    # Scalar passing has very different arguments
    if nam_entry.mapping == 'Scalar':
        # Write the resolutions and grids
        nam_file.write(' 1 1 1 1 %s %s SEQ=+%d\n' % \
                           (origin_grid, dest_grid, seq))

        # Write the rest of the information
        nam_file.write(' R 0 R 0\n#\n BLASOLD\n#\n 1.0 0\n')
    elif nam_entry.mapping == 'OneD':
        # Determine resolution
        if origin_grid in run_info:
            data_len = run_info[origin_grid]
        else:
            sys.stderr.write('[FAIL] size of 1d grid %s is unknown.\n' %
                             origin_grid)
            sys.exit(error.UNKNOWN_1D_GRID_SIZE)
        # Write the resolutions and grids
        nam_file.write(' %d 1 %d 1 %s %s SEQ=+%d\n' % \
                       (data_len, data_len, origin_grid, dest_grid, seq))

        # Write the rest of the information
        nam_file.write(' R 0 R 0\n#\n BLASOLD\n#\n 1.0 0\n')
    else:
        # Determine the number of grid points in y-direction
        origin_resol_name = nam_entry.origin + '_resol'
        dest_resol_name = nam_entry.dest + '_resol'
        ny_origin = run_info[origin_resol_name][1]
        if nam_entry.grid == 'v' and (nam_entry.origin == 'ATM' or
                                      nam_entry.origin == 'JNR'):
            # An extra grid point is needed for atmosphere on v-grid.
            ny_origin += 1
        ny_dest = run_info[dest_resol_name][1]
        if nam_entry.grid == 'v' and (nam_entry.dest == 'ATM' or
                                      nam_entry.dest == 'JNR'):
            # An extra grid point is needed for atmosphere on v-grid.
            ny_dest += 1

        # Write the resolutions and grids
        nam_file.write(' %d %d %d %d %s %s SEQ=+%d\n' % \
                           (run_info[origin_resol_name][0], ny_origin,
                            run_info[dest_resol_name][0], ny_dest,
                            origin_grid, dest_grid, seq))

        # For now we're always using periodic boundary conditions
        nam_file.write(' P %d P %d\n' % (origin_overlap, dest_overlap))

        if l_rmp_create:
            # Create the rmp file
            nam_file.write('#\n LOCTRANS SCRIPR\n INSTANT\n')

            if nam_entry.mapping == 'CONSERV_DESTAREA':
                nam_file.write(' CONSERV LR SCALAR LATLON 50 DESTAREA ')
                if nam_entry.mapping_order == 2:
                    nam_file.write('SECOND\n')
                else:
                    nam_file.write('FIRST\n')
            elif nam_entry.mapping == 'CONSERV_FRACAREA':
                nam_file.write(' CONSERV LR SCALAR LATLON 50 FRACAREA ')
                if nam_entry.mapping_order == 2:
                    nam_file.write('SECOND\n')
                else:
                    nam_file.write('FIRST\n')
            elif nam_entry.mapping == 'BILINEA' or \
                    nam_entry.mapping == 'BILINEAR':
                nam_file.write(' BILINEAR LR SCALAR LATLON 1\n')
            else:
                sys.stderr.write('[FAIL] unable to create remapping file for '
                                 'mapping of %s\n' % nam_entry.mapping)
                sys.exit(error.MISSING_RMP_MAPPING)
        else:
            # MAPPING text
            nam_file.write('#\n MAPPING\n#\n')

            # Remapping file
            nam_file.write(' rmp_%s_to_%s_%s' % \
                               (origin_grid, dest_grid, nam_entry.mapping))
            if nam_entry.mapping.count('BILINEA') >= 1:
                nam_file.write('.nc\n')
            else:
                if nam_entry.mapping_order == 2:
                    nam_file.write('_2nd.nc\n')
                else:
                    nam_file.write('_1st.nc\n')

def _write_coupling_fields(nam_file, run_info, coupling_list):
    '''
    Write the fields in coupling_list to namcouple file
    '''
    # Key information is contained in run_info
    print_run_info(run_info)

    # Determine the abreviated ocean name used for the SNR<->JNR
    # coupling grids
    if 'OCN_grid' in run_info:
        ocn_res = int(run_info['OCN_grid'].replace('orca', ''))
        if ocn_res < 10:
            ocn_abrev = 'o' + str(ocn_res)
        else:
            ocn_abrev = str(ocn_res)
    else:
        # The problem is likely to be that this is a SNR<->JNR
        # coupling without an ocean, and so the ocean resolution
        # which is used in all the ancillaries etc needed to be
        # explicitly defined in the um app.
        sys.stderr.write('[FAIL] ocean resolution will need to be set. '
                         'Try setting the environment variable OCN_RES '
                         'in the um app.\n')
        sys.exit(error.NO_OCN_RESOL)

    # Initialise
    origin_old       = 'none'
    seq              = 0
    n_field          = 1
    cf_names         = []
    cf_table_num     = {}
    n_cf_table       = 0
    cpl_restart_file = 'atmos_restart.nc'
    stashmaster_info = None

    # Loop across all the coupling
    for nam_entry in coupling_list:

        # Determine if field should be removed
        if nam_entry.mapping != 'remove':

            # Determine if seq should be updated
            if nam_entry.origin != origin_old:
                seq += 1
                origin_old = nam_entry.origin

            # Determine the coupling frequency
            cpl_freq = _coupling_freq(nam_entry, run_info)

            # Determine if this is a hybrid field
            if nam_entry.l_hybrid:
                # Determine if STASHmaster_A file should be read
                if not stashmaster_info:
                    stashmaster_info = \
                        _read_stashmaster(run_info['STASHMASTER'])

                # Determine the base name_in, long name, grid and number
                # of vertical levels
                name_in, longname, nam_entry.grid, \
                    nam_entry.nlev, nam_entry.l_soil = \
                    _snr2jnr_field_info(nam_entry,
                                        run_info['ATM_model_levels'],
                                        run_info['ATM_soil_levels'],
                                        stashmaster_info)

                # Determine the cf_name_table.txt attributes
                cf_names.append(CfNameTableEntry(longname, 'unknown'))
                n_cf_table += 1
                cf_table_number = n_cf_table

            else:
                # Determine further field information
                name_in, cf_names, cf_table_number, cf_table_num, n_cf_table = \
                    _atm2ocn_field_info(nam_entry, cf_names, cf_table_num,
                                        n_cf_table)
                longname = cf_names[cf_table_number - 1].longname

            # See if remapping file needs creating
            l_rmp_create = False
            n_trans = 1
            if 'rmp_create' in run_info:
                if nam_entry.l_hybrid:
                    name_match_str = nam_entry.name_out[0:6]
                else:
                    name_match_str = nam_entry.name_out
                for create_entry in run_info['rmp_create']:
                    if create_entry == name_match_str:
                        l_rmp_create = True
                        n_trans += 1

            # Write the TRANSDEF information to namcouple
            _write_transdef(nam_file, nam_entry, cpl_freq, n_field, longname)

            # Write the line with field names and coupling frequency
            _write_main_line(nam_file, nam_entry, cpl_freq, name_in,
                             cf_table_number, n_trans, cpl_restart_file,
                             run_info)

            # Write the grid information
            _write_grid_info(nam_file, ocn_abrev, nam_entry, seq,
                             run_info, l_rmp_create)

            # Move to next field
            n_field += 1

    return cf_names

def _write_cf_name_table(cf_names):
    '''
    Write the cf_name_table.txt file
    '''
    # Open the file
    cf_file = common.open_text_file('cf_name_table.txt', 'w')

    # Write the header
    cf_file.write('# Maximum index of the table entries, total '
                  'number of indices\n')
    cf_file.write('%d %d\n' % (len(cf_names), len(cf_names)))
    cf_file.write('#Index, CF longname, unit\n')

    # Loop across the entries
    i_entry = 1
    for cf_entry in cf_names:
        cf_file.write(" %d  '%s' '%s'\n" % (i_entry, cf_entry.longname,
                                            cf_entry.unit))
        i_entry += 1

    # Close file
    cf_file.close()

def write_namcouple(common_env, run_info, coupling_list):
    '''
    Write the namcouple file
    '''
    # Run some check on the data in run_info
    run_info = _checks_on_run_info(run_info)

    # See if any default couplings need adding
    for nam_entry in coupling_list:
        if 'default' in nam_entry.name_out:
            coupling_list = \
                default_couplings.add_default_couplings(run_info,
                                                        coupling_list)
            break

    # Open the file
    nam_file = common.open_text_file('namcouple', 'w')

    # Create the header
    _write_header(common_env, nam_file, run_info, len(coupling_list))

    # Sort the coupling_list by weighting
    coupling_list = sorted(coupling_list,
                           key=lambda nam_entry: nam_entry.weight)

    # Write the coupling fields
    cf_names = _write_coupling_fields(nam_file, run_info, coupling_list)

    # Close file
    nam_file.close()

    # Write cf_name_table.txt file
    _write_cf_name_table(cf_names)

    # Now that namcouple has been created, we can create the transient
    # field namelist
    _, _ = common.exec_subproc('./OASIS_fields')
