#!/usr/bin/env python3
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2021-2025 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
'''

import unittest
import unittest.mock as mock

import sys
import mct_driver

class TestMultiglob(unittest.TestCase):
    '''
    Test the multiglob function
    '''
    def test_no_arguments(self):
        '''If there are no arguments return an empty list'''
        self.assertEqual(mct_driver._multiglob(), [])

    @mock.patch('mct_driver.glob.glob')
    def test_one_argument(self, mock_glob):
        '''Test a single argument'''
        mock_glob.return_value = ['file1']
        self.assertEqual(mct_driver._multiglob('arg1'), ['file1'])
        mock_glob.assert_called_once_with('arg1')

    @mock.patch('mct_driver.glob.glob')
    def test_multiple(self, mock_glob):
        '''Test multiple argument and variety of returns'''
        mock_glob.side_effect = [['file1'], [], ['file2', 'file3']]
        self.assertEqual(mct_driver._multiglob('arg1', 'arg2', 'arg3'),
                         ['file1', 'file2', 'file3'])
        mock_glob.assert_has_calls([mock.call('arg1'),
                                    mock.call('arg2'),
                                    mock.call('arg3')])

class TestSetupLFRicCpld(unittest.TestCase):
    '''
    Test the setting up for LFRic for coupling
    '''
    @mock.patch('mct_driver.glob.glob')
    @mock.patch('mct_driver.common.remove_file')
    def test_setup_lfric_cpld(self, mock_rmfile, mock_glob):
        '''Test the function'''
        lfric_envar = {'LFRIC_LINK': 'lfric_link'}
        mock_glob.return_value = ['file1', 'file2']
        mct_driver._setup_lfric_cpld(None, None, lfric_envar)
        mock_glob.assert_called_once_with('*lfric_link*.nc')
        mock_rmfile.assert_has_calls([mock.call('file1'), mock.call('file2')])


class TestGenerateNGMSNamcouple(unittest.TestCase):
    '''
    Test the generation of the NGMS namcouple file
    '''
    def cleanup_modules(self):
        '''Cleanup the mocked modules at the end of a test'''
        try:
            sys.modules.pop('generate_nam')
        except KeyError:
            pass

    def tearDown(self):
        '''Cleanup at end of model run'''
        self.cleanup_modules()

    @mock.patch('mct_driver.sys.stderr.write')
    def test_missing_module(self, mock_stderr):
        '''Test that when the generate_nam module is missing we exit'''
        with self.assertRaises(SystemExit) as context:
            mct_driver._generate_ngms_namcouple()
        mock_stderr.assert_called_with(
            'This run requires access to the MOCI namcouple'
            ' generation library\n. Please ensure this is'
            ' available\n')

    @mock.patch('mct_driver._multiglob')
    @mock.patch('mct_driver.common.remove_file')
    def test_correct_run(self, mock_rmfile, mock_multiglob):
        '''Test the function makes the correct calls. We dont want to delete
        any python modules'''
        sys.modules['generate_nam'] = mock.MagicMock()
        mock_multiglob.return_value = ['file1', 'file2', 'file3.py']
        with mock.patch.object(sys.modules['generate_nam'],
                               'generate_nam') as mock_gen:
            mct_driver._generate_ngms_namcouple()

        mock_multiglob.assert_called_with('namcouple*')
        self.assertEqual(mock_rmfile.mock_calls,
                         [mock.call('file1'), mock.call('file2')])
        mock_gen.assert_called_with(
            'cpl_configuration.nml', 'namcouple', 'namelist')
        # We need to remove the mocked generate_nam so other tests behave
        # correctly
        self.cleanup_modules()
