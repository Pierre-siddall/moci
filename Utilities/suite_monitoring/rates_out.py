#!/usr/bin/env/python
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
NAME
    rates_out.py

DESCRIPTION
    Functions to provide the text output to standard output
'''

import sys
import rates_lib


KEY_TITLE = 'Output key:\n'
KEY_RAW = '  effr: Effective rate\n' \
          '  cplr: Coupled model rate\n' \
          '  cpqr: Coupled and Queuing rate\n' \
          '  cpwr: Coupled and Waiting rate\n'

KEY_DECAYED = '  deff: Decayed effective rate\n' \
              '  dcpl: Decayed coupled model rate\n' \
              '  dcpq: Decayed Coupled and Queuing rate\n' \
              '  dcpw: Decayed Coupled and Waiting rate\n'

KEY_DAYS = '  days: Number of days the suite has been running\n'

KEY_SUMMARY = '  last: Last cycle run\n' \
              '  ravg: Avergage rate\n' \
              '  decd: Last decayed value\n'
KEY_DETAIL = '  intp: Last interpolated rate\n' \
             '  davg: Average decayed value\n'


def calculate_start_and_end(rates, start, end):
    '''
    Takes the given start and end dates and a rates list, and returns the
    start and end date for the filter. If start and end are None, then
    no filter is applied and if they have negative values we work from the
    ends
    '''
    if not start:
        start = rates[0].day
    else:
        if start < 0.0:
            start = rates[-1].day + start
    if not end:
        end = rates[-1].day
    else:
        if end < 0.0:
            end = rates[-1].day + end
    return start, end


def filter_rates(rates, start=None, end=None):
    '''
    filter rate objects between start day 'start' and end day 'end'
    default is to return everything. Can use negative values to go backwards
    '''
    start_day, end_day = calculate_start_and_end(rates, start, end)
    return tuple(rate for rate in rates if start_day <= rate.day <= end_day)


def print_raw_rates(rates, formatted=True, filter_start=None, filter_end=None):
    '''
    Display the raw rates to standard out, either formatted or unformatted
    '''
    if formatted:
        control = "{:8.1f} {:8.2f} {:8.2f} {:8.2f} {:8.2f}\n"
    else:
        control = "{} {} {} {} {}\n"

    if formatted:
        # print the header and key
        sys.stdout.write(KEY_TITLE)
        sys.stdout.write(KEY_DAYS)
        sys.stdout.write(KEY_RAW)
        sys.stdout.write("{:>8s} {:>8s} {:>8s} {:>8s} {:>8s}\n".
                         format("days", "effr", "cplr", "cpqr", "cpwr"))
    for rate in filter_rates(rates, filter_start, filter_end):
        sys.stdout.write(control.format(rate.day, rate.effective,
                                        rate.coupled, rate.coupled_queue,
                                        rate.coupled_wait))

def print_interpolated_rates(rates, interval, decay_const, formatted=True,
                             filter_start=None, filter_end=None):
    '''
    Display the interpolated rates to standard out, either formatted or
    unformatted
    '''
    if formatted:
        control = "{:8.1f}" + " {:8.2f}" * 8 + "\n"
    else:
        control = "{} {} {} {} {} {} {} {} {}\n"

    if formatted:
        # print the header and key
        sys.stdout.write(KEY_TITLE)
        sys.stdout.write(KEY_DAYS)
        sys.stdout.write(KEY_RAW)
        sys.stdout.write(KEY_DECAYED)
        sys.stdout.write("{:>8s} {:>8s} {:>8s} {:>8s} {:>8s} {:>8s}"
                         " {:>8s} {:>8s} {:>8s}\n".format(
                             "days", "effr", "cplr", "cpqr", "cpwr",
                             "deff", "dcpl", "dcpq", "dcpw"))
    filtered_rates = filter_rates(rates, filter_start, filter_end)
    interpolated_rates = rates_lib.interpolate_rates(filtered_rates, interval)

    decayed_rates = rates_lib.decay_rates(interpolated_rates, decay_const)
    for interp, decayed in zip(interpolated_rates, decayed_rates):
        sys.stdout.write(control.format(interp.day,
                                        interp.effective, interp.coupled,
                                        interp.coupled_queue,
                                        interp.coupled_wait,
                                        decayed.effective, decayed.coupled,
                                        decayed.coupled_queue,
                                        decayed.coupled_wait))

# The functions below deal with generating summaries
def print_summary_values(item, rates,
                         interp_rates, integ_rates,
                         decayed_rates, decayed_integ, runtime,
                         job='coupled', detailed=False, formatted=True):
    '''
    Display the summary values, choose either detailed or summary, and then
    formatted or unformatted (4 potential options
    '''
    if item not in ('effective', 'coupled_queue', 'coupled_wait', 'coupled'):
        raise rates_lib.ScriptError('Unable to write output for property {}'.
                                    format(item))
    # whilst the script is written for coupled tasks, and this is the default
    # it may not always be the case.
    title = item.replace('coupled', job)
    if detailed:
        if formatted:
            control = '{:20s} {:8.1f} {:8.2f} {:8.2f} {:8.2f} {:8.2f} {:8.2f}\n'
        else:
            control = '{}{} {} {} {} {} {}\n'
        sys.stdout.write(
            control.format(title if formatted else '',
                           interp_rates[-1].day - interp_rates[0].day,
                           getattr(rates[-1], item),
                           getattr(integ_rates, item) / runtime,
                           getattr(decayed_rates[-1], item),
                           getattr(interp_rates[-1], item),
                           getattr(decayed_integ, item)/runtime))
    else:
        if formatted:
            control = '{:20s} {:8.1f} {:8.2f} {:8.2f} {:8.2f}\n'
        else:
            control = '{}{} {} {} {}\n'
        sys.stdout.write(
            control.format(title if formatted else '',
                           interp_rates[-1].day - interp_rates[0].day,
                           getattr(rates[-1], item),
                           getattr(integ_rates, item) / runtime,
                           getattr(decayed_rates[-1], item)))

def print_summary(rates, suite, interval, decay_const, job="coupled",
                  formatted=True, detailed=False, filter_start=None,
                  filter_end=None):
    '''
    Display the headers for the summary values, then call the
    print_summary_values function to print the actual values
    '''
    items = ['effective', 'coupled', 'coupled_queue', 'coupled_wait']

    #calculate items to print
    filtered_rates = filter_rates(rates, filter_start, filter_end)
    interpolated_rates = rates_lib.interpolate_rates(rates, interval)
    integrated_rates = rates_lib.integrate(interpolated_rates, interval)
    decayed_rates = rates_lib.decay_rates(interpolated_rates, decay_const)
    decayed_integrated = rates_lib.integrate(decayed_rates, interval)
    runtime = integrated_rates.n * integrated_rates.interval

    # sort out our keys
    if formatted:
        sys.stdout.write(KEY_TITLE)
        sys.stdout.write(KEY_DAYS)
        sys.stdout.write(KEY_SUMMARY)
        if detailed:
            sys.stdout.write(KEY_DETAIL)
    # sort out our colum headings if appropriate
    if formatted:
        if detailed:
            sys.stdout.write(
                '{:20s} {:>8s} {:>8s} {:>8s} {:>8s} {:>8s} {:>8s}\n'
                .format(suite, 'days', 'last', 'ravg', 'decd', 'intp', 'davg'))
        else:
            sys.stdout.write(
                '{:20s} {:>8s} {:>8s} {:>8s} {:>8s}\n'.format(
                    suite, 'days', 'last', 'ravg', 'decd'))
    for item in items:
        print_summary_values(item,
                             filtered_rates,
                             interpolated_rates,
                             integrated_rates,
                             decayed_rates,
                             decayed_integrated,
                             runtime,
                             job=job,
                             detailed=detailed, formatted=formatted)
