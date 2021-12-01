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

import generate_nam_s2

class TestGlobal(unittest.TestCase):
    '''
    Test any global variables in the module
    '''
    def test_error(self):
        '''An error code must be between 1 and 127 inclusive'''
        self.assertTrue(1 <= generate_nam_s2.GENERATE_SECTION2_ERROR <= 127)

    def test_grids(self):
        '''Test the variable linking grids to models'''
        expected_value = {'tor1': 'ocn',
                          'vor1': 'ocn',
                          'uor1': 'ocn',
                          'atm3': 'atm',
                          'avm3': 'atm',
                          'aum3': 'atm',
                          'lfric': 'lfric'}
        self.assertEqual(expected_value, generate_nam_s2.GRIDS)

class TestStrToList(unittest.TestCase):
    '''
    Test the function to allow for strings produced from length one lists in
    rose app-conf to be turned back into lists if necessary
    '''
    def test_list_to_list(self):
        '''Test that a list passes straight through'''
        test_list = ['a', 'b', 'c']
        return_list = generate_nam_s2.str_to_list(test_list)
        self.assertEqual(return_list, test_list)

    def test_string_to_list(self):
        '''Test that a string passes through as a length one list'''
        test_str = 'Hello, World!'
        expected_return = [test_str]
        return_list = generate_nam_s2.str_to_list(test_str)
        self.assertEqual(return_list, expected_return)

class TestGetLenListNoFalse(unittest.TestCase):
    '''
    Test the function that gets the length of a list (not including any items
    that evaluate to false
    '''
    def test_empty_list(self):
        '''Test the length of an empty list is zero'''
        self.assertEqual(0, generate_nam_s2.get_len_list_no_false([]))

    def test_true_list(self):
        '''Test a list of 'true' items'''
        input_list = [1, 'a', True, ['a', 'b']]
        self.assertEqual(4, generate_nam_s2.get_len_list_no_false(input_list))

    def test_false_list(self):
        '''Test a list of 'false' items'''
        input_list = [0, '', False, None, []]
        self.assertEqual(0, generate_nam_s2.get_len_list_no_false(input_list))

    def test_mix_list(self):
        '''Test a list that includes true and false items'''
        input_list = ['MAPPING', None, 'OTHER_TRANSFORM', None, None]
        self.assertEqual(2, generate_nam_s2.get_len_list_no_false(input_list))

    def test_len_1_list_true(self):
        '''Test a true length one list'''
        input_list = ['a']
        self.assertEqual(1, generate_nam_s2.get_len_list_no_false(input_list))

    def test_len_1_list_false(self):
        '''Test a false length one list'''
        input_list = ['']
        self.assertEqual(0, generate_nam_s2.get_len_list_no_false(input_list))

class TestGetModelFromGrid(unittest.TestCase):
    '''
    Test the retrieving of the model type from its grid
    '''
    def test_correct(self):
        '''Test a correct grid and its corresponding model'''
        self.assertEqual('ocn', generate_nam_s2.get_model_from_grid('tor1'))

    @mock.patch('generate_nam_s2.sys.stderr.write')
    def test_incorrect(self, mock_stderr):
        '''Test the behaviour of an incorrect grid'''
        expected_err = '[FAIL] Can not determine the model type for grid' \
                       ' wrong_grid\n'
        with self.assertRaises(SystemExit) as context:
            generate_nam_s2.get_model_from_grid('wrong_grid')
        self.assertEqual(context.exception.code,
                         generate_nam_s2.GENERATE_SECTION2_ERROR)
        mock_stderr.assert_called_with(expected_err)


class GenerateS2L1(unittest.TestCase):
    '''
    Test the generation of the first line of section 2
    '''
    @mock.patch('generate_nam_s2.get_len_list_no_false')
    def test_gen_l1_with_list(self, mock_len_list):
        '''Test the generation of line one'''
        transform_list = ['TRANSFORM_1', 'TRANSFORM_2']
        header_dict = {'mod_restart': 'model_restart.nc'}
        field_dict = {'src_name': 'source_field',
                      'trg_name': 'target_field',
                      'cpl_freq': 'coupling_frequency',
                      'transform': transform_list,
                      'fld_op': 'EXPORTED'}
        expected_output = "{} {} 1 {} {} {} {}\n".format(
            field_dict['src_name'],
            field_dict['trg_name'],
            field_dict['cpl_freq'],
            len(transform_list),
            header_dict['mod_restart'],
            field_dict['fld_op'])
        mock_len_list.return_value = len(transform_list)
        output = generate_nam_s2.gen_section_two_l1(header_dict,
                                                    field_dict,
                                                    'mod')
        mock_len_list.assert_called_once_with(transform_list)
        self.assertEqual(expected_output, output)

    @mock.patch('generate_nam_s2.get_len_list_no_false')
    def test_gen_l1_with_string(self, mock_len_list):
        '''When there is only one transform, it will be a string not a list'''
        transform = 'TRANSFORM_1'
        header_dict = {'mod_restart': 'model_restart.nc'}
        field_dict = {'src_name': 'source_field',
                      'trg_name': 'target_field',
                      'cpl_freq': 'coupling_frequency',
                      'transform': transform,
                      'fld_op': 'EXPORTED'}
        expected_output = "{} {} 1 {} {} {} {}\n".format(
            field_dict['src_name'],
            field_dict['trg_name'],
            field_dict['cpl_freq'],
            1,
            header_dict['mod_restart'],
            field_dict['fld_op'])
        output = generate_nam_s2.gen_section_two_l1(header_dict,
                                                    field_dict,
                                                    'mod')
        mock_len_list.assert_not_called()
        self.assertEqual(expected_output, output)

class GenerateS2L2(unittest.TestCase):
    '''
    Test the generation of the second line of section 2
    '''
    def setUp(self):
        self.field_dict_root = {'src_grid_name': 'source_grid_name',
                                'trg_grid_name': 'target_grid_name'}
        self.header_dict = {'source_t_dim': [20, 40],
                            'target_t_dim': [10, 20]}

    def test_positve_lag_seq(self):
        '''Test the correct generation of the line if the lag is positive'''
        i_field_dict = {'lag': 2, 'seq': 3}
        field_dict = {**self.field_dict_root, **i_field_dict}
        expected_output = " {} {} {} {} {} {} LAG=+{} SEQ=+{}\n".format(
            self.header_dict['source_t_dim'][0],
            self.header_dict['source_t_dim'][1],
            self.header_dict['target_t_dim'][0],
            self.header_dict['target_t_dim'][1],
            field_dict['src_grid_name'], field_dict['trg_grid_name'],
            field_dict['lag'], field_dict['seq'])
        output = generate_nam_s2.gen_section_two_l2(self.header_dict,
                                                    field_dict,
                                                    'source', 'target')
        self.assertEqual(expected_output, output)

    def test_negative_lag_seq(self):
        '''Test the correct generation of the line if the lag is negative'''
        i_field_dict = {'lag': -2, 'seq': -3}
        field_dict = {**self.field_dict_root, **i_field_dict}
        expected_output = " {} {} {} {} {} {} LAG={} SEQ={}\n".format(
            self.header_dict['source_t_dim'][0],
            self.header_dict['source_t_dim'][1],
            self.header_dict['target_t_dim'][0],
            self.header_dict['target_t_dim'][1],
            field_dict['src_grid_name'], field_dict['trg_grid_name'],
            field_dict['lag'], field_dict['seq'])
        output = generate_nam_s2.gen_section_two_l2(self.header_dict,
                                                    field_dict,
                                                    'source', 'target')
        self.assertEqual(expected_output, output)

class GenerateS2L3(unittest.TestCase):
    '''
    Test the generation of the third line of section 3
    '''
    @mock.patch('generate_nam_s2.sys.stderr.write')
    def test_src_dest_same_name(self, mock_stderr):
        '''Test error is reurned if the src and dest models have the same
        name'''
        error_string = "Source model and destination model have the same" \
                       " name - model\n"
        with self.assertRaises(SystemExit) as context:
            generate_nam_s2.gen_section_two_l3({}, 'model', 'model')
        self.assertEqual(context.exception.code,
                         generate_nam_s2.GENERATE_SECTION2_ERROR)
        mock_stderr.assert_called_with(error_string)

    def test_periodic_l_o(self):
        '''Test for periodic LFRic to ocean'''
        header_dict = {'lfric_periodic': True,
                       'ocn_periodic': True,
                       'ocn_wrap': 2,
                       'lfric_wrap': 3}
        expected_output = ' P 3 P 2\n'
        self.assertEqual(generate_nam_s2.gen_section_two_l3(header_dict,
                                                            'lfric', 'ocn'),
                         expected_output)

    def test_periodic_o_l(self):
        '''Test for regional Ocean to LFric'''
        header_dict = {'lfric_periodic': False,
                       'ocn_periodic': False,
                       'ocn_wrap': 2,
                       'lfric_wrap': 3}
        expected_output = ' R 2 R 3\n'
        self.assertEqual(generate_nam_s2.gen_section_two_l3(header_dict,
                                                            'ocn', 'lfric'),
                         expected_output)

    def test_periodic_o_a(self):
        '''Test for periodic ocean to UM (atm)'''
        header_dict = {'atm_periodic': True,
                       'ocn_periodic': True,
                       'ocn_wrap': 2,
                       'atm_wrap': 3}
        expected_output = ' P 2 P 3\n'
        self.assertEqual(generate_nam_s2.gen_section_two_l3(header_dict,
                                                            'ocn', 'atm'),
                         expected_output)

    def test_regional_a_o(self):
        '''Test for regional UM (atm) to ocean'''
        header_dict = {'atm_periodic': False,
                       'ocn_periodic': False,
                       'ocn_wrap': 2,
                       'atm_wrap': 3}
        expected_output = ' R 3 R 2\n'
        self.assertEqual(generate_nam_s2.gen_section_two_l3(header_dict,
                                                            'atm', 'ocn'),
                         expected_output)

class GenerateS2L4(unittest.TestCase):
    '''
    Test the generation of the fourth line of section 2
    '''
    def test_first_element_transform(self):
        '''Test if first elements work correctly'''
        field_dict = {'transform': ['MAPPING', None],
                      'transops': ['Remap', None]}
        expected_output = ' MAPPING\n Remap\n'
        self.assertEqual(generate_nam_s2.gen_section_two_l4(field_dict),
                         expected_output)

    def test_second_element_transform(self):
        '''Test if second elements work correctly'''
        field_dict = {'transform': [None, 'MAPPING', None],
                      'transops': [None, 'Remap', None]}
        expected_output = ' MAPPING\n Remap\n'
        self.assertEqual(generate_nam_s2.gen_section_two_l4(field_dict),
                         expected_output)

    def test_two_strings(self):
        '''Test if transform and transops come in as strings, as a consequence
        of how rose edit deals with length one lists'''
        field_dict = {'transform': 'MAPPING',
                      'transops': 'Remap'}
        expected_output = ' MAPPING\n Remap\n'
        self.assertEqual(generate_nam_s2.gen_section_two_l4(field_dict),
                         expected_output)

    def test_multiple_transop_multiple_transform(self):
        '''Test multiple transops and multiple transforms with offset
        distribution in list. All transops should appear on one line and all
        transforms line by line following'''
        field_dict = {'transform' : ['TRANSFORM_1', None, 'TRANSFORM_2',
                                     'TRANSFORM_3', None],
                      'transops' : ['OP1', 'OP2', None, None, 'OP3']}
        expected_output = ' TRANSFORM_1 TRANSFORM_2 TRANSFORM_3\n' \
                          ' OP1\n OP2\n OP3\n'
        self.assertEqual(generate_nam_s2.gen_section_two_l4(field_dict),
                         expected_output)

class TestGenS2Item(unittest.TestCase):
    '''
    Test top level generation function, which calls in turn the function that
    writes all the namcouple lines
    '''
    @mock.patch('generate_nam_s2.get_model_from_grid')
    @mock.patch('generate_nam_s2.gen_section_two_l1', return_value='line1')
    @mock.patch('generate_nam_s2.gen_section_two_l2', return_value='line2')
    @mock.patch('generate_nam_s2.gen_section_two_l3', return_value='line3')
    @mock.patch('generate_nam_s2.gen_section_two_l4', return_value='line4')
    def test_gen_section_two_item(self, l4_mock, l3_mock, l2_mock, l1_mock,
                                  mock_get_model):
        '''
        Test the return values and calls for the top level function
        '''
        field_dict_dummy = {'src_grid_name': 'source_grid',
                            'trg_grid_name': 'dest_grid'}
        expected_output = '###\nline1line2line3line4'
        mock_get_model.side_effect = ['source_model', 'destination_model']
        rvalue = generate_nam_s2.gen_section_two_item('header_dict',
                                                      field_dict_dummy)
        self.assertEqual(expected_output, rvalue)
        mock_get_model.assert_has_calls(
            [mock.call('source_grid'), mock.call('dest_grid')])
        l1_mock.assert_called_with('header_dict', field_dict_dummy,
                                   'source_model')
        l2_mock.assert_called_with('header_dict', field_dict_dummy,
                                   'source_model',
                                   'destination_model')
        l3_mock.assert_called_with('header_dict', 'source_model',
                                   'destination_model')
        l4_mock.assert_called_with(field_dict_dummy)
