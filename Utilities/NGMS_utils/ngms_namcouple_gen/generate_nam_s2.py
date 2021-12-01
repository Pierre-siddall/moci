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
'''
import sys

GENERATE_SECTION2_ERROR = 2

# The various model grids
GRIDS = {'tor1': 'ocn',
         'vor1': 'ocn',
         'uor1': 'ocn',
         'atm3': 'atm',
         'avm3': 'atm',
         'aum3': 'atm',
         'lfric': 'lfric'}

def str_to_list(input_value):
    '''
    Takes in a string or a list. If a list we return that list, otherwise we
    return an list of length one containing the input string
    '''
    if isinstance(input_value, str):
        rvalue = [input_value]
    else:
        rvalue = input_value
    return rvalue

def get_len_list_no_false(i_list):
    '''
    Returns the length of a list without any items that evaluate to false.
    '''
    return len([item for item in i_list if item])

def get_model_from_grid(grid_name):
    '''
    Get a model based on its grid name from the GRIDS dictionary
    '''
    try:
        model = GRIDS[grid_name]
    except KeyError:
        sys.stderr.write('[FAIL] Can not determine the model type for grid'
                         ' {}\n'.format(grid_name))
        sys.exit(GENERATE_SECTION2_ERROR)
    return model

def gen_section_two_l1(header_dict, field_dict, src_model):
    '''
    Take in the header dictionary, field dictionary, and the source model and
    return the first line of section two
    '''
    # The transform can sometime be a string, owing to the reading of a
    # namelist item with a single value list. In this case the number of
    # transforms is one
    if isinstance(field_dict['transform'], list):
        num_transforms = get_len_list_no_false(field_dict['transform'])
    else:
        num_transforms = 1
    line_1 = "{} {} 1 {} {} {} {}".format(field_dict['src_name'],
                                          field_dict['trg_name'],
                                          field_dict['cpl_freq'],
                                          num_transforms,
                                          header_dict['{}_restart'.format(
                                              src_model)],
                                          field_dict['fld_op'])
    return '{}\n'.format(line_1)

def gen_section_two_l2(header_dict, field_dict, src_model, dest_model):
    '''
    Take in the header dictionary, field dictionary, the source model and the
    destination model, and return the second line of section two
    '''
    lag = str(field_dict['lag'])
    if lag[0] != '-':
        lag = '+{}'.format(lag)
    seq = str(field_dict['seq'])
    if seq[0] != '-':
        seq = '+{}'.format(seq)
    line_2 = "{} {} {} {} {} {} LAG={} SEQ={}".format(
        header_dict['{}_t_dim'.format(src_model)][0],
        header_dict['{}_t_dim'.format(src_model)][1],
        header_dict['{}_t_dim'.format(dest_model)][0],
        header_dict['{}_t_dim'.format(dest_model)][1],
        field_dict['src_grid_name'], field_dict['trg_grid_name'],
        lag, seq)
    return ' {}\n'.format(line_2)

def gen_section_two_l3(header_dict, src_model, dest_model):
    '''
    Take in the header dictionary, source model and destination model and
    return the third line of section two
    '''
    if src_model == dest_model:
        error_str = "Source model and destination model have the same" \
                    " name - {}\n".format(src_model)
        sys.stderr.write(error_str)
        sys.exit(GENERATE_SECTION2_ERROR)
    src_pr = ('R', 'P')[header_dict['{}_periodic'.format(src_model)]]
    dest_pr = ('R', 'P')[header_dict['{}_periodic'.format(dest_model)]]
    if src_model == 'ocn':
        src_wrap = header_dict['ocn_wrap']
    elif src_model == 'atm':
        src_wrap = header_dict['atm_wrap']
    elif src_model == 'lfric':
        src_wrap = header_dict['lfric_wrap']
    if dest_model == 'ocn':
        dest_wrap = header_dict['ocn_wrap']
    elif dest_model == 'atm':
        dest_wrap = header_dict['atm_wrap']
    elif dest_model == 'lfric':
        dest_wrap = header_dict['lfric_wrap']
    line_3 = '{} {} {} {}'.format(src_pr, src_wrap, dest_pr, dest_wrap)
    return ' {}\n'.format(line_3)

def gen_section_two_l4(field_dict):
    '''
    Take in the field dictionary and return the fourth line of section two.
    Transops should appear on a single line, followed by a list of transforms
    on their own lines
    '''
    line_4 = ''
    # First we make sure that we always have a list of items
    transops = str_to_list(field_dict['transops'])
    transforms = str_to_list(field_dict['transform'])
    line_4 = ''
    for transform in [t for t in transforms if t]:
        line_4 = '{} {}'.format(line_4, transform)
    if line_4:
        line_4 = '{}\n'.format(line_4)
    for transop in transops:
        if transop:
            line_4 = '{} {}\n'.format(line_4, transop)
    return line_4

def gen_section_two_item(header_dict, field_dict):
    '''
    Take in a namelist dictionary for a header and field namelist and generate
    the corresponding namcouple entry. Takes also a string for source and
    destination models atm, ocn
    '''
    src_model = get_model_from_grid(field_dict['src_grid_name'])
    dest_model = get_model_from_grid(field_dict['trg_grid_name'])
    section_2_item = '{}{}{}{}{}'.format(
        '###\n',
        gen_section_two_l1(header_dict, field_dict, src_model),
        gen_section_two_l2(header_dict, field_dict, src_model, dest_model),
        gen_section_two_l3(header_dict, src_model, dest_model),
        gen_section_two_l4(field_dict))
    return section_2_item
