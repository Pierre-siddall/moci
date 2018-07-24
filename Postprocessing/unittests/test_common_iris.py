#!/usr/bin/env python
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2018 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
'''
import os
import unittest
try:
    # mock is integrated into unittest as of Python 3.3
    import unittest.mock as mock
except ImportError:
    # mock is a standalone package (back-ported)
    import mock

import testing_functions as func
import runtime_environment

try:
    import iris_transform
    IRIS_AVAIL = True
except ImportError:
    IRIS_AVAIL = False
    func.logtest('\n*** Iris is not available.  '
                 'All 14 IRIS tests (CubesClassTests) will be skipped.\n')

runtime_environment.setup_env()


@unittest.skipUnless(IRIS_AVAIL, 'Python module "Iris" is not available')
class CubesClassTests(unittest.TestCase):
    '''Unit tests for the IrisCubes class methods'''
    def setUp(self):
        self.testfile = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'air_temp.pp'
            )
        self.fields = {'air_temperature': 'AIR-T'}
        self.transform = iris_transform.IrisCubes(self.testfile, self.fields)
        self.cubefield = self.transform.field_attributes\
            ['air_temperature']['IrisCube']
        self.outfile = 'output.nc'

    def tearDown(self):
        try:
            os.remove(self.outfile)
        except OSError:
            pass

    def test_instantiation(self):
        '''Testinstantiation of IrisCubes '''
        func.logtest('Assert instantiation of IrisCubes object:')
        self.assertIsInstance(self.transform.field_attributes, dict)
        self.assertEqual(self.transform.field_attributes['air_temperature']
                         ['Descriptor'], 'AIR-T')
        self.assertIsInstance(self.transform.field_attributes['air_temperature']
                              ['IrisCube'], iris_transform.iris.cube.Cube)
        self.assertListEqual(
            sorted(self.transform.field_attributes['air_temperature'].keys()),
            sorted(['StartDate', 'EndDate', 'Descriptor', 'IrisCube',
                    'STASHcode', 'DataFrequency']))

    def test_instantiation_stashcode(self):
        '''Test instantiation of IrisCubes '''
        func.logtest('Assert instantiation of IrisCubes object with stashcode:')
        transform = iris_transform.IrisCubes(self.testfile, {16203: 'STASH1'})
        self.assertEqual(transform.field_attributes['16203']
                         ['Descriptor'], 'STASH1')
        self.assertIsInstance(transform.field_attributes['16203']
                              ['IrisCube'], iris_transform.iris.cube.Cube)

    def test_extract_stashcode(self):
        '''Test extraction of the STASHcode from the Iris cube'''
        func.logtest('Assert extraction of the STASHcode from the cube')
        stashcode = iris_transform.extract_stash_code(self.cubefield)
        self.assertEqual(stashcode, 16203)

    def test_extract_stashcode_none(self):
        '''Test failed extraction of the STASHcode from the Iris cube'''
        func.logtest('Assert no STASHcode extracted from the cube')
        del self.cubefield.attributes['STASH']
        stashcode = iris_transform.extract_stash_code(self.cubefield)
        self.assertEqual(stashcode, 0)

    @mock.patch('iris_transform.iris.load')
    def test_extract_data(self, mock_load):
        '''Test composition of load constraints for loading an Iris cube'''
        func.logtest('Assert composition of load constraints for Iris cube')
        _ = iris_transform.extract_data(self.testfile, self.fields)
        mock_load.assert_called_once_with(self.testfile,
                                          constraints=list(self.fields.keys()))

    @mock.patch('iris_transform.iris.load')
    def test_extract_data_stash(self, mock_load):
        '''Test composition of STASH load constraints for loading Iris cube'''
        func.logtest('Assert composition of STASH constraints for Iris cube')
        fields = {16203: 'AIR-T', 24: 'SURF-T'}

        _ = iris_transform.extract_data(self.testfile, fields)

        constraints = [
            iris_transform.iris.AttributeConstraint(STASH='m01s00i024'),
            iris_transform.iris.AttributeConstraint(STASH='m01s16i203')
            ]
        # I can't seem verify the call to mock_load directly, since apparently:
        #           iris.AttributeConstraint() != iris.AttributeConstraint()
        # mock_load.assert_called_once_with(self.testfile,
        #                                   constraints=constraints)
        self.assertEqual(mock_load.call_args[0], (self.testfile,))
        for arg in mock_load.call_args[1]['constraints']:
            self.assertIn(repr(arg), [repr(c) for c in constraints])
            self.assertIsInstance(arg, iris_transform.iris.AttributeConstraint)

    def test_extract_data_error(self):
        '''Test IOError exception for non-existent file in extract_data '''
        func.logtest('Assert IOError exception in extract_data')
        cube = iris_transform.extract_data('NO_FILE', self.fields)
        self.assertTrue(cube is None)
        self.assertIn('File does not exist', func.capture('err'))

    def test_extract_data_period(self):
        '''Test extraction of date/period information from the Iris cube'''
        func.logtest('Assert dates extraction from Iris cube')
        start, end, freq = iris_transform.extract_data_period(self.cubefield)
        # The test data has a single time data point spanning a 4 year period
        self.assertEqual(start, '19941201')
        self.assertEqual(end, '19981201')
        self.assertEqual(freq, '4y')

    def test_extract_data_period_notime(self):
        '''Test extraction of date/period info from Iris cube - no time coord'''
        func.logtest('Assert dates extraction from Iris cube - no time coord')
        self.cubefield.remove_coord('time')
        start, end, freq = iris_transform.extract_data_period(self.cubefield)
        self.assertTrue(start == end == '')
        self.assertEqual(freq, '1h')

    def test_save_netcdf(self):
        '''Test save as netCDF format'''
        func.logtest('Assert creation of netCDF file:')
        iris_transform.save_format(
            self.transform.field_attributes['air_temperature']['IrisCube'],
            self.outfile,
            'netcdf',
            {'ncftype': 'NETCDF4', 'complevel': None}
            )
        self.assertTrue(os.path.isfile(self.outfile))
        self.assertIn('Saved data to netcdf file: output.nc',
                      func.capture())

    def test_save_format_valueerror(self):
        '''Test save as given format - ValueError'''
        func.logtest('Assert creation of given format file - ValueError:')
        iris_transform.save_format(
            self.transform.field_attributes['air_temperature']['IrisCube'],
            self.outfile,
            'netcdf',
            {'ncftype': 'MYTYPE', 'complevel': 1}
            )
        self.assertFalse(os.path.isfile(self.outfile))
        self.assertIn("Unknown netCDF file format, got 'MYTYPE'",
                      func.capture('err'))
        self.assertIn('Failed to create netcdf file',
                      func.capture('err'))

    def test_save_format_keyerror(self):
        '''Test save as given format - KeyError'''
        func.logtest('Assert creation of given format file - KeyError:')
        iris_transform.save_format(
            self.transform.field_attributes['air_temperature']['IrisCube'],
            self.outfile,
            'netcdf',
            {'ncftype': 'NETCDF4'}
            )
        self.assertFalse(os.path.isfile(self.outfile))
        self.assertIn("missing keyword: 'complevel'",
                      func.capture('err'))
        self.assertIn('Failed to create netcdf file',
                      func.capture('err'))

    def test_save_format_bad_filetype(self):
        '''Test save as given format - Unrecognised filetype'''
        func.logtest('Assert creation of given format file - Bad filetype:')
        iris_transform.save_format(
            self.transform.field_attributes['air_temperature']['IrisCube'],
            self.outfile,
            'sometype',
            {}
            )
        self.assertFalse(os.path.isfile(self.outfile))
        self.assertIn("File format not recognised: sometype",
                      func.capture('err'))
        self.assertIn('Failed to create sometype file',
                      func.capture('err'))

    def test_save_format_ioerror(self):
        '''Test save as given format - IOError'''
        func.logtest('Assert creation of given format file - IOError:')
        iris_transform.save_format(
            self.transform.field_attributes['air_temperature']['IrisCube'],
            os.path.join('NO_SUCH_DIR', self.outfile),
            'netcdf',
            {'ncftype': 'NETCDF4', 'complevel': None}
            )
        self.assertFalse(os.path.isfile(self.outfile))
        self.assertIn("Could not write to file: NO_SUCH_DIR/output.nc",
                      func.capture('err'))
        self.assertIn('Failed to create netcdf file',
                      func.capture('err'))
