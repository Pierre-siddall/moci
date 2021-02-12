#!/usr/bin/env python
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2019-2020 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
'''

import unittest
try:
    # mock is integrated into unittest as of Python 3.3
    import unittest.mock as mock
except ImportError:
    # mock is a standalone package (back-ported)
    import mock

import rates_lib

class CalcRateTest(unittest.TestCase):
    '''
    Test the calculate_rates function
    '''
    def setUp(self):
        self.days = [rates_lib.DAYS._make((1.069, 1.091, 1.171)),
                     rates_lib.DAYS._make((1.171, 1.496, 1.574))]

    def test_error(self):
        '''
        Test the exception is raised if the length of times list is 1
        '''
        with self.assertRaises(rates_lib.ScriptError) as context:
            rates_lib.calculate_rates([3.0], 1., 30., 360.)
        self.assertTrue('Need a completed cycle to compute a rate' in
                        str(context.exception))

    def test_rates(self):
        '''
        Test that we can calculate rates correctly
        '''
        expected_rates = rates_lib.RATES._make(
            (1.069,
             0.8169934640522868,
             1.0416666666666659,
             0.8169934640522868,
             1.0416666666666659))
        self.assertEqual(
            rates_lib.calculate_rates(
                self.days, 1.0, 30.0, 360.0)[0], expected_rates)

class RelativeTimesTest(unittest.TestCase):
    '''
    Test the calculate_relative_times function
    '''
    def setUp(self):
        self.days = [rates_lib.DAYS._make((0.5, 1.5, 2.5)),
                     rates_lib.DAYS._make((2.8, 3.7, 5.2)),
                     rates_lib.DAYS._make((6.0, 7.25, 8.9))]

    def test_relative(self):
        '''
        Test the maths of the function'''
        expected_rel_days = (rates_lib.DAYS._make((0.0, 1.0, 2.0)),
                             rates_lib.DAYS._make((2.3, 3.2, 4.7)),
                             rates_lib.DAYS._make((5.5, 6.75, 8.4)))
        self.assertEqual(
            rates_lib.calculate_relative_times(self.days),
            expected_rel_days)

class DatabaseTest(unittest.TestCase):
    '''
    Test the days_from_db function
    '''
    @mock.patch('rates_lib.sqlite3.connect')
    def test_db_database_problem(self, sqlite):
        '''
        Check that if no values are retrieved from database an exception
        will be raised
        '''
        sqlite.return_value.__enter__.return_value. \
            cursor.return_value.fetchall. \
            return_value = []
        with self.assertRaises(rates_lib.ScriptError) as context:
            rates_lib.days_from_db(None)
        self.assertTrue('Unable to retrieve cycle times from the cylc'
                        ' database' in str(context.exception))

    @mock.patch('rates_lib.sqlite3.connect')
    def test_db(self, sqlite):
        '''
        Check that DAYS objects will be returned when times are read from the
        database
        '''
        expected_output = [
            rates_lib.DAYS._make((1., 1., 1.)),
            rates_lib.DAYS._make((2., 2., 2.))]

        sqlite.return_value.__enter__.return_value. \
            cursor.return_value.fetchall. \
            return_value = [[1., 1., 1.], [2., 2., 2.]]

        self.assertEqual(
            rates_lib.days_from_db(None), expected_output)

    @mock.patch('rates_lib.sqlite3.connect')
    def test_query(self, sqlite):
        '''
        As it is potentially quite brittle, test that the correct database
        query is used. In addition this tests that a job that isnt the
        default of 'coupled' can be investigated
        '''
        expected_query = 'select ' \
                         'julianday(time_submit), julianday(time_run), ' \
                         'julianday(time_run_exit) ' \
                         'from ' \
                         'task_jobs ' \
                         'where ' \
                         'name == "postproc" and submit_status == 0 ' \
                         'and run_status == 0 and ' \
                         'julianday(time_submit) IS NOT NULL and ' \
                         'julianday(time_run) IS NOT NULL and ' \
                         'julianday(time_run_exit) IS NOT NULL ' \
                         'order by julianday(time_submit)'
        sqlite.return_value.__enter__.return_value. \
            cursor.return_value.fetchall. \
            return_value = [[1., 1., 1.], [2., 2., 2.]]

        _ = rates_lib.days_from_db(None, job='postproc')

        sqlite.return_value.__enter__.return_value. \
            cursor.return_value.execute.assert_called_once_with(expected_query)

    def test_invalid_name(self):
        '''
        Test an invalid job name
        '''
        with self.assertRaises(rates_lib.ScriptError) as context:
            rates_lib.days_from_db(None, '7nvalid_name')
        self.assertTrue('7nvalid_name is an invalid job name' in
                        str(context.exception))

class InterpolateTest(unittest.TestCase):
    '''
    Test the interpolate function
    '''
    def test_fail_on_diff_no_x_y_values(self):
        '''
        Test failure if there are differing numbers of x and y values
        '''
        with self.assertRaises(rates_lib.ScriptError) as context:
            rates_lib.interpolate([1., 2., 3.], [1., 2.], None)
        self.assertTrue(
            'Need the same number of x- and y- values to interpolate'
            in str(context.exception))

    def test_fail_on_one_axis_value(self):
        '''
        Test failure if there are only one axis value
        '''
        with self.assertRaises(rates_lib.ScriptError) as context:
            rates_lib.interpolate([1.], [1.], None)
        self.assertTrue(
            'Need two or more values to perform interpolation'
            in str(context.exception))

    def test_perform_interpolation(self):
        '''
        Test a simple interpolation
        '''
        expected_result = ([1.0, 1.5, 2.0, 2.5, 3.0],
                           [1.0, 0.75, 0.5, 1.25, 2.0])
        self.assertEqual(
            rates_lib.interpolate([1., 2., 3.],
                                  [1., 0.5, 2.], 0.5),
            expected_result)

class InterpolateRatesTest(unittest.TestCase):
    '''
    Test the interpolate_rates function
    '''
    def test_fail_on_one_rate_val(self):
        '''
        Fail if only one rate in presented to the interpolation
        '''
        with self.assertRaises(rates_lib.ScriptError) as context:
            rates_lib.interpolate_rates([None], None)
        self.assertTrue(
            'Need two or more completed cycles to perform interpolation'
            in str(context.exception))

    def test_perform_interpolation(self):
        '''
        Perform a simple interpolation of the rates
        '''
        expected_results = (
            rates_lib.RATES._make([1.0, 1.0, 1.0, 1.0, 1.0]),
            rates_lib.RATES._make([1.5, 0.25, 0.75, 1.5, 2.0]),
            rates_lib.RATES._make([2.0, -0.5, 0.5, 2.0, 3.0]))
        self.assertEqual(
            rates_lib.interpolate_rates(
                [rates_lib.RATES._make([1., 1., 1., 1., 1.]),
                 rates_lib.RATES._make([2., -0.5, 0.5, 2, 3.])], 0.5),
            expected_results)

class IntegrateTest(unittest.TestCase):
    '''
    Test the integrate function
    '''
    def test_integration(self):
        '''
        Perform a simple integration
        '''
        expected_result = rates_lib.INTEGRATEDRATES._make(
            [0.5, 2, 0.75, 1.25, 1.5, 2.0])

        self.assertEqual(
            rates_lib.integrate(
                [rates_lib.RATES._make([1., 1., 2., 1., 1.]),
                 rates_lib.RATES._make([2., 0.5, 0.5, 2, 3.])], 0.5),
            expected_result)

class DecayingMeansTest(unittest.TestCase):
    '''
    Test the decaying means functionality
    '''
    def test_decay_mean_const(self):
        '''
        Perform a simple test of the function that actually calculates the
        decay with a list of constant values.
        '''
        expected_result = [5.0, 5.0, 5.0, 5.0, 5.0]
        self.assertEqual(
            rates_lib.decay_mean([5.0, 5.0, 5.0, 5.0, 5.0], 0.05),
            expected_result)

    def test_decay_mean(self):
        '''
        Perform a simple test of the function that actually calculates the
        decay with a list of arbitary values and constant of 0.1
        '''
        expected_result = [5.0, 5.1, 4.99, 4.791]
        self.assertEqual(
            rates_lib.decay_mean([5., 6., 4., 3.], 0.1),
            expected_result)

    def test_decay_rates(self):
        '''
        Test the decay_rates function with RATES objects
        '''
        input_data = [rates_lib.RATES._make([1., 5., 5., 5., 5.]),
                      rates_lib.RATES._make([2., 6., 6., 6., 6.]),
                      rates_lib.RATES._make([3., 4., 4., 4., 4.]),
                      rates_lib.RATES._make([4., 3., 3., 3., 3.])]
        expected_result = (
            rates_lib.RATES._make([1., 5., 5., 5., 5.]),
            rates_lib.RATES._make([2., 5.1, 5.1, 5.1, 5.1]),
            rates_lib.RATES._make([3., 4.99, 4.99, 4.99, 4.99]),
            rates_lib.RATES._make([4., 4.791, 4.791, 4.791, 4.791]))
        self.assertEqual(
            rates_lib.decay_rates(input_data, 0.1),
            expected_result)
