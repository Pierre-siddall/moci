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
import argparse
import copy
import sys
sys.path.append('../ngms_suite_lib')

import read_nl
import read_rose_app_conf

import generate_nam_s1
import generate_nam_s2

GENERATE_NAM_ERROR = 3


def build_namcouple(header, coupling_namelists):
    '''
    Build the namecouple file and return a string containing the namcouple
    file
    '''
    section_one = generate_nam_s1.construct_section_one(header,
                                                        len(coupling_namelists))
    namcouple_file = '{}'.format(section_one)
    start_strings = '##################\n###\n### Coupling fields\n###\n##################\n$STRINGS\n'
    namcouple_file = '{}{}'.format(namcouple_file, start_strings)
    for coupling_nl in coupling_namelists:
        i_section_two = generate_nam_s2.gen_section_two_item(header,
                                                             coupling_nl)
        namcouple_file = '{}{}'.format(namcouple_file, i_section_two)

    end_strings = '$END'
    namcouple_file = '{}{}'.format(namcouple_file, end_strings)

    return namcouple_file

def write_namcouple(file_contents, namfilename):
    '''
    Write the generated namcouple file contents to the file namfilename
    '''
    with open(namfilename, 'w') as nam_fh:
        nam_fh.write(file_contents)


def identify_namelists(namelists, model_types=('atm', 'ocn', 'coupling_table')):
    '''
    Separate out the header and coupling item namelists. We use a key of
    model times to identify the namelists used for coupling
    '''
    header = copy.deepcopy(namelists['namcheader'])
    coupling_namelists = []
    for key, value in namelists.items():
        if key[:3] in model_types or key[:14] in model_types:
            coupling_namelists.append(copy.deepcopy(value))

    return header, coupling_namelists


def load_data(datafile, mode):
    '''
    Load the data from either a fortran namelist file, or from a rose app
    conf file
    '''
    if mode == 'rose_app_conf':
        rvalue, result_dict = read_rose_app_conf.read_rose_app_conf(datafile)
        try:
            namelists = result_dict['namelist']
        except KeyError:
            namelists = {}
    elif mode == 'namelist':
        rvalue, namelists = read_nl.read_nl(datafile)
    else:
        sys.stderr.write('[FAIL] The file loading mode {} is not valid\n'
                         '  The mode must be either:\n'
                         '      rose_app_conf\n'
                         '      namelist\n'.format(mode))
        sys.exit(GENERATE_NAM_ERROR)
    if rvalue:
        sys.stderr.write('[FAIL] There has been an error loading file {}\n'.
                         format(datafile))
        sys.exit(GENERATE_NAM_ERROR)
    return namelists

def gather_arguments():
    '''
    Gather the command line arguments to the script and return a parse_args
    object
    '''
    parser = argparse.ArgumentParser(
        description='Convert a fortran namelist, or rose-app.conf file from' \
        ' a coupled model configuration into a namcouple file')
    parser.add_argument('-o', '--output_file',
                        action='store',
                        dest='namcouple_fn', default='namcouple',
                        help='Filename for the namcouple file produced')
    parser.add_argument('mode',
                        choices=('namelist', 'rose_app_conf'),
                        help='Select the type of input file')
    parser.add_argument('input_file',
                        help='The input file from which the namecouple is to' \
                        ' be produced')
    return parser.parse_args()


def generate_nam(inputfile, outputfile, mode):
    '''
    Interface function to generate the namcouple file, to allow this to be used
    as both a module and interactively. Takes as arguments the input file name,
    output file name, and mode {'namelist', 'rose_app_conf'} depending on the
    file type
    '''
    namelist_data = load_data(inputfile, mode)
    header_namelist, coupling_namelists = identify_namelists(namelist_data)
    namcouple_contents = build_namcouple(header_namelist, coupling_namelists)
    write_namcouple(namcouple_contents, outputfile)


def main():
    '''
    Main function when running interactively
    '''
    arguments = gather_arguments()
    generate_nam(arguments.input_file,
                 arguments.namcouple_fn,
                 arguments.mode)


if __name__ == '__main__':

    main()
