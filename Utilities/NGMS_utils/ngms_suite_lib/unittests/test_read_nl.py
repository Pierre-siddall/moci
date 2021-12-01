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

import read_nl


class TestReadNLFile(unittest.TestCase):
    '''
    Test the function to read the namelist file
    '''
    def setUp(self):
        '''Set up an example namelist file, wtih two namelist and a blank
        line'''
        namelist_contents = '''&nam1(ab)
nl_var1=10,
nl_var2=30,
/
&nam2

list=1,2,3,
/
'''
        self.test_file_name = 'test_file'
        with open(self.test_file_name, 'w') as f_h:
            f_h.write(namelist_contents)

    def tearDown(self):
        try:
            os.remove(self.test_file_name)
        except OSError:
            pass

    def test_read_nl(self):
        '''Test the reading of the example file'''
        expected_value = [['[namelist:nam1(ab)]', 'nl_var1=10', 'nl_var2=30'],
                          ['[namelist:nam2]', 'list=1,2,3']]

        self.assertEqual(
            expected_value, read_nl.read_nl_file(self.test_file_name))


class TestReadNL(unittest.TestCase):
    '''
    Test the main function
    '''
    @mock.patch('read_nl.os.path.isfile', return_value=False)
    def test_no_file(self, mock_isfile):
        '''Test the case where no file is found'''
        self.assertEqual((1, {}), read_nl.read_nl(None))

    @mock.patch('read_nl.os.path.isfile')
    @mock.patch('read_nl.read_nl_file')
    @mock.patch('read_nl.read_nl_lib.variable_dict')
    def test_when_file_found(self, mock_variable_dict, mock_read_file,
                             mock_isfile):
        '''
        Test the correct behaviour for constructing the dictionary
        '''
        mock_isfile.return_value = True
        mock_read_file.return_value = 'File contents'
        mock_variable_dict.return_value = 'var_dict_return'
        self.assertEqual((0, 'var_dict_return'),
                         read_nl.read_nl('filename'))
        mock_read_file.assert_called_once_with('filename')
        mock_variable_dict.assert_called_once_with('namelist', 'File contents')
