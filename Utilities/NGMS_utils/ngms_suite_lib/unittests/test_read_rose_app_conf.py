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
import os

import read_rose_app_conf


class TestReadRoseAppConfFile(unittest.TestCase):
    '''
    Test the function to read the rose-app.conf file
    '''
    def setUp(self):
        '''Set up an example rose-app.conf file, with command, evironment var,
        file, and namelist. Have a blank line. Have a list, user igonred
        variable, and user ignored namelist'''
        rose_app_conf_contents = '''import=import1 import2
meta=my/meta/path
[command]
default=default-cmd

[env]
VAR1=val1
VAR2=some/path
[file:$DATAM]
mode=mkdir
source=
[namelist:nam1(ab)]
nl_var1=10
nl_var2=30
[!!namelist:ignore_me]
ig_var1=40
ig_var2=50
[namelist:nam2]
!user_ignored=.true.
list=1,2,3
'''
        self.test_file_name = 'test_file'
        with open(self.test_file_name, 'w') as f_h:
            f_h.write(rose_app_conf_contents)

    def tearDown(self):
        try:
            os.remove(self.test_file_name)
        except OSError:
            pass

    def test_read_rose_app_conf(self):
        '''Test the reading of the example file'''
        expected_value = {'command': [['[command]', 'default=default-cmd']],
                          'env': [['[env]', 'VAR1=val1', 'VAR2=some/path']],
                          'file': [['[file:$DATAM]', 'mode=mkdir', 'source=']],
                          'namelist': [['[namelist:nam1(ab)]', 'nl_var1=10',
                                        'nl_var2=30'],
                                       ['[namelist:nam2]', 'list=1,2,3']]}

        self.assertEqual(
            expected_value, read_rose_app_conf.read_file(
                self.test_file_name))



class TestReadRoseAppConf(unittest.TestCase):
    '''
    Test the main function
    '''
    @mock.patch('read_rose_app_conf.os.path.isfile', return_value=False)
    def test_no_file(self, mock_isfile):
        '''Test the case where no file is found'''
        self.assertEqual((1, {}), read_rose_app_conf.read_rose_app_conf(None))

    @mock.patch('read_rose_app_conf.os.path.isfile')
    @mock.patch('read_rose_app_conf.read_file')
    @mock.patch('read_rose_app_conf.read_nl_lib.variable_dict')
    def test_when_file_found(self, mock_variable_dict, mock_read_file,
                             mock_isfile):
        '''
        Test the correct behaviour for constructing the dictionary
        '''
        mock_isfile.return_value = True
        mock_read_file.return_value = {'item1': 'var1',
                                       'empty_item': [],
                                       'item2': 'var2'}
        mock_variable_dict.side_effect = [('return1'), ('return2')]
        self.assertEqual((0, {'item1': 'return1', 'item2': 'return2',
                              'empty_item': {}}),
                         read_rose_app_conf.read_rose_app_conf('fn'))
        mock_isfile.assert_called_once_with('fn')
        mock_read_file.assert_called_once_with('fn')
        mock_variable_dict.assert_has_calls([mock.call('item1', 'var1'),
                                             mock.call('item2', 'var2')])
