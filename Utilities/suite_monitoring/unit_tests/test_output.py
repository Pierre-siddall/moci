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
    test_output.py

DESCRIPTION
    Unit test the rates_out.py module
'''


import unittest
import io
try:
    # mock is integrated into unittest as of Python 3.3
    import unittest.mock as mock
except ImportError:
    # mock is a standalone package (back-ported)
    import mock

import rates_out
import rates_lib

class FilterRates(unittest.TestCase):
    '''
    Test the filtering of the rates to provide output
    '''
    def setUp(self):
        # we need a list of rates objects, use the same input for all the
        # tests so we can see what is going on. These aren't real rates,
        # but it makes it easy to see whats going on.
        self.input_rates = []
        for i in range(6):
            self.input_rates.append(
                rates_lib.RATES._make(5*[i]))

    def test_calculate_start_end_full(self):
        '''
        Check that when we don't want a filter the start and end dates are
        correct
        '''
        expected_output = (0, 5)
        self.assertEqual(
            rates_out.calculate_start_and_end(
                self.input_rates, None, None),
            expected_output)

    def test_calculate_start_end_given(self):
        '''
        Test a given start and end date with positive values
        '''
        expected_output = (10, 12)
        self.assertEqual(
            rates_out.calculate_start_and_end(
                self.input_rates, 10, 12),
            expected_output)

    def test_calculate_start_end_negative(self):
        '''
        Test a givens tart and end date with negative vales
        '''
        expected_output = (1, 4)
        self.assertEqual(
            rates_out.calculate_start_and_end(
                self.input_rates, -4, -1),
            expected_output)

    def test_filter_full(self):
        '''
        Test the filter using full output, which is the default call
        '''
        expected_output = []
        for i in range(6):
            expected_output.append(
                rates_lib.RATES._make(5*[i]))
        self.assertEqual(
            rates_out.filter_rates(
                self.input_rates), tuple(expected_output))

    def test_filter_start_end_given(self):
        '''
        Filter the results given start and end dates
        '''
        expected_output = []
        for i in range(1, 5):
            expected_output.append(
                rates_lib.RATES._make(5*[i]))
        self.assertEqual(
            rates_out.filter_rates(
                self.input_rates, 1, 4), tuple(expected_output))

    def test_filter_start_end_negative(self):
        '''
        Filter the results given negative start and end dates
        '''
        expected_output = []
        for i in range(1, 5):
            expected_output.append(
                rates_lib.RATES._make(5*[i]))
        self.assertEqual(
            rates_out.filter_rates(
                self.input_rates, -4, -1), tuple(expected_output))

class HeaderKeys(unittest.TestCase):
    '''
    Check that the header keys still say what we want them to
    '''
    def test_key_title(self):
        '''
        Test the KEY_TITLE
        '''
        expected_key = 'Output key:\n'
        self.assertEqual(
            rates_out.KEY_TITLE, expected_key)

    def test_key_raw(self):
        '''
        Test the KEY_RAW key for the raw rates header
        '''
        expected_key = '  effr: Effective rate\n' \
                       '  cplr: Coupled model rate\n' \
                       '  cpqr: Coupled and Queuing rate\n' \
                       '  cpwr: Coupled and Waiting rate\n'
        self.assertEqual(
            rates_out.KEY_RAW, expected_key)

    def test_key_decayed(self):
        '''
        Test the KEY_DECAYED for the decayed rates header
        '''
        expected_key = '  deff: Decayed effective rate\n' \
                       '  dcpl: Decayed coupled model rate\n' \
                       '  dcpq: Decayed Coupled and Queuing rate\n' \
                       '  dcpw: Decayed Coupled and Waiting rate\n'
        self.assertEqual(
            rates_out.KEY_DECAYED, expected_key)

    def test_key_days(self):
        '''
        Test the KEY_DAYS for the expected output
        '''
        expected_key = '  days: Number of days the suite has been running\n'
        self.assertEqual(
            rates_out.KEY_DAYS, expected_key)

    def test_key_summary(self):
        '''
        Test the KEY_SUMMARY for the expected output
        '''
        expected_key = '  last: Last cycle run\n' \
                       '  ravg: Avergage rate\n' \
                       '  decd: Last decayed value\n'
        self.assertEqual(
            rates_out.KEY_SUMMARY, expected_key)

    def test_key_detail(self):
        '''
        Test the KEY_DETAIL for the expected output
        '''
        expected_key = '  intp: Last interpolated rate\n' \
                       '  davg: Average decayed value\n'
        self.assertEqual(
            rates_out.KEY_DETAIL, expected_key)


class RawRates(unittest.TestCase):
    '''
    Check the output from the raw rates function. We need to test formatted
    and unformatted
    '''
    def setUp(self):
        '''
        Set up the tests
        '''
        self.input_rates = []
        for i in range(2):
            self.input_rates.append(
                rates_lib.RATES._make(5*[i]))

    def test_raw_unformatted(self):
        '''
        Test display of unformatted raw data
        '''
        expected_output = '0 0 0 0 0\n' \
                          '1 1 1 1 1\n'

        with mock.patch('sys.stdout', new=io.StringIO()) as patch_output:
            rates_out.print_raw_rates(self.input_rates, formatted=False)
            self.assertEqual(patch_output.getvalue(), expected_output)

    def test_raw_formatted(self):
        '''
        Test the display of formatted raw data
        '''
        expected_output = rates_out.KEY_TITLE
        expected_output += rates_out.KEY_DAYS
        expected_output += rates_out.KEY_RAW
        expected_output += "{:>8s} {:>8s} {:>8s} {:>8s} {:>8s}\n". \
                          format("days", "effr", "cplr", "cpqr", "cpwr")
        expected_output += '{:8.1f} {:8.2f} {:8.2f} {:8.2f} {:8.2f}\n'. \
                           format(0, 0, 0, 0, 0)
        expected_output += '{:8.1f} {:8.2f} {:8.2f} {:8.2f} {:8.2f}\n'. \
                           format(1, 1, 1, 1, 1)
        with mock.patch('sys.stdout', new=io.StringIO()) as patch_output:
            rates_out.print_raw_rates(self.input_rates, formatted=True)
            self.assertEqual(patch_output.getvalue(), expected_output)


class InterpolatedRates(unittest.TestCase):
    '''
    Check the output from the interpolated rates function. We need to test
    formatted and unformatted
    '''
    
    def setUp(self):
        '''
        Set up the tests
        '''
        self.input_rates = []
        for i in range(2):
            self.input_rates.append(
                rates_lib.RATES._make(5*[i]))
        self.interval = 0.5
        self.decay_constant = 0.5

    def test_interpolated_unformatted(self):
        '''
        Test display of unformatted interpolated data
        '''
        expected_output = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n'
        expected_output += '0.5 0.5 0.5 0.5 0.5 0.25 0.25 0.25 0.25\n'
        expected_output += '1.0 1.0 1.0 1.0 1.0 0.625 0.625 0.625 0.625\n'

        with mock.patch('sys.stdout', new=io.StringIO()) as patch_output:
            rates_out.print_interpolated_rates(self.input_rates,
                                               self.interval,
                                               self.decay_constant,
                                               formatted=False)
            self.assertEqual(patch_output.getvalue(), expected_output)

    def test_interpolated_formatted(self):
        '''
        Test display of formatted interpolated data
        '''
        control = "{:8.1f}" + " {:8.2f}" * 8 + "\n"
        expected_output = rates_out.KEY_TITLE
        expected_output += rates_out.KEY_DAYS
        expected_output += rates_out.KEY_RAW
        expected_output += rates_out.KEY_DECAYED
        expected_output += "{:>8s} {:>8s} {:>8s} {:>8s} {:>8s} {:>8s}" \
                           " {:>8s} {:>8s} {:>8s}\n".format(
                               "days", "effr", "cplr", "cpqr", "cpwr", "deff",
                               "dcpl", "dcpq", "dcpw")
        expected_output += control.format(
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        expected_output += control.format(
            0.5, 0.5, 0.5, 0.5, 0.5, 0.25, 0.25, 0.25, 0.25)
        expected_output += control.format(
            1.0, 1.0, 1.0, 1.0, 1.0, 0.625, 0.625, 0.625, 0.625)

        with mock.patch('sys.stdout', new=io.StringIO()) as patch_output:
            rates_out.print_interpolated_rates(self.input_rates,
                                               self.interval,
                                               self.decay_constant,
                                               formatted=True)
            self.assertEqual(patch_output.getvalue(), expected_output)


class SummaryRates(unittest.TestCase):
    '''
    Test the printing of the summary. Remember there is formatted summary,
    formatted detail, unformatted summary, and unformatted detail.
    '''
    maxDiff = None
    def setUp(self):
        '''
        Set up the tests
        '''
        self.input_rates = []
        for i in range(2):
            self.input_rates.append(
                rates_lib.RATES._make(5*[i]))
        self.interval = 0.5
        self.decay_constant = 0.5
        self.suite_name = 'u-ni735'
        self.job = 'cyclejob'
        self.items = ['effective',
                      '{}'.format(self.job),
                      '{}_queue'.format(self.job),
                      '{}_wait'.format(self.job)]

    def test_unformatted_summary(self):
        '''
        Test the unformatted summary
        '''
        expected_output = '1.0 1 0.5 0.625\n' * 4
        with mock.patch('sys.stdout', new=io.StringIO()) as patch_output:
            rates_out.print_summary(self.input_rates,
                                    self.suite_name,
                                    self.interval,
                                    self.decay_constant,
                                    self.job,
                                    formatted=False,
                                    detailed=False)
            self.assertEqual(patch_output.getvalue(), expected_output)

    def test_unformatted_detail(self):
        '''
        Test the unformatted detail summary
        '''
        expected_output = '1.0 1 0.5 0.625 1.0 0.2916666666666667\n' * 4
        with mock.patch('sys.stdout', new=io.StringIO()) as patch_output:
            rates_out.print_summary(self.input_rates,
                                    self.suite_name,
                                    self.interval,
                                    self.decay_constant,
                                    self.job,
                                    formatted=False,
                                    detailed=True)
            self.assertEqual(patch_output.getvalue(), expected_output)

    def test_formatted_summary(self):
        '''
        Test the formatted summary
        '''
        expected_output = rates_out.KEY_TITLE
        expected_output += rates_out.KEY_DAYS
        expected_output += rates_out.KEY_SUMMARY
        expected_output += '{:20s} {:>8s} {:>8s} {:>8s} {:>8s}\n'.format(
            self.suite_name, 'days', 'last', 'ravg', 'decd')
        for item in self.items:
            expected_output += '{:20s} {:8.1f} {:8.2f} {:8.2f} {:8.2f}\n'. \
                                format(item, 1, 1, 0.5, 0.625)

        with mock.patch('sys.stdout', new=io.StringIO()) as patch_output:
            rates_out.print_summary(self.input_rates,
                                    self.suite_name,
                                    self.interval,
                                    self.decay_constant,
                                    self.job,
                                    formatted=True,
                                    detailed=False)
            self.assertEqual(patch_output.getvalue(), expected_output)

    def test_formatted_detail(self):
        '''
        Test the detailed formatted summary
        '''
        expected_output = rates_out.KEY_TITLE
        expected_output += rates_out.KEY_DAYS
        expected_output += rates_out.KEY_SUMMARY
        expected_output += rates_out.KEY_DETAIL
        expected_output += '{:20s} {:>8s} {:>8s} {:>8s} {:>8s} {:>8s}' \
                           ' {:>8s}\n'.format(self.suite_name, 'days', 'last',
                                              'ravg', 'decd', 'intp', 'davg')
        for item in self.items:
            expected_output += '{:20s} {:8.1f} {:8.2f} {:8.2f} {:8.2f}' \
                               ' {:8.2f} {:8.2f}\n'.format(
                                   item, 1, 1, 0.5, 0.62, 1, 0.29)

        with mock.patch('sys.stdout', new=io.StringIO()) as patch_output:
            rates_out.print_summary(self.input_rates,
                                    self.suite_name,
                                    self.interval,
                                    self.decay_constant,
                                    self.job,
                                    formatted=True,
                                    detailed=True)
            self.assertEqual(patch_output.getvalue(), expected_output)

    def test_filter_summary_unformatted(self):
        '''
        We do apply a filter to these jobs, so this will check our start
        and end filters work, and that this functionality hasnt been removed
        '''
        input_rates_for_filter = [
            rates_lib.RATES._make([0, 10, 10, 10, 10]),
            rates_lib.RATES._make([1, 0, 0, 0, 0]),
            rates_lib.RATES._make([2, 1, 1, 1, 1]),
            rates_lib.RATES._make([3., 10, 10, 10, 10])]
        expected_output = '3.0 1 4.571428571428571 6.765625\n' * 4
        with mock.patch('sys.stdout', new=io.StringIO()) as patch_output:
            rates_out.print_summary(input_rates_for_filter,
                                    self.suite_name,
                                    self.interval,
                                    self.decay_constant,
                                    self.job,
                                    formatted=False,
                                    detailed=False,
                                    filter_start=0.9,
                                    filter_end=2.1)
            self.assertEqual(patch_output.getvalue(), expected_output)
