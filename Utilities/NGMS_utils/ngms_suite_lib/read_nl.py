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

# we use the functions to manipulate variables from read rose_app_conf
import os
import read_nl_lib

def read_nl_file(infile):
    '''
    Read in a fortran namelist file
    '''
    namelist = []
    with open(infile, 'r') as nl_fh:
        current_item = []
        for line in nl_fh.readlines():
            line = line.strip()
            if not line:
                # ignore any empty line
                pass
            elif line[0] == '&':
                # Turn the name into an ini format so it matches what is
                # expected in read_rose_app_conf
                name = '[namelist:{}]'.format(line[1:])
                current_item.append(name)
            elif line[0] == '/':
                # This is the end of the reading
                namelist.append(current_item)
                current_item = []
            else:
                # if the last element of the line is a comma it needs to be
                # removed
                if line[-1] == ',':
                    line = line[:-1]
                current_item.append(line)
    return namelist


def read_nl(filename):
    '''
    Take in a path to a fortran namelist file, and returns a dictionary of the
    values contained within. Will return 0 and a dictionary if successful,
    and 1 and an empty dictionary if the file isnt found. This can be considered
    the main function
    '''
    if not os.path.isfile(filename):
        return 1, {}
    namelist = read_nl_file(filename)
    nl_dict = read_nl_lib.variable_dict('namelist', namelist)
    return 0, nl_dict

if __name__ == '__main__':
    import sys
    _, NAMELIST = read_nl(sys.argv[1])
    import pprint
    pprint.pprint(NAMELIST)
