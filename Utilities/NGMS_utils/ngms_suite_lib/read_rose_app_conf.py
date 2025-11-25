#!/usr/bin/env python3
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2021-2025 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
'''

import os
import re
import read_nl_lib


def read_file(infile):
    '''
    Read in either [file], [env], [command] or [naemlist] items from the
    rose app conf file
    '''
    types = {'file': [],
             'env': [],
             'command': [],
             'namelist': []}
    with open(infile, 'r') as rose_app_conf:
        current_item = []
        first_item = True
        ignore_item = False
        for line in rose_app_conf.readlines():
            if line.startswith('meta') or line.startswith('import'):
                pass
            elif line[:2] == '[!':
                ignore_item = True
            elif line[0] == '[':
                ignore_item = False
                if first_item:
                    first_item = False
                else:
                    types[current_type].append(current_item)
                    current_item = []
                # get the type from the [] line
                match = re.match(r'\[(\w+).*', line)
                current_type = match.group(1)
                current_item.append(line.strip())
            elif line[0] == '!':
                pass
            elif '=' in line and not ignore_item:
                current_item.append(line.strip())
            else:
                pass
    types[current_type].append(current_item)
    return types


def read_rose_app_conf(filename):
    '''
    Takes in a path to rose app conf file, and returns a dictionary of the
    values contained within. Will return 0 and a dictionary if successful,
    and 1 and an empty dictionary if the file isnt found. This can be considered
    the main function
    '''
    if not os.path.isfile(filename):
        return 1, {}
    types = read_file(filename)
    result_dict = {}
    for key, value in types.items():
        if value:
            result_dict[key] = read_nl_lib.variable_dict(key, value)
        else:
            result_dict[key] = {}
    return 0, result_dict


if __name__ == '__main__':
    import sys
    import pprint

    _, ROSE_APP_CONF_DICT = read_rose_app_conf(sys.argv[1])
    pprint.pprint(ROSE_APP_CONF_DICT)
