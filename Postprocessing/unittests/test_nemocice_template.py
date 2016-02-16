#!/usr/bin/env python2.7
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2015 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
'''
import unittest
import os
import mock
import sys
sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(__file__)))+'/common')
sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(__file__)))+'/nemocice')

import runtimeEnvironment
import testing_functions as func
import modeltemplate


class MeansTests(unittest.TestCase):
    '''Unit tests relating to creation of means'''

    def setUp(self):
        with mock.patch('nlist.loadNamelist'):
            with mock.patch('suite.SuiteEnvironment'):
                self.model = modeltemplate.ModelTemplate()
        self.model.suite.envars.CYLC_SUITE_INITIAL_CYCLE_POINT = \
            '19950821T0000Z'
        self.model.nl.debug = False
        self.model.nl.restart_directory = os.environ['PWD']

        self.model.move_to_share = mock.Mock()
        self.model.loop_inputs = mock.Mock()
        self.model.loop_inputs.return_value = \
            [modeltemplate.RegexArgs(period='Annual')]
        self.model.periodend = mock.Mock()
        self.model.periodend.return_value = ['setend']
        self.model.get_date = mock.Mock()
        self.model.get_date.return_value = ('1996', '09', '01')
        self.model.periodset = mock.Mock()
        self.model.periodset.return_value = ['file1', 'file2',
                                             'file3', 'file4']
        self.model.meantemplate = mock.Mock()
        self.model.meantemplate.return_value = 'meanfilename'

    def tearDown(self):
        try:
            os.remove('nemocicepp.nl')
        except OSError:
            pass

    @mock.patch('os.path')
    @mock.patch('utils.exec_subproc')
    def test_create_annual_mean(self, mock_exec, mock_path):
        '''Test successful creation of annual mean'''
        func.logtest('Assert successful creation of annual mean:')
        mock_exec.return_value = (0, '')
        mock_path.return_value = True
        self.model.create_means()
        self.assertIn('Created .* Annual mean for 1996', func.capture())

    @mock.patch('utils.remove_files')
    @mock.patch('os.path')
    @mock.patch('utils.exec_subproc')
    def test_create_monthly_mean(self, mock_exec, mock_path, mock_rm):
        '''Test successful creation of monthly mean'''
        func.logtest('Assert successful creation of monthly mean:')
        self.model.loop_inputs.return_value = \
            [modeltemplate.RegexArgs(period='Monthly')]
        self.model.periodset.return_value = ['file1', 'file2', 'file3']
        mock_exec.return_value = (0, '')
        mock_path.return_value = True

        self.model.create_means()
        self.assertIn('Created .* Monthly mean for', func.capture())
        mock_rm.assert_called_with(['file1', 'file2', 'file3'],
                                   os.environ['PWD'])

    @mock.patch('os.path')
    @mock.patch('utils.exec_subproc')
    def test_create_annual_mean_fail(self, mock_exec, mock_path):
        '''Test failed creation of annual mean'''
        func.logtest('Assert failed creation of annual mean:')
        mock_exec.return_value = (99, '')
        mock_path.return_value = True
        with self.assertRaises(SystemExit):
            self.model.create_means()
        self.assertIn('Error=99', func.capture('err'))

        self.model.nl.debug = True
        self.model.create_means()
        self.assertIn('Error=99', func.capture('err'))

    def test_create_means_partial(self):
        '''Test create_means function with partial period'''
        func.logtest('Assert create_means functionality with partial period:')
        self.model.periodset.return_value = ['file1', 'file2', 'file3']

        with self.assertRaises(SystemExit):
            self.model.create_means()
        self.assertIn('not possible as only got 3', func.capture('err'))

        self.model.nl.debug = True
        self.model.create_means()
        self.assertIn('not possible as only got 3', func.capture('err'))
        self.assertIn('[DEBUG]  Ignoring failed', func.capture())

    def test_create_means_spinup(self):
        '''Test create_means function in spinup mode'''
        func.logtest('Assert create_means functionality in spinup:')
        self.model.periodset.return_value = ['file1', 'file2', 'file3']
        self.model.get_date.return_value = ('1995', '09', '01')

        self.model.create_means()
        self.assertIn('in spinup mode', func.capture())
        self.assertIn('not possible as only got 3', func.capture())

    def test_annual_mean_spinup(self):
        '''Test Spinup period for annual means'''
        func.logtest('Assert initial spinup period for annual means:')

        self.assertTrue(self.model.means_spinup(
            'FIELD Annual mean for YYYY', ('1995', '12', '01')))
        self.assertFalse(self.model.means_spinup(
            'FIELD Annual mean for YYYY', ('1996', '12', '01')))

    def test_seasonal_mean_spinup(self):
        '''Test Spinup period for seasonal means'''
        func.logtest('Assert initial spinup period for seasonal means:')

        self.assertTrue(self.model.means_spinup(
            'FIELD Seasonal mean for SEASON YYYY', ('1995', '09', '01')))

        self.model.suite.envars.CYLC_SUITE_INITIAL_CYCLE_POINT = \
            '19950601T0000Z'
        self.assertFalse(self.model.means_spinup(
            'FIELD Seasonal mean for SEASON YYYY', ('1995', '09', '01')))
        self.assertFalse(self.model.means_spinup(
            'FIELD Seasonal mean for SEASON YYYY', ('1995', '12', '01')))

    def test_monthly_mean_spinup(self):
        '''Test Spinup period for monthly means'''
        func.logtest('Assert initial spinup period for monthly means:')

        self.assertTrue(self.model.means_spinup(
            'FIELD Monthly mean for MONTH YYYY', ('1995', '09', '01')))
        self.assertFalse(self.model.means_spinup(
            'FIELD Monthly mean for MONTH YYYY', ('1995', '10', '01')))

        self.model.suite.envars.CYLC_SUITE_INITIAL_CYCLE_POINT = \
            '19950901T0000Z'
        self.assertFalse(self.model.means_spinup(
            'FIELD Monthly mean for MONTH YYYY', ('1995', '10', '01')))

    def test_spinup_invalid(self):
        '''Test Spinup period for invalid means'''
        func.logtest('Assert initial spinup period for invalid means:')
        self.assertFalse(self.model.means_spinup(
            'FIELD INVALID mean for YYYY', ('1995', '10', '01')))
        self.assertIn('[WARN]', func.capture('err'))
        self.assertIn('unknown meantype', func.capture('err'))


def main():
    '''Main function'''
    unittest.main(buffer=True)


if __name__ == '__main__':
    main()
