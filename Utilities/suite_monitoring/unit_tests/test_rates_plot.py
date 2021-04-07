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
    test_rates_plot.py

DESCRIPTION
    Unit test the rates_plot.py module
'''

import unittest
try:
    # mock is integrated into unittest as of Python 3.3
    import unittest.mock as mock
except ImportError:
    # mock is a standalone package (back-ported)
    import mock

import rates_lib
import rates_plot

class GraphTest(unittest.TestCase):
    '''
    Check that the plotting hasn't been broken
    '''
    def setUp(self):
        self.input_rates = []
        for i in range(6):
            self.input_rates.append(
                rates_lib.RATES._make(5*[i]))
        self.interval = 0.5
        self.decay_const = 0.5

    @mock.patch('rates_plot.pylab')
    def test_plotting_of_rates(self, plot):
        '''
        Check that all the calls to plot the graph work
        '''
        rates_plot.plot_interpolated_rates(self.input_rates,
                                           self.interval, self.decay_const,
                                           filter_start=1,
                                           filter_end=2)
        #expected calls to plot
        plot_calls = [mock.call([1.0, 1.5, 2.0], [1.0, 1.5, 2.0],
                                label='Coupled'),
                      mock.call([1.0, 1.5, 2.0], [1.0, 1.5, 2.0],
                                label='Coupled and Waiting'),
                      mock.call([1.0, 1.5, 2.0], [1.0, 1.5, 2.0],
                                label='Coupled and Queuing'),
                      mock.call([1.0, 1.5, 2.0], [1.0, 1.25, 1.625],
                                label='Decaying Effective, const={}'.
                                format(self.decay_const))]
        plot.plot.assert_has_calls(plot_calls)

    @mock.patch('rates_plot.pylab')
    def test_graph_formatting(self, plot):
        '''
        Make sure that we still have axis labels etc
        '''
        rates_plot.plot_interpolated_rates(self.input_rates,
                                           self.interval, self.decay_const,
                                           filter_start=1,
                                           filter_end=2)
        plot.legend.assert_called_once_with(loc='best')
        plot.ylim.assert_called_once_with(ymin=0)
        plot.ylabel.assert_called_once_with('Rate (years/day)')
        plot.xlabel.assert_called_once_with('Run time (days)')
