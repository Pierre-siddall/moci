#!/usr/bin/env python3

'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2017-2025 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************

 NAME
   compare_nemo_stat.py

 USAGE
   Implements function to compare 2 NEMO solver.stat or run.stat (NEMO4.0) files

'''
import os
import re
import abc

import test_common


class NemoStatMismatchError(Exception):
    '''
    Error triggered when timesteps in solver.stat or run.stat files
    have differing norm values
    '''

    def __init__(self, msg=None):
        Exception.__init__(self)
        if msg:
            self.message = msg
        else:
            self.message = 'Values in the following .stat files do not match:'
        self.fname1 = 'unknown'
        self.fname2 = 'unknown'

    def __str__(self):
        self.message += '\n\tFile 1: {fname1}\n\tFile 2: {fname2}'
        self.message = self.message.format(**self.__dict__)
        return str(self.message)


class StatFileFmt(object):
    '''
    Base class for formatting of a single timestep line from a .stat file
    '''
    __metatclass__ = abc.ABCMeta

    REGEX_VAR = r'(\S+)\s*:\s+'
    REGEX_INT = r'(-?\d+)\s*'
    REGEX_FLOAT = r'(-?\d+\.\d+E[-+]\d+)\s*'

    @classmethod
    def match_fmt(cls, text_line):
        '''
        Class method - Return the class if the given text_line <type str>
                       matches the class format string, else return None.
        '''
        if cls().get_match_groups(text_line) is None:
            return None
        return cls()

    @abc.abstractproperty
    def _line_fmt(self):
        '''
        Placeholder for text line format string.
        Return <type str> - A format string to result in a re.match().groups()
                            list of alternately vairables and their values
        '''
        raise NotImplementedError(
            msg='File format not recongnised - cannot parse text'
        )

    def get_match_groups(self, line):
        '''
        Return re.match().groups() representing a list of alternatively
        variables and their values.
        '''
        try:
            groups = re.match(self._line_fmt, line.strip()).groups()
        except AttributeError:
            groups = None
        return groups


class SolverStatFmt(StatFileFmt):
    ''' Subclass of StatFileFmt to represent a line from solver.stat '''

    @property
    def _line_fmt(self):
        ''' Return a format string to match a line from solver.stat file '''
        return r'{v}{i}{v}{i}{v}{f}{v}{f}'.format(v=SolverStatFmt.REGEX_VAR,
                                                  i=SolverStatFmt.REGEX_INT,
                                                  f=SolverStatFmt.REGEX_FLOAT)


class RunStatFmt(StatFileFmt):
    ''' Subclass of StatFileFmt to represent a line from run.stat '''

    @property
    def _line_fmt(self):
        ''' Return a format string to match a line from run.stat.file '''
        return '{v}{i}{v}{f}{v}{f}{v}{f}{v}{f}'.format(v=RunStatFmt.REGEX_VAR,
                                                       i=RunStatFmt.REGEX_INT,
                                                       f=RunStatFmt.REGEX_FLOAT)


class NemoTimestep(object):
    ''' Container for values held for a single timestep read in from file '''
    __metatclass__ = abc.ABCMeta

    COMP_TOLERANCE = 1e-8

    def __init__(self, text_line1, timestep_num_offset=0):
        '''
        Constructor for NemoTimestep object.

        obj1 = NemoTimeStep(text_line1, timestep_num_offset)

        Arguments:
           text_line1          - Line of test from the stat file to parse
           timestep_num_offset - Offset to add to timestep number.
                                 This is for comparing runs with different
                                 timesteps numbers for the same model time.
        '''
        self.norms = {}
        for filetype in StatFileFmt.__subclasses__():
            ts = filetype.match_fmt(text_line1)
            if ts is not None:
                self.set_attributes(ts.get_match_groups(text_line1))
                break
        try:
            self.timestep_num += timestep_num_offset
        except AttributeError:
            pass

    def __str__(self):
        ''' Return a human readable string description of the timestep '''
        description = '\nTimestep: {}\n'.format(self.timestep_num)
        try:
            description += 'No. of iterations: {}\n'.format(self.num_iterations)
        except AttributeError:
            pass
        for var, val in sorted(self.norms.items()):
            description += '{} = {}\n'.format(var, val)

        return description + '\n'

    def __eq__(self, other):
        for norm in self.norms:
            if norm not in other.norms:
                raise NemoStatMismatchError(
                    msg='List of available norms do not match:'
                )
            if abs(self.norms[norm] - other.norms[norm]) > \
                    NemoTimestep.COMP_TOLERANCE:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def set_attributes(self, match_groups):
        '''
        Set the attibutes of the object:
            self.timestep_num   <type int>   - Timestep number
            self.num_iterations <type int>   - Number of iterations
                                               (solver.stat only)
            self.norms          <type float> - Norms values to be compared

        Arguments:
            match_groups <type list> - A list of alternatively variables
                                       and their values.
                                       e.g. The return from a call to
                                       re.match().groups()
        '''
        iterator = iter(match_groups)
        for var in iterator:
            if var == 'it':
                self.timestep_num = int(next(iterator))
            elif var == 'iter':
                self.num_iterations = int(next(iterator))
            else:
                self.norms[var] = float(next(iterator))

    def get_diffs(self, other):
        '''
        Return a <type dict> containing diff values for the norms
        available at each timestep.

        Arguments:
            other <type NemoTimestep> Comparator timerstep

        Return <type dict {norm: diff}> Differences for each norm available
        '''
        diffs = {}
        for norm in self.norms:
            diffs[norm] = abs(self.norms[norm] - other.norms[norm])
        return diffs


def parse_nemo_stat_file(path1, offset=0):
    '''
    Parse a NEMO solver.stat or run.stat file

    Arguments:
        path1  - Path to NEMO .stat file
        offset - Offset to add to timestep numer, for later comparison
                 purposes.  See compare_nemo_stat_files() for more details.

    Return <type list of <type NemoTimestep>>
    '''
    timestep_list = []
    with open(path1) as stat_file:
        for line1 in stat_file:
            timestep_list.append(NemoTimestep(line1, offset))
    return timestep_list


def compare_timestep_lists(timestep_list1, timestep_list2,
                           stop_on_error):
    '''
    Arguments:
        timestep_list1 <type list of <type NemoTimestep>>
        timestep_list2 <type list of <type NemoTimestep>>
        stop_on_error  <type bool> Stop comparing timesteps when an
                                   error is found

    Return <type tuple (<int>  Number of matching timesteps compared,
                        <list> Timestep numbers which did not match,
                        <dict> Maximum errors for each norm value) >

    Errors:
       NemoStatMismatchError - Raised if an error is found and
                               stop_on_error is True
    '''
    num_comps = 0
    mismatches = []
    max_errs = {}
    for norm in timestep_list1[0].norms:
        max_errs[norm] = 0.0

    # Create list of all timestep combinations
    ts_combos = [(ts1, ts2)
                 for ts1 in timestep_list1
                 for ts2 in timestep_list2
                 if ts1.timestep_num == ts2.timestep_num]
    for ts1, ts2 in ts_combos:
        if ts1 != ts2:
            if stop_on_error:
                raise NemoStatMismatchError()
            mismatches.append(ts1.timestep_num)
            diffs = ts1.get_diffs(ts2)
            for var in max_errs:
                if diffs[var] > max_errs[var]:
                    max_errs[var] = diffs[var]

    return len(ts_combos), mismatches, max_errs


def compare_nemo_stat_files(nemo_stat_file1, nemo_stat_file2,
                            list_errors,
                            stop_on_error,
                            nemo_stat_file2_offset,
                            io_manager):
    '''
    Compare two NEMO .stat files, as given by nemo_stat_file1
    and nemo_stat_file2

    Arguments:
       nemo_stat_file1 <type str>        - Path to first .stat file
       nemo_stat_file2 <type str>        - Path to second .stat file
       list_errors <type bool >          - Reproduce the list of mismatched
                                           timetep numbers upon completion
       stop_on_error <type_bool>         - Stop on finding the first error
       nemo_stat_file2_offset <type int> - Offset the timestep number in the
                                           second file.
                                           This allows Nrun-CRun comparison
                                           where the model time is the same but
                                           the timestep number may not be.

    Return <type int> 0 if no errors, non-zero if errors found
    '''
    if not io_manager:
        io_manager = test_common.TestIO()

    timestep_list1 = parse_nemo_stat_file(nemo_stat_file1)
    timestep_list2 = parse_nemo_stat_file(nemo_stat_file2,
                                          offset=nemo_stat_file2_offset)
    io_manager.write_out('{} timesteps found in file 1'.
                         format(len(timestep_list1)))
    io_manager.write_out('{} timesteps found in file 2'.
                         format(len(timestep_list2)))
    io_manager.write_out('File2 timesteps adjusted by an offset of {}'.
                         format(nemo_stat_file2_offset))
    try:
        num_comps, mismatches, max_errs = \
            compare_timestep_lists(timestep_list1, timestep_list2,
                                   stop_on_error)
    except NemoStatMismatchError as err:
        err.fname1 = nemo_stat_file1
        err.fname2 = nemo_stat_file2
        raise err

    io_manager.write_out('{} matching timesteps found'.format(num_comps))
    intro_msg = \
        'Comparing norm values with tolerance {}'
    intro_msg = intro_msg.format(NemoTimestep.COMP_TOLERANCE)
    io_manager.write_out(intro_msg)

    ret_val = 0
    if len(mismatches) == 0:
        if num_comps > 0:
            msg = 'All {} corresponding timestep(s) have equal solver values'
            io_manager.write_out(msg.format(num_comps))
        else:
            msg = 'No corresponding timesteps found'
            io_manager.write_both(msg.format(num_comps))
            ret_val = 1
    else:
        msg = '{} of {} corresponding timestep have differing ' \
              'solver values\n'.format(len(mismatches), num_comps)
        errors = '\n\t'.join(['{} error = {}'.format(k, v)
                              for k, v in max_errs.items()])
        msg += 'Maximum errors:\n\t' + errors

        if list_errors:
            io_manager.write_out(
                'List of timesteps with different solver values:'
            )
            for tstep in mismatches:
                io_manager.write_out('\tTimestep {}'.format(tstep))
        ret_val = 2
        io_manager.write_both(msg)

    return ret_val


def compare_solver_stat_files(nemo_solver_file1, nemo_solver_file2,
                              list_errors,
                              stop_on_error,
                              nemo_solver_file2_offset,
                              io_manager):
    '''
    NEMO3.6 (GO6) legacy method.
    This function has been reworked and renamed for relevance since
    NEMO4.0 replaced solver.stat with run.stat.

    Return call to compare_nemo_stat_files() only.
    '''
    return compare_nemo_stat_files(nemo_solver_file1, nemo_solver_file2,
                                   list_errors,
                                   stop_on_error,
                                   nemo_solver_file2_offset,
                                   io_manager)
