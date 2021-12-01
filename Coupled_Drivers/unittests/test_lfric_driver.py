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
'''

import unittest
import unittest.mock as mock

import dr_env_lib.lfric_def
import lfric_driver

class TestSentCouplingFields(unittest.TestCase):
    '''
    Test the sent coupling fields dummy function
    '''
    def test_sent_coupling_fields(self):
        '''Run info should pass through, and should also return None as a
        second value'''
        self.assertEqual(lfric_driver._sent_coupling_fields(None, 'run_info'),
                         ('run_info', None))


class TestSetupExecutable(unittest.TestCase):
    '''
    Test the loading of environment variables and file copies
    '''
    @mock.patch('lfric_driver.dr_env_lib.env_lib.LoadEnvar')
    @mock.patch('lfric_driver.dr_env_lib.env_lib.load_envar_from_definition')
    @mock.patch('lfric_driver.common.remove_file')
    @mock.patch('lfric_driver.os.symlink')
    def test_setup_executable(
            self, mock_link, mock_rmfile, mock_load_def, mock_load):
        '''Test the _setup_executable function'''
        lfric_envar = {'LFRIC_LINK': 'link',
                       'LFRIC_EXEC': 'executable'}
        mock_load.return_value = 'lfric_envar'
        mock_load_def.return_value = lfric_envar
        return_lfric_envar = lfric_driver._setup_executable(None, None)
        mock_load.assert_called_once_with()
        mock_load_def.assert_called_once_with(
            'lfric_envar', dr_env_lib.lfric_def.LFRIC_ENVIRONMENT_VARS_INITIAL)
        mock_rmfile.assert_called_once_with('link')
        mock_link.assert_called_once_with('executable', 'link')
        self.assertEqual(return_lfric_envar, lfric_envar)


class TestFinalizeExecutable(unittest.TestCase):
    '''
    Test the finalizing of the executable
    '''
    def test_finalize_executable(self):
        '''Test the finalize. It does nothing at the moment'''
        self.assertIsNone(lfric_driver._finalize_executable(None))



class TestRunDriver(unittest.TestCase):
    '''
    Test the interface to run the driver
    '''
    @mock.patch('lfric_driver._setup_executable')
    @mock.patch('lfric_driver._finalize_executable')
    def test_run_driver_finalize(self, mock_finalize, mock_setup):
        '''Test finalise mode'''
        rvalue = lfric_driver.run_driver('common_env', 'finalize', 'run_info')
        self.assertEqual(rvalue, (None, None, 'run_info', None))
        mock_setup.assert_not_called()
        mock_finalize.assert_called_once_with('common_env')

    @mock.patch('lfric_driver._setup_executable')
    @mock.patch('lfric_driver._finalize_executable')
    def test_run_driver_failure(self, mock_finalize, mock_setup):
        '''Test finalise mode'''
        rvalue = lfric_driver.run_driver('common_env', 'failure', 'run_info')
        self.assertEqual(rvalue, (None, None, 'run_info', None))
        mock_setup.assert_not_called()
        mock_finalize.assert_not_called()

    @mock.patch('lfric_driver._setup_executable')
    @mock.patch('lfric_driver._set_launcher_command')
    @mock.patch('lfric_driver._sent_coupling_fields')
    @mock.patch('lfric_driver._finalize_executable')
    def test_run_driver_l_namcouple(self, mock_finalize, mock_namc,
                                    mock_launcher_cmd, mock_setup):
        '''Test run mode with l_namcouple set in run info'''
        run_info = {'l_namcouple': True}
        common_env = {'ROSE_LAUNCHER': 'launcher'}
        mock_setup.return_value = 'exe_envar'
        mock_launcher_cmd.return_value = 'launch_cmd'
        rvalue = lfric_driver.run_driver(common_env, 'run_driver', run_info)
        self.assertEqual(rvalue, ('exe_envar', 'launch_cmd', run_info, None))
        mock_setup.assert_called_once_with(common_env, run_info)
        mock_launcher_cmd.assert_called_once_with('launcher', 'exe_envar')
        mock_namc.assert_not_called()
        mock_finalize.assert_not_called()

    @mock.patch('lfric_driver._setup_executable')
    @mock.patch('lfric_driver._set_launcher_command')
    @mock.patch('lfric_driver._sent_coupling_fields')
    @mock.patch('lfric_driver._finalize_executable')
    def test_run_driver_no_l_namcouple(
            self, mock_finalize, mock_namc, mock_launcher_cmd, mock_setup):
        '''Test run mode with l_namcouple set to false in run info'''
        run_info = {'l_namcouple': False}
        common_env = {'ROSE_LAUNCHER': 'launcher'}
        mock_setup.return_value = 'exe_envar'
        mock_launcher_cmd.return_value = 'launch_cmd'
        mock_namc.return_value = ('run_info', 'model_snd_list')
        rvalue = lfric_driver.run_driver(common_env, 'run_driver', run_info)
        self.assertEqual(
            rvalue, ('exe_envar', 'launch_cmd', 'run_info', 'model_snd_list'))
        mock_setup.assert_called_once_with(common_env, run_info)
        mock_launcher_cmd.assert_called_once_with('launcher', 'exe_envar')
        mock_namc.assert_called_once_with('exe_envar', run_info)
        mock_finalize.assert_not_called()
