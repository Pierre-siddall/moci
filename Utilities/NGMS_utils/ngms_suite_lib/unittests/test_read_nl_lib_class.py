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

# Test the classes in read_nl_lib
class MultipleNameDictionaryNamelistTest(unittest.TestCase):
    '''
    Test the class MultipleNameDictionary and its methods when the type set
    during initialisation is namelist
    '''
    def setUp(self):
        '''Instantiate the MultipleNameDictionary object'''
        self.multiplename = read_nl_lib.MultipleNameDictionary('namelist')

    def tearDown(self):
        '''Delete the MultipleNameDictionary object at the end of tests'''
        del self.multiplename

    def reset(self):
        '''Reset the MultipleNameDictionary object between tests'''
        del self.multiplename
        self.multiplename = read_nl_lib.MultipleNameDictionary('namelist')

    def test_init(self):
        '''Test the instantiation of the object'''
        self.assertIsInstance(self.multiplename,
                              read_nl_lib.MultipleNameDictionary)
        self.assertTrue(self.multiplename.isnamelist)
        self.assertEqual(self.multiplename.dictionary_of_nls, {})
        self.assertEqual(self.multiplename.initial_count_val, 1)
        self.assertEqual(self.multiplename.namelist_counter, {})

    def test_iadd(self):
        '''Test the overriding of += operator for non namelist then reset'''
        self.multiplename += ('namelistA', 'valueA1')
        self.multiplename += ('namelistA', 'valueA2')
        self.multiplename += ('namelistB', 'valueB')
        self.multiplename += ('namelistC', 33)
        self.assertIsInstance(self.multiplename,
                              read_nl_lib.MultipleNameDictionary)
        self.assertEqual(self.multiplename.dictionary_of_nls,
                         {'namelistA': 'valueA1',
                          'namelistA.1': 'valueA2',
                          'namelistB': 'valueB',
                          'namelistC': 33})
        self.assertEqual(self.multiplename.namelist_counter,
                         {'namelistA': 2, 'namelistB': 1, 'namelistC': 1})
        self.reset()

    def test_tidy_multiple(self):
        '''Test the tidying of non multiple items'''
        self.multiplename.namelist_counter = {
            'single_item_1': 1,
            'multiple_item_1': 10,
            'multiple_item_2': 20,
            'single_item_2': 1}
        self.multiplename.tidy_multiple()
        self.assertEqual(self.multiplename.namelist_counter,
                         {'multiple_item_1': 10, 'multiple_item_2': 20})
        self.reset()

    def test_zero_pad(self):
        '''Test the zeropadding of multiple items'''
        # create our multiple items, a set of 11 and a set of 101
        self.multiplename.namelist_counter = {
            'multiple11': 11, 'multiple101': 101}
        dictionary_of_nls = {
            'multiple11': 'val11_0', 'multiple101': 'val101_0',
            'single': 'singleval'}
        expected_return = {
            'multiple11.00': 'val11_0', 'multiple101.000': 'val101_0',
            'single': 'singleval'}
        for i in range(101):
            number = i+1
            if number <= 11:
                dictionary_of_nls[
                    'multiple11.{}'.format(number)] = 'val11_{}'.format(number)
                expected_return[
                    'multiple11.{:02d}'.format(number)] \
                    = 'val11_{}'.format(number)
            dictionary_of_nls[
                'multiple101.{}'.format(number)] = 'val101_{}'.format(number)
            expected_return[
                'multiple101.{:03d}'.format(number)] \
                = 'val101_{}'.format(number)
        self.multiplename.dictionary_of_nls = dictionary_of_nls
        self.assertEqual(expected_return, self.multiplename.zero_pad())

    def test_get_dir(self):
        '''Test get dir if we have a namelist'''
        self.multiplename.tidy_multiple = mock.MagicMock()
        self.multiplename.zero_pad = mock.MagicMock()
        self.multiplename.zero_pad.return_value = 'zero_padded'
        self.assertEqual(self.multiplename.get_dir(), 'zero_padded')
        self.multiplename.tidy_multiple.assert_called_once_with()
        self.multiplename.zero_pad.assert_called_once_with()
        self.reset()



class MultipleNameDictionaryNonNamelistTest(unittest.TestCase):
    '''
    Test the class MultipleNameDictionary and its methods when the type set
    during initialisation is not namelist
    '''
    def setUp(self):
        self.multiplename = read_nl_lib.MultipleNameDictionary('list')

    def tearDown(self):
        del self.multiplename

    def reset(self):
        '''Reset the MultipleNameDictionary object between tests'''
        del self.multiplename
        self.multiplename = read_nl_lib.MultipleNameDictionary('list')

    def test_init(self):
        '''Test the instantiation of the object'''
        self.assertFalse(self.multiplename.isnamelist)

    def test_iadd(self):
        '''Test the overriding of += operator for a non namelist object'''
        self.multiplename += ('varA', 'valueA')
        self.multiplename += ('varB', 'valueB')
        self.assertIsInstance(self.multiplename,
                              read_nl_lib.MultipleNameDictionary)
        self.assertEqual(self.multiplename.dictionary_of_nls,
                         {'varA': 'valueA', 'varB': 'valueB'})
        self.reset()

    def test_get_dir(self):
        '''Test get dir if we have a non namelist'''
        self.multiplename.dictionary_of_nls = 'dictionary_of_nls'
        self.assertEqual(self.multiplename.get_dir(), 'dictionary_of_nls')
        self.reset()
