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

GENERATE_SECTION1_ERROR = 1

def check_nfields(nfields, n_field_def):
    '''
    Takes in the value for nfields in the header, and the number of fields
    defined in the fields dictionary. If the first value is smaller than
    the second, we will redefine it as the second and write information
    to the user that this has happened
    '''
    if nfields >= n_field_def:
        return nfields
    sys.stdout.write('[INFO] The value for nfields in the namelist ({0}) is' \
                     ' smaller than the number of fields required for' \
                     ' coupling ({1}). Automatically redefinining nfields' \
                     ' to {1}\n'.format(nfields, n_field_def))
    return n_field_def

def check_nlogprt_val1(nlogprt_val1):
    '''
    The first value in nlogprt must be in 0,1,2,5,10,12,15,20,30. If it is
    set to a different value, will round to the next highest value
    '''
    nlogprt_val1 = int(nlogprt_val1)
    correct_values = [0, 1, 2, 5, 10, 12, 15, 20, 30]
    if nlogprt_val1 in correct_values:
        return nlogprt_val1
    if nlogprt_val1 >= 30:
        rval = 30
    else:
        for val in correct_values:
            if nlogprt_val1 <= val:
                rval = val
                break
    sys.stdout.write('[INFO] The user chosen value for nlogprt is {}, which'
                     ' is an invalid value. It has been reset to the next'
                     ' highest valid value, {}\n'.format(nlogprt_val1, rval))
    return rval

def check_nlogprt_val2(nlogprt_val2):
    '''
    The second value in nlogprt can be set to -1,0,1,2,3. The value -1
    indicates the Lucia tool will be run
    '''
    nlogprt_val2 = int(nlogprt_val2)
    if nlogprt_val2 not in [-1, 0, 1, 2, 3]:
        sys.stderr.write('[FAIL] The user chosen value for the second value' \
                         ' for nlogprt is {}. It must be -1, 0, 1, 2, 3\n'.
                         format(nlogprt_val2))
        sys.exit(GENERATE_SECTION1_ERROR)

def build_item(name, value, include_end=False):
    '''
    Build the item for the namelist file. Takes in the name, and the value
    for the variable. Optional value include_end to put the $END keyword. This
    is not required for O3-MCT4.0, but might be usefull
    '''
    name = '${}\n'.format(name.upper())
    value = ' {}\n'.format(value)
    item_string = '{}{}'.format(name, value)
    if include_end:
        item_string = '{}$END\n'.format(item_string)
    return '{}'.format(item_string)


def construct_section_one(header, size_fields_dict):
    '''
    Take in the header namelist dictionary and the size of the fields
    dictionary and construct section one, returing a string
    '''
    namcouple_str = ''
    # construct NFIELDS
    nfields = check_nfields(header['nfields'], size_fields_dict)
    namcouple_str += build_item('NFIELDS', nfields, include_end=True)

    # construct runtime
    namcouple_str += build_item('RUNTIME', header['runtime'],
                                include_end=True)

    # construct nlogprt
    nlogprt_val1 = header['nlogprt'][0]
    nlogprt_val2 = header['nlogprt'][1]
    nlogprt_val1 = check_nlogprt_val1(nlogprt_val1)
    check_nlogprt_val2(nlogprt_val2)
    nlogprt_str = '{} {}'.format(nlogprt_val1, nlogprt_val2)
    namcouple_str += build_item('NLOGPRT', nlogprt_str,
                                include_end=True)

    return namcouple_str
