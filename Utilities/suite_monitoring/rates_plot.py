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

import pylab
import rates_lib
import rates_out

def plot_interpolated_rates(rates, interval, decay_const,
                            filter_start=None, filter_end=None):
    '''
    Plot the rates using matplotlib
    '''
    rates = rates_out.filter_rates(rates, filter_start, filter_end)
    interpolated_rates = rates_lib.interpolate_rates(rates, interval)

    decayed_rates = rates_lib.decay_rates(interpolated_rates, decay_const)

    #data arrays
    days = []
    coupled = []
    coupled_waiting = []
    coupled_queuing = []
    decayed_effective = []
    for i in range(len(interpolated_rates)):
        days.append(interpolated_rates[i].day)
        coupled.append(interpolated_rates[i].coupled)
        coupled_waiting.append(interpolated_rates[i].coupled_wait)
        coupled_queuing.append(interpolated_rates[i].coupled_queue)
        decayed_effective.append(decayed_rates[i].effective)
    pylab.plot(days, coupled, label='Coupled')
    pylab.plot(days, coupled_waiting, label='Coupled and Waiting')
    pylab.plot(days, coupled_queuing, label='Coupled and Queuing')
    pylab.plot(days, decayed_effective, label='Decaying Effective, const={}'.
               format(decay_const))
    pylab.legend(loc='best')
    pylab.ylim(ymin=0)
    pylab.ylabel('Rate (years/day)')
    pylab.xlabel('Run time (days)')
    pylab.show()
