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
import collections
try:
    # mock is integrated into unittest as of Python 3.3
    import unittest.mock as mock
except ImportError:
    # mock is a standalone package (back-ported)
    import mock

import rates_lib
import suite_run_rates


class Defaults(unittest.TestCase):
    '''
    Check all the default values havent been changed
    '''
    def test_default_cycle(self):
        '''Check cycle length'''
        self.assertEqual(suite_run_rates.CYCLE_LENGTH, 1.)

    def test_default_month(self):
        '''Check month length'''
        self.assertEqual(suite_run_rates.MONTH_LENGTH, 30.)

    def test_default_year(self):
        '''Check year length'''
        self.assertEqual(suite_run_rates.YEAR_LENGTH, 360.)

    def test_default_decay(self):
        '''Check decay constant'''
        self.assertEqual(suite_run_rates.DECAY_CONSTANT, 0.05)

    def test_default_interval(self):
        '''Check interval'''
        self.assertEqual(suite_run_rates.INTERVAL, (20./(24.*60)))


class CommandLineInterface(unittest.TestCase):
    '''
    Test the aspects of the command line interface to the script
    '''

    @mock.patch('suite_run_rates.argparse.ArgumentParser')
    def test_gather_arguments(self, mock_argparse):
        '''
        Check all the helps/default values/variable names etc are ok
        '''
        suite_run_rates.gather_arguments()

        # Get a big list of the calls to add arguments.
        calls = [mock.call("-c", "--cycle-length",
                           action='store', type=float,
                           dest='cycle_len',
                           default=suite_run_rates.CYCLE_LENGTH,
                           help=("The suite cycle length in months, default {}"
                                 .format(suite_run_rates.CYCLE_LENGTH))),
                 mock.call("-m", "--month-length",
                           action='store', type=float,
                           dest='month_len',
                           default=suite_run_rates.MONTH_LENGTH,
                           help=("The length of a month in days, default {}"
                                 .format(suite_run_rates.MONTH_LENGTH))),
                 mock.call("-y", "--year-length",
                           action='store', type=float,
                           dest='year_len',
                           default=suite_run_rates.YEAR_LENGTH,
                           help=("The length of a year in days, default {}"
                                 .format(suite_run_rates.YEAR_LENGTH))),
                 mock.call("-a", "--decay_constant",
                           action='store', type=float,
                           dest='decay_constant',
                           default=suite_run_rates.DECAY_CONSTANT,
                           help=("Decay Constant  for decaying average,"
                                 " default {}".
                                 format(suite_run_rates.DECAY_CONSTANT))),
                 mock.call("-i", "--interpolation-interval",
                           action='store', type=float,
                           dest='interval', default=suite_run_rates.INTERVAL,
                           help=("Interpolation interval, in days, default {}"
                                 .format(suite_run_rates.INTERVAL))),
                 mock.call("-j", "--job-name",
                           action='store',
                           dest='job', default="coupled",
                           help="Suite task name (default 'coupled')"),
                 mock.call("-s", "--start-day",
                           action='store', type=float,
                           dest='start', default=None,
                           help="Starting day for calculations"),
                 mock.call("-e", "--end-day",
                           action='store', type=float,
                           dest='end', default=None,
                           help="Ending day for calculations"),
                 mock.call("-p", "--unformatted-output",
                           action='store_false',
                           dest='formatted',
                           default=True,
                           help="Produce unformatted output," \
                           " with no headers etc."),
                 mock.call("-r", "--report-type",
                           choices=('summary', 'detailed',
                                    'raw', 'interpolated', 'plot'),
                           dest='report_type', default='summary',
                           help="Report type to produce (default is summary)"),
                 mock.call("CYLC_RUN_DIR",
                           help="Cylc run directory for the suite")]
        mock_argparse.return_value.add_argument.assert_has_calls(calls)


class CommandLineArgumentsValidation(unittest.TestCase):
    '''
    Check the validations of the command line arguments work
    '''

    def test_small_cycle_length(self):
        '''
        Error if cycle length is negative
        '''
        Args = collections.namedtuple('args', 'cycle_len')
        args = Args(cycle_len=-1)
        with self.assertRaises(rates_lib.ScriptError) as context:
            suite_run_rates.check_arguments(args)
        self.assertTrue('Cycle length must be greater than 0' in
                        str(context.exception))

    def test_small_interval(self):
        '''
        Error if negative length is negative
        '''
        Args = collections.namedtuple('args', ('cycle_len', 'interval'))
        args = Args(cycle_len=10, interval=-1)
        with self.assertRaises(rates_lib.ScriptError) as context:
            suite_run_rates.check_arguments(args)
        self.assertTrue('Interpolation interval must be greater than 0' in
                        str(context.exception))

    @mock.patch('suite_run_rates.os.path')
    def test_small_decay(self, mock_ospath):
        '''
        Error if decay constant <0
        '''
        mock_ospath.isdir.return_value = True
        Args = collections.namedtuple('args', ('cycle_len', 'interval',
                                               'decay_constant',
                                               'CYLC_RUN_DIR'))
        args = Args(cycle_len=10, interval=10, decay_constant=-1,
                    CYLC_RUN_DIR='testdir')
        with self.assertRaises(rates_lib.ScriptError) as context:
            suite_run_rates.check_arguments(args)
        self.assertTrue('Decay constant must be between 0 and 1' in
                        str(context.exception))

    @mock.patch('suite_run_rates.os.path')
    def test_big_decay(self, mock_ospath):
        '''
        Error oif decay constant >1
        '''
        mock_ospath.isdir.return_value = True
        Args = collections.namedtuple('args', ('cycle_len', 'interval',
                                               'decay_constant',
                                               'CYLC_RUN_DIR'))
        args = Args(cycle_len=10, interval=10, decay_constant=2,
                    CYLC_RUN_DIR='testdir')
        with self.assertRaises(rates_lib.ScriptError) as context:
            suite_run_rates.check_arguments(args)
        self.assertTrue('Decay constant must be between 0 and 1' in
                        str(context.exception))

    @mock.patch('suite_run_rates.os.path')
    def test_no_directory(self, mock_ospath):
        '''
        Error if the cylc run directory deosnt exist
        '''
        mock_ospath.isdir.return_value = False
        Args = collections.namedtuple('args', ('cycle_len', 'interval',
                                               'decay_constant',
                                               'CYLC_RUN_DIR'))
        args = Args(cycle_len=10, interval=10, decay_constant=0.5,
                    CYLC_RUN_DIR='testdir')
        with self.assertRaises(rates_lib.ScriptError) as context:
            suite_run_rates.check_arguments(args)
        self.assertTrue('testdir does not exist, or is not a directory' in
                        str(context.exception))

    @mock.patch('suite_run_rates.os.path')
    def test_working(self, mock_ospath):
        '''
        Make sure we get everything back if the function works correctly
        '''
        mock_ospath.isdir.return_value = True
        Args = collections.namedtuple('args', ('cycle_len', 'interval',
                                               'decay_constant',
                                               'CYLC_RUN_DIR'))
        args = Args(cycle_len=10, interval=10, decay_constant=0.5,
                    CYLC_RUN_DIR='testdir')
        self.assertEqual(suite_run_rates.check_arguments(args),
                         args)



class CheckMain(unittest.TestCase):
    '''
    Make sure the right thing is being called given the arguments
    '''
    def setUp(self):
        # Create most of our arguments we need
        self.args = collections.namedtuple('args',
                                           ('cycle_len', 'month_len',
                                            'year_len', 'interval', 'job',
                                            'start', 'end', 'decay_constant',
                                            'formatted', 'CYLC_RUN_DIR', #
                                            'report_type'))
        self.make_list = [1., 30., 360., 0.5, 'test_job', None, None, 0.05,
                          True, 'test_run_dir']

    @mock.patch('suite_run_rates.os.path')
    def test_main_no_path_to_db(self, mock_os_path):
        '''
        Error if cylc database can not be found
        '''
        mock_os_path.split.return_value = ['test']
        mock_os_path.join.return_value = 'cylc.db'
        mock_os_path.isfile.return_value = False
        Args = collections.namedtuple('args', 'CYLC_RUN_DIR')
        args = Args(CYLC_RUN_DIR='testdir')
        with self.assertRaises(rates_lib.ScriptError) as context:
            suite_run_rates.main(args)
        self.assertTrue('The path cylc.db to the cylc database doesnt exist' in
                        str(context.exception))

    @mock.patch('suite_run_rates.os.path')
    @mock.patch('suite_run_rates.rates_lib')
    def test_main_days_from_db(self, mock_lib, mock_os_path):
        '''
        Ensure days_from_db is called correctly
        '''
        mock_os_path.split.return_value = ['test']
        mock_os_path.join.return_value = 'cylc.db'
        mock_os_path.isfile.return_value = True
        arg_list = self.make_list + ['raw']
        args = self.args._make(arg_list)
        suite_run_rates.main(args)
        mock_lib.days_from_db.assert_called_once_with(
            'cylc.db', 'test_job')

    @mock.patch('suite_run_rates.os.path')
    @mock.patch('suite_run_rates.rates_lib')
    def test_main_calculate_relative_times(
            self, mock_lib, mock_os_path):
        '''
        Ensure calculate_relative_times is called correctly
        '''
        mock_os_path.split.return_value = ['test']
        mock_os_path.join.return_value = 'cylc.db'
        mock_os_path.isfile.return_value = True
        mock_lib.days_from_db.return_value = ['days']
        arg_list = self.make_list + ['raw']
        args = self.args._make(arg_list)
        suite_run_rates.main(args)
        mock_lib.calculate_relative_times.assert_called_once_with(
            ['days'])


    @mock.patch('suite_run_rates.os.path')
    @mock.patch('suite_run_rates.rates_lib')
    def test_main_calculate_rates(
            self, mock_lib, mock_os_path):
        '''
        Ensure calculate_rates is called correctly
        '''
        mock_os_path.split.return_value = ['test']
        mock_os_path.join.return_value = 'cylc.db'
        mock_os_path.isfile.return_value = True
        mock_lib.days_from_db.return_value = ['days']
        mock_lib.calculate_relative_times.return_value = ['rel']
        arg_list = self.make_list + ['raw']
        args = self.args._make(arg_list)
        suite_run_rates.main(args)
        mock_lib.calculate_rates.assert_called_once_with(
            ['rel'], 1., 30., 360.)


    @mock.patch('suite_run_rates.os.path')
    @mock.patch('suite_run_rates.rates_lib')
    @mock.patch('suite_run_rates.rates_out')
    def test_main_raw(
            self, mock_out, mock_lib, mock_os_path):
        '''
        Ensure print_raw_rates is called if appropriate
        '''
        mock_os_path.split.return_value = ['test']
        mock_os_path.join.return_value = 'cylc.db'
        mock_os_path.isfile.return_value = True
        mock_lib.days_from_db.return_value = ['days']
        mock_lib.calculate_relative_times.return_value = ['rel']
        mock_lib.calculate_rates.return_value = ['rates']
        arg_list = self.make_list + ['raw']
        args = self.args._make(arg_list)
        suite_run_rates.main(args)
        mock_out.print_raw_rates.assert_called_once_with(
            ['rates'], args.formatted, args.start, args.end)

    @mock.patch('suite_run_rates.os.path')
    @mock.patch('suite_run_rates.rates_lib')
    @mock.patch('suite_run_rates.rates_out')
    def test_main_interpolated(
            self, mock_out, mock_lib, mock_os_path):
        '''
        Ensure print_interpolated_rates is called if appropriate
        '''
        mock_os_path.split.return_value = ['test']
        mock_os_path.join.return_value = 'cylc.db'
        mock_os_path.isfile.return_value = True
        mock_lib.days_from_db.return_value = ['days']
        mock_lib.calculate_relative_times.return_value = ['rel']
        mock_lib.calculate_rates.return_value = ['rates']
        arg_list = self.make_list + ['interpolated']
        args = self.args._make(arg_list)
        suite_run_rates.main(args)
        mock_out.print_interpolated_rates.assert_called_once_with(
            ['rates'], args.interval, args.decay_constant, args.formatted,
            args.start, args.end)

    @mock.patch('suite_run_rates.os.path')
    @mock.patch('suite_run_rates.rates_lib')
    @mock.patch('suite_run_rates.rates_plot')
    def test_main_plot(
            self, mock_plot, mock_lib, mock_os_path):
        '''
        Ensure plot_interpolated_rates is called if appropriate
        '''
        mock_os_path.split.return_value = ['test']
        mock_os_path.join.return_value = 'cylc.db'
        mock_os_path.isfile.return_value = True
        mock_lib.days_from_db.return_value = ['days']
        mock_lib.calculate_relative_times.return_value = ['rel']
        mock_lib.calculate_rates.return_value = ['rates']
        arg_list = self.make_list + ['plot']
        args = self.args._make(arg_list)
        suite_run_rates.main(args)
        mock_plot.plot_interpolated_rates.assert_called_once_with(
            ['rates'], args.interval, args.decay_constant,
            args.start, args.end)

    @mock.patch('suite_run_rates.os.path')
    @mock.patch('suite_run_rates.rates_lib')
    @mock.patch('suite_run_rates.rates_out')
    def test_main_print_summary_detailed(
            self, mock_out, mock_lib, mock_os_path):
        '''
        Ensure print_summary with detailed option is called if appropriate
        '''
        mock_os_path.split.return_value = ['test']
        mock_os_path.join.return_value = 'cylc.db'
        mock_os_path.isfile.return_value = True
        mock_lib.days_from_db.return_value = ['days']
        mock_lib.calculate_relative_times.return_value = ['rel']
        mock_lib.calculate_rates.return_value = ['rates']
        arg_list = self.make_list + ['detailed']
        args = self.args._make(arg_list)
        suite_run_rates.main(args)
        mock_out.print_summary.assert_called_once_with(
            ['rates'], 'test', args.interval, args.decay_constant,
            args.job, args.formatted, True, args.start, args.end)

    @mock.patch('suite_run_rates.os.path')
    @mock.patch('suite_run_rates.rates_lib')
    @mock.patch('suite_run_rates.rates_out')
    def test_main_print_summary_summary(
            self, mock_out, mock_lib, mock_os_path):
        '''
        Ensure print_summary with summary option is called if appropriate
        '''
        mock_os_path.split.return_value = ['test']
        mock_os_path.join.return_value = 'cylc.db'
        mock_os_path.isfile.return_value = True
        mock_lib.days_from_db.return_value = ['days']
        mock_lib.calculate_relative_times.return_value = ['rel']
        mock_lib.calculate_rates.return_value = ['rates']
        arg_list = self.make_list + ['summary']
        args = self.args._make(arg_list)
        suite_run_rates.main(args)
        mock_out.print_summary.assert_called_once_with(
            ['rates'], 'test', args.interval, args.decay_constant,
            args.job, args.formatted, False, args.start, args.end)
