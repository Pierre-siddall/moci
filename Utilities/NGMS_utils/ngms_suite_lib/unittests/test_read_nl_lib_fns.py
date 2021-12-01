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

import read_nl_lib

# Test the functions in read_nl_lib

class TestIsArray(unittest.TestCase):
    '''
    Check that variables containing commas are dealt with correctly
    '''
    def test_string_with_comma(self):
        '''A string with comma should be passed straight through'''
        self.assertEqual('Hello, world',
                         read_nl_lib.is_array("'Hello, world'"))

    def test_empty_list(self):
        '''An empty list should return a python list with that number of
        empty string elements'''
        r_value = read_nl_lib.is_array(',,,')
        self.assertEqual(r_value, ['', '', '', ''])

    def test_list_of_strings(self):
        '''Test a list of strings, one of these strings contains a comma,
        another a space after the opening quotes'''
        r_value = read_nl_lib.is_array(
            "'Hello', ' World', 'Hello, world'")
        self.assertEqual(
            r_value, ['Hello', ' World', 'Hello, world'])

    def test_other_list(self):
        '''Test a list of non string items (floats) with varying spaces'''
        r_value = read_nl_lib.is_array("1.0,2.1, 3.2,    4.3")
        self.assertEqual(r_value, ['1.0', '2.1', '3.2', '4.3'])

    def test_sparse_list(self):
        '''Test a sparse list of booleans'''
        r_value = read_nl_lib.is_array(",.true.,,.false.,")
        self.assertEqual(r_value, ['', '.true.', '', '.false.', ''])

class TestVars(unittest.TestCase):
    '''
    Unit test for testing variables
    '''
    def test_empty_string(self):
        '''Empty string doesnt return anything'''
        self.assertEqual(None, read_nl_lib.test_vars(''))

    def test_single_quote_string(self):
        ''' Check a single quoted string looses the quotes'''
        self.assertEqual('test', read_nl_lib.test_vars('\'test\''))

    def test_double_quote_string(self):
        '''Check a double quoted string looses the quotes'''
        self.assertEqual('test', read_nl_lib.test_vars('\"test\"'))

    def test_integer(self):
        ''' Check the return of an integer'''
        self.assertEqual(10, read_nl_lib.test_vars('10'))

    def test_float(self):
        '''Check the return of a float'''
        self.assertEqual(10.0, read_nl_lib.test_vars('10.0'))

    def test_scientific(self):
        '''Test the return of scientific notation as a float'''
        self.assertEqual(1000.0, read_nl_lib.test_vars('1.0e3'))

    def test_true(self):
        '''Check .true. returns python boolean True (lowercase)'''
        self.assertEqual(True, read_nl_lib.test_vars('.true.'))

    def test_false(self):
        '''Check .FALSE. returns python boolean False (uppercase)'''
        self.assertEqual(False, read_nl_lib.test_vars('.FALSE.'))

    def test_basic_string(self):
        '''A python string should just pass straight through'''
        self.assertEqual('string', read_nl_lib.test_vars('string'))


class TestGetItemName(unittest.TestCase):
    '''
    Test the retrieval of an item name, (either env, command, file, or namelist
    '''
    def test_env(self):
        '''Test that for type env, it returns itself as a name, we dont mind
        about the second argument'''
        self.assertEqual('env', read_nl_lib.get_item_name('env', None))

    def test_command(self):
        '''Test that for type command, it returns itself as a name, we dont mind
        about the second argument'''
        self.assertEqual('command',
                         read_nl_lib.get_item_name('command', None))

    def test_normal_namelist(self):
        '''Test we get the name of namelist:test_nl'''
        self.assertEqual('test_nl',
                         read_nl_lib.get_item_name('namelist',
                                                   '[namelist:test_nl]'))

    def test_bracket_namelist(self):
        '''Test we get the name of namelist:test_nl(a1b2c3)'''
        self.assertEqual('test_nl(a1b2c3)',
                         read_nl_lib.get_item_name(
                             'namelist', '[namelist:test_nl(a1b2c3)]'))

    def test_file(self):
        '''Test a simple filename'''
        self.assertEqual('filename',
                         read_nl_lib.get_item_name(
                             'file', '[file:filename]'))

    def test_file_period(self):
        '''Test a filename that contains a period'''
        self.assertEqual('filename.nl',
                         read_nl_lib.get_item_name(
                             'file', '[file:filename.nl]'))

    def test_file_two_periods(self):
        '''Test a filename that contains multiple periods'''
        self.assertEqual('filename.um.nl',
                         read_nl_lib.get_item_name(
                             'file', '[file:filename.um.nl]'))

    def test_file_envar(self):
        '''Test a simple filename that is an environment variable'''
        self.assertEqual('$DATAM',
                         read_nl_lib.get_item_name(
                             'file', '[file:$DATAM]'))

    def test_file_envar_path(self):
        '''Test a simple filename that is a delimited path, with environment
        variables'''
        self.assertEqual('$DATAM/history/$NEMO_HIST',
                         read_nl_lib.get_item_name(
                             'file', '[file:$DATAM/history/$NEMO_HIST]'))

class TestReadVariablesTypes(unittest.TestCase):
    '''
    Test the reading of variable types
    '''
    @mock.patch('read_nl_lib.get_item_name')
    @mock.patch('read_nl_lib.test_vars')
    def test_env_string(self, mock_test_vars, mock_get_item_name):
        '''Test an environment string / non namelist type'''
        line_arr = ['[env]', 'variable1=val1', 'variable2=val2']
        mock_get_item_name.return_value = 'env'
        expected_value = ('env', {'variable1':'val1', 'variable2':'val2'})
        r_value = read_nl_lib.read_variables_types('env', line_arr)
        self.assertEqual(expected_value, r_value)
        # check in this case test_vars wont be called
        mock_test_vars.assert_has_calls([])
        mock_get_item_name.assert_called_with('env', '[env]')

    @mock.patch('read_nl_lib.get_item_name')
    @mock.patch('read_nl_lib.test_vars')
    def test_namelist_string_no_comma(self, mock_test_vars, mock_get_item_name):
        '''Test a namelist string without comma'''
        line_arr = ['[namelist:nam1]', "variable1='val1'"]
        mock_get_item_name.return_value = 'nam1'
        mock_test_vars.side_effect = [('val1')]
        expected_value = ('nam1', {'variable1':'val1'})
        r_value = read_nl_lib.read_variables_types('namelist', line_arr)
        self.assertEqual(expected_value, r_value)
        # check in this case test_vars wont be called
        mock_test_vars.assert_called_with("'val1'")

    @mock.patch('read_nl_lib.get_item_name')
    @mock.patch('read_nl_lib.test_vars')
    def test_namelist_string_comma(self, mock_test_vars, mock_get_item_name):
        '''Test a namelist string comma'''
        line_arr = ['[namelist:nam1]', "variable1='val,1'"]
        mock_get_item_name.return_value = 'nam1'
        mock_test_vars.side_effect = [('val,1')]
        expected_value = ('nam1', {'variable1':'val,1'})
        r_value = read_nl_lib.read_variables_types('namelist', line_arr)
        self.assertEqual(expected_value, r_value)
        # check in this case test_vars wont be called
        mock_test_vars.assert_called_with("'val,1'")


    @mock.patch('read_nl_lib.get_item_name')
    @mock.patch('read_nl_lib.test_vars')
    def test_namelist_string_array(self, mock_test_vars, mock_get_item_name):
        '''Test a namelist string containing fortran list'''
        line_arr = ['[namelist:nam1]', 'variable1=ls1,ls2']
        mock_get_item_name.return_value = 'nam1'
        mock_test_vars.side_effect = [('ls1'), ('ls2')]
        expected_value = ('nam1', {'variable1':['ls1', 'ls2']})
        r_value = read_nl_lib.read_variables_types('namelist', line_arr)
        self.assertEqual(expected_value, r_value)
        # check in this case test_vars wont be called
        mock_test_vars.assert_has_calls([mock.call('ls1'), mock.call('ls2')])


class TestVariableDict(unittest.TestCase):
    '''
    Test the functionb variable_dict
    '''
    @mock.patch('read_nl_lib.read_variables_types')
    def test_command_type(self, mock_read_variables_types):
        '''Test the loading of command items'''
        mock_read_variables_types.side_effect = [('command', 'return1')]
        expected_calls = [mock.call('command', 'item1')]
        self.assertEqual('return1',
                         read_nl_lib.variable_dict('command',
                                                   ['item1']))
        mock_read_variables_types.assert_has_calls(expected_calls)

    @mock.patch('read_nl_lib.read_variables_types')
    def test_environment_type(self, mock_read_variables_types):
        '''Test the loading of two environmnet items'''
        mock_read_variables_types.side_effect = [('env', {'return1',
                                                          'return2'})]
        expected_calls = [mock.call('env', 'item1')]
        self.assertEqual({'return1', 'return2'},
                         read_nl_lib.variable_dict(
                             'env', ['item1']))
        mock_read_variables_types.assert_has_calls(expected_calls)

    @mock.patch('read_nl_lib.read_variables_types')
    def test_namelist_type(self, mock_read_variables_types):
        '''Test a namelist type item (that is one that isnt command or
        env)'''
        mock_read_variables_types.side_effect = [('nam1', {'var1': 'val1'}),
                                                 ('nam2', {'var2': 'val2'})]
        expected_val = {'nam1': {'var1': 'val1'},
                        'nam2': {'var2': 'val2'}}
        expected_calls = [mock.call('namelist', 'item1'),
                          mock.call('namelist', 'item2')]
        self.assertEqual(expected_val,
                         read_nl_lib.variable_dict(
                             'namelist', ['item1', 'item2']))
        mock_read_variables_types.assert_has_calls(expected_calls)
