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
import mock

import testing_functions as func
import runtime_environment

import utils

# Import of control requires 'RUNID' from runtime environment
runtime_environment.setup_env()
import control

class RunPostProcTests(unittest.TestCase):
    '''Unit tests for the RunPostProc base class'''

    def setUp(self):
        self.postp = control.RunPostProc()

    def tearDown(self):
        utils.set_debugmode(False)

    def test_abstract_methods(self):
        '''Test system exit from abstract properties'''
        func.logtest('Assert system exit from abstract properties:')
        for method in ['runpp', 'methods']:
            with self.assertRaises(SystemExit):
                getattr(self.postp, method)()

    @mock.patch('utils.check_directory', return_value='MyDir/here')
    def test_directory(self, mock_dir):
        '''Test return from _directory method'''
        func.logtest('Assert return from _directory method:')
        _ = self.postp._directory('MyDir/here', 'TITLE')
        self.assertIn('TITLE directory: MyDir/here', func.capture())
        mock_dir.assert_called_once_with('MyDir/here')

    def test_debugmode_true(self):
        '''Test debug_mode method functionality - debug_mode'''
        func.logtest('Assert successful setup of debug variables - debug_mode')
        self.postp._debug_mode(debug=True)
        self.assertTrue(self.postp.debug_ok)
        self.assertTrue(utils.get_debugok())
        self.assertTrue(utils.get_debugmode())

    def test_debugmode_false(self):
        '''Test debug_mode method functionality - live_mode'''
        func.logtest('Assert successful setup of debug variables - live_mode')
        self.postp._debug_mode()
        self.assertTrue(self.postp.debug_ok)
        self.assertTrue(utils.get_debugok())
        self.assertFalse(utils.get_debugmode())

    def test_finalise_debug_ok(self):
        '''Test finalise_debug method - ok'''
        func.logtest('Assert positive finalisation of debug:')
        self.postp.finalise_debug()
        self.assertTrue(self.postp.debug_ok)

    def test_finalise_debug_fail(self):
        '''Test finalise_debug method - fail'''
        func.logtest('Assert negative finalisation of debug:')
        utils.set_debugmode(True)
        utils.catch_failure()
        self.postp.finalise_debug()
        self.assertFalse(self.postp.debug_ok)
