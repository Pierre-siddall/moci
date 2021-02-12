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

import os
import argparse
import rates_lib
import rates_out
import rates_plot


# Default values
CYCLE_LENGTH = 1.
MONTH_LENGTH = 30.
YEAR_LENGTH = 360.
DECAY_CONSTANT = 0.05
INTERVAL = (20./(24*60))


def gather_arguments():
    '''
    Gather the command line arguments the script and return a parse_args
    object
    '''
    parser = argparse.ArgumentParser(
        description='Report rates from a task in a cycling suite')
    parser.add_argument("-c", "--cycle-length",
                        action='store', type=float,
                        dest='cycle_len', default=CYCLE_LENGTH,
                        help=("The suite cycle length in months, default {}"
                              .format(CYCLE_LENGTH)))
    parser.add_argument("-m", "--month-length",
                        action='store', type=float,
                        dest='month_len', default=MONTH_LENGTH,
                        help=("The length of a month in days, default {}"
                              .format(MONTH_LENGTH)))
    parser.add_argument("-y", "--year-length",
                        action='store', type=float,
                        dest='year_len', default=YEAR_LENGTH,
                        help=("The length of a year in days, default {}"
                              .format(YEAR_LENGTH)))
    parser.add_argument("-a", "--decay_constant",
                        action='store', type=float,
                        dest='decay_constant', default=DECAY_CONSTANT,
                        help=("Decay Constant  for decaying average, default {}"
                              .format(DECAY_CONSTANT)))
    parser.add_argument("-i", "--interpolation-interval",
                        action='store', type=float,
                        dest='interval', default=INTERVAL,
                        help=("Interpolation interval, in days, default {}"
                              .format(INTERVAL)))
    parser.add_argument("-j", "--job-name",
                        action='store',
                        dest='job', default="coupled",
                        help="Suite task name (default 'coupled')")
    parser.add_argument("-s", "--start-day",
                        action='store', type=float,
                        dest='start', default=None,
                        help="Starting day for calculations")
    parser.add_argument("-e", "--end-day",
                        action='store', type=float,
                        dest='end', default=None,
                        help="Ending day for calculations")
    parser.add_argument("-p", "--unformatted-output",
                        action='store_false',
                        dest='formatted',
                        default=True,
                        help="Produce unformatted output, with no headers etc.")
    parser.add_argument("-r", "--report-type",
                        choices=('summary', 'detailed',
                                 'raw', 'interpolated', 'plot'),
                        dest='report_type', default='summary',
                        help="Report type to produce (default is summary)")
    parser.add_argument("CYLC_RUN_DIR",
                        help="Cylc run directory for the suite")
    return parser.parse_args()


def check_arguments(args):
    '''
    Parse the arguments and ensure that they fall within sensible values.
    Returns parse_args object for further use
    '''
    if args.cycle_len <= 0:
        raise rates_lib.ScriptError('Cycle length must be greater than 0')
    if args.interval <= 0:
        raise rates_lib.ScriptError(
            'Interpolation interval must be greater than 0')
    if not os.path.isdir(args.CYLC_RUN_DIR):
        raise rates_lib.ScriptError(
            '{} does not exist, or is not a directory'.
            format(args.CYLC_RUN_DIR))
    if not 0.0 < args.decay_constant < 1.0:
        raise rates_lib.ScriptError('Decay constant must be between 0 and 1')
    return args


def main(args, cylc_db='log/db'):
    '''
    Main function, takes the parsed arguments and then calls the appropriate
    parts of the code.
    '''
    suite_name = os.path.split(args.CYLC_RUN_DIR)[-1]
    path_to_db = os.path.join(args.CYLC_RUN_DIR, cylc_db)
    if not os.path.isfile(path_to_db):
        raise rates_lib.ScriptError('The path {} to the cylc database doesnt'
                                    ' exist'.format(path_to_db))
    days = rates_lib.days_from_db(path_to_db, args.job)
    days = rates_lib.calculate_relative_times(days)
    rates = rates_lib.calculate_rates(days, args.cycle_len, args.month_len,
                                      args.year_len)
    if args.report_type in ('summary', 'detailed'):
        rates_out.print_summary(rates, suite_name, args.interval,
                                args.decay_constant, args.job, args.formatted,
                                (args.report_type == 'detailed'),
                                args.start, args.end)
    elif args.report_type == 'raw':
        rates_out.print_raw_rates(rates, args.formatted, args.start, args.end)
    elif args.report_type == 'interpolated':
        rates_out.print_interpolated_rates(rates, args.interval,
                                           args.decay_constant, args.formatted,
                                           args.start, args.end)
    elif args.report_type == 'plot':
        rates_plot.plot_interpolated_rates(rates, args.interval,
                                           args.decay_constant, args.start,
                                           args.end)
    else:
        raise rates_lib.ScriptError('Report type {} is not valid'.
                                    format(args.report_type))


if __name__ == '__main__':
    ARGUMENTS = gather_arguments()
    PARSED_ARGS = check_arguments(ARGUMENTS)
    main(PARSED_ARGS)
