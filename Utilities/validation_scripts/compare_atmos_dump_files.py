#!/usr/bin/env python2.7
#
#*****************************COPYRIGHT******************************
#(C) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT.txt
# which you should have received as part of this distribution.
#*****************************COPYRIGHT******************************
"""
 CODE OWNER
   Stephen Haddad

 NAME
   compare_atmos_dump_files.py

Compare 2 UM dump files using the MULE API and the CUMF UM util based on MULE.
"""
import sys
import argparse

import mule
import um_utils.cumf

import validate_common

# The "lbegin" parameter of the lookup must be ignored for comparing the
# output of an NRUN with an equivalent CRUN. See Section 4.2 of UMDP F03 for
# more info
NRUN_NRUN_IGNORE_INDICES = range(1, 13) + [29]

def compare_files(fields_file_path_1,
                  fields_file_path_2,
                  stop_on_error,
                  list_errors,
                  instant_fields_only,
                  io_manager=None):
    """
    Main function to compare 2 UM dump files.

    Inputs:
    fields_file_path_1 - Path to first UM restart dump
    fields_file_path_2 - Path to second UM restart dump
    stop_on_error - If true, stop when the first error is encountered. If
                    false, all fields will be compared.
    list_errors - If true, a full list of errors will be printed. Otherwise,
                  only summary information will be output. Note that
                  if stop_on_error is true, this setting will be ignored as
                  the script will abort immediately if an error is found
                  and not output a list of errors.
    instant_fields_only - If true any non-instantaneous fields are ignored
                          when comparing fields in dump files.
    io_manager - an IO wrapper, which ensures output is sent to the correct
                 output destination. This is usually stdout/stderr, but
                 but for rose_ana tasks, goes through the rose_ana reporter
                 mechanism.
    
    Return values:
    status code - 0 if the 2 files match.
    """
    fields_file_1 = mule.load_umfile(fields_file_path_1)
    fields_file_2 = mule.load_umfile(fields_file_path_2)

    if not io_manager:
        io_manager = validate_common.ValidateIO()

    if instant_fields_only:
        #filter contents of the dump to only include instantaeous fields
        ff1_old_fields = fields_file_1.fields
        ff2_old_fields = fields_file_2.fields
        fields_file_1.fields = [f1 for f1 in ff1_old_fields if f1.lbtim < 10]
        fields_file_2.fields = [f2 for f2 in ff2_old_fields if f2.lbtim < 10]

    #these fields are important to ignore for nrun + nrun comparisons, as
    # they will differ in that case
    um_utils.cumf.COMPARISON_SETTINGS['ignore_templates']['lookup'] = \
        NRUN_NRUN_IGNORE_INDICES
    um_utils.cumf.COMPARISON_SETTINGS['ignore_missing'] = True


    io_manager.write_out('Comparing UM restart files using default '
                         'mule / CUMF comparison')
    comparison12 = um_utils.cumf.UMFileComparison(fields_file_1,
                                                  fields_file_2)

    number_of_fields = len(comparison12.field_comparisons)
    number_of_mismatches = \
        sum([1 for fc1 in comparison12.field_comparisons if not fc1.match])
    max_rms_error = comparison12.max_rms_diff_1
    status_code = 0
    if number_of_mismatches > 0:
        msg = '{0} of {1} fields do not match!\n'
        msg += 'max diff in norms: {0:g}'.format(max_rms_error[0])
        msg = msg.format(number_of_mismatches,
                         number_of_fields)
        status_code = 1
        if stop_on_error:
            sys.stderr.write(msg + '\n')
            error1 = validate_common.DataMismatchError()
            error1.file_name1 = fields_file_1
            error1.file_name2 = fields_file_2
            raise error1
        if list_errors:
            um_utils.cumf.full_report(comparison12)

    else:
        msg = 'All {0} fields match!\n'.format(number_of_fields)

    io_manager.write_both(msg)

    return status_code

def get_command_line_arguments():
    """
    input_path1, input_path2 = get_command_line_arguments()
    Process command line arguments
    """
    desc_msg = 'Compare dump files from 2 GA7 tasks.'
    parser = argparse.ArgumentParser(description=desc_msg)
    parser.add_argument('--input-path1', dest='input_path1')
    parser.add_argument('--input-path2', dest='input_path2')
    args1 = parser.parse_args()
    return (args1.input_path1, args1.input_path2)

def main():
    """Main function for compare_atmos_dump_files.py."""
    io_manager = validate_common.ValidateIO()
    io_manager.write_out('comparing data in dump files\n')
    input_path1, input_path2 = get_command_line_arguments()
    status_code = compare_files(fields_file_path_1=input_path1,
                                fields_file_path_2=input_path2,
                                stop_on_error=False,
                                list_errors=True,
                                instant_fields_only=False)
    exit(status_code)

if __name__ == '__main__':
    main()
