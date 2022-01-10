#!/usr/bin/env python
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2022 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
'''

import unittest
try:
    # mock is integrated into unittest as of Python 3.3
    import unittest.mock as mock
except ImportError:
    # mock is a standalone package (back-ported)
    import mock

import io
import os
import sys
import cpmip_um
import error

class TestIsMule(unittest.TestCase):
    '''
    Test the helper function that determines if mule is avaliable
    '''
    @mock.patch.object(cpmip_um.sys, 'modules', [])
    def test_no_mule(self):
        '''
        Test that False is returned if mule not avaliable
        '''
        self.assertFalse(cpmip_um._is_mule())

    @mock.patch.object(cpmip_um.sys, 'modules', ['mule'])
    def test_is_mule(self):
        '''
        Test that True is returned if mule avaliable
        '''
        self.assertTrue(cpmip_um._is_mule())

class TestUpdateInput(unittest.TestCase):
    '''
    Test the input update for the UM
    '''
    def create_input_files(self):
        '''
        Create test namelist files
        '''
        shared_file = '&TESTNL_SHARED\n' \
                      'ltimer=x,\n' \
                      'l_oasis_timers=x,\n' \
                      'lstashdumptimer=x,\n' \
                      '/\n'
        with open('SHARED', 'w') as sh_fh:
            sh_fh.write(shared_file)

        iosctl_file = '&TESTNL_IOSCNTL\n' \
                      'prnt_writers=x,\n' \
                      '/\n'
        with open('IOSCNTL', 'w') as ios_fh:
            ios_fh.write(iosctl_file)

    def remove_files(self):
        '''
        Remove test namelist files
        '''
        for f_to_delete in ['SHARED', 'IOSCNTL']:
            try:
                os.remove(f_to_delete)
            except FileNotFoundError:
                pass

    def tearDown(self):
        '''
        If there are any remaining files at the end of the test, remove them
        '''
        self.remove_files()


    def test_wrong_version_number(self):
        '''
        The UM version number has to be a number that can be turned into
        a float
        '''
        cpmip_envar = {'VN': 'bob'}
        expected_error = 'Expecting a numerical value for UM Version in' \
                         ' environment variable VN. Instead got bob\n'
        with mock.patch('sys.stderr', new=io.StringIO()) as patch_err:
            with self.assertRaises(SystemExit) as context:
                cpmip_um.update_input_for_metrics_um(cpmip_envar, None, None)
        self.assertEqual(patch_err.getvalue(), expected_error)
        self.assertEqual(context.exception.code, error.INVALID_EVAR_ERROR)


    def test_version_lt107(self):
        '''
        Versions lower than 10.7 need to set ltimer to be true
        '''
        self.create_input_files()
        cpmip_envar = {'VN': '10.6', 'IO_COST': 'false'}
        expected_shared = '&TESTNL_SHARED\n' \
                          'ltimer=.true.,\n' \
                          'l_oasis_timers=x,\n' \
                          'lstashdumptimer=x,\n' \
                          '/\n'
        expected_ioscntl = '&TESTNL_IOSCNTL\n' \
                           'prnt_writers=2,\n' \
                           '/\n'
        nn_timing_val = cpmip_um.update_input_for_metrics_um(cpmip_envar,
                                                             'SHARED',
                                                             'IOSCNTL')
        self.assertEqual(nn_timing_val, 1)
        with open('SHARED', 'r') as shared_fh:
            shared_out = shared_fh.read()
        with open('IOSCNTL', 'r') as ioscntl_fh:
            ioscntl_out = ioscntl_fh.read()
        self.assertEqual(shared_out, expected_shared)
        self.assertEqual(ioscntl_out, expected_ioscntl)
        self.remove_files()

    def test_version_107_io_cost(self):
        '''
        Versions higher than 10.7 can set l_oasis_timers to true, and ltimer
        to false. When the IO cost metric is active lstashdumptimer is set
        to true also
        '''
        self.create_input_files()
        cpmip_envar = {'VN': '10.7', 'IO_COST': 'True'}
        expected_shared = '&TESTNL_SHARED\n' \
                          'ltimer=.false.,\n' \
                          'l_oasis_timers=.true.,\n' \
                          'lstashdumptimer=.true.,\n' \
                          '/\n'
        expected_ioscntl = '&TESTNL_IOSCNTL\n' \
                           'prnt_writers=2,\n' \
                           '/\n'
        nn_timing_val = cpmip_um.update_input_for_metrics_um(cpmip_envar,
                                                             'SHARED',
                                                             'IOSCNTL')
        self.assertEqual(nn_timing_val, 2)
        with open('SHARED', 'r') as shared_fh:
            shared_out = shared_fh.read()
        with open('IOSCNTL', 'r') as ioscntl_fh:
            ioscntl_out = ioscntl_fh.read()
        self.assertEqual(shared_out, expected_shared)
        self.assertEqual(ioscntl_out, expected_ioscntl)
        self.remove_files()


class TestUMPeOutputName(unittest.TestCase):
    '''
    Test the construction of the name of the PEO output file
    '''
    def setUp(self):
        '''
        Set up environment variable dictionary
        '''
        self.cpmip_envar = {'STDOUT': 'stdout.pe'}

    @mock.patch('cpmip_um.get_um_info', return_value=(1, 2, 3))
    def test_100_mpi_ranks(self, mock_get_um_info):
        '''
        Test with 100 MPI ranks the file has a 2 digit suffix
        '''
        self.assertEqual(cpmip_um.time_resources_um(self.cpmip_envar,
                                                    100, 'STDOUT'),
                         (1, 2, 3, 'stdout.pe00'))

    @mock.patch('cpmip_um.get_um_info', return_value=(1, 2, 3))
    def test_500_mpi_ranks(self, mock_get_um_info):
        '''
        Test with 500 MPI ranks the file has 3 digit suffix
        '''
        self.assertEqual(cpmip_um.time_resources_um(self.cpmip_envar,
                                                    500, 'STDOUT'),
                         (1, 2, 3, 'stdout.pe000'))


class TestGetUMInfo(unittest.TestCase):
    '''
    Test the retieval of the UM coupling timers
    '''
    def setUp(self):
        # Non hybrid
        self.pe0_output_name = 'test_pe0'
        self.pe0_empty_outputname = 'test_pe0_empty'
        open(self.pe0_empty_outputname, 'w').close()

        example_pe0 = '''
5 oasis3_inita2o  1  0.00  0.00  0.00  0.00  0.00  0.00  0.98

MPP Timing information :
1512 processors in atmosphere configuration 42 x 36
Number of OMP threads : 1

MPP : Non Inclusive timer summary

WALLCLOCK  TIMES
N ROUTINE  MEAN  MEDIAN  SD  % of mean  MAX (PE)  MIN (PE)
1 UM_SHELL  3685.30  3685.29  0.01  0.00%  3685.31 ( 608)  3685.29 (1060)
2 oasis3_geto2a  109.77  109.77  0.01  0.01%  109.78 ( 196)  109.75 ( 609)
3 oasis3_puta2o  20.91  20.91  0.00  0.00%  20.91 ( 941)  20.91 (  52)
4 oasis3_grid  0.01  0.00  0.31  ******% 12.03 (   0)  0.00 (   1)
5 oasis3_inita2o  0.00  0.00  0.00  ******%  0.00 (   0)  0.00 (   1)

CPU TIMES (sorted by wallclock times)
N ROUTINE  MEAN  MEDIAN  SD % of mean  MAX (PE)  MIN  (PE)
1 UM_SHELL  3665.21  3665.44  2.08  0.06%  3669.20 ( 735)  3607.97 (   0)
        '''
        with open(self.pe0_output_name, 'w') as test_pe0:
            test_pe0.write(example_pe0)

        #Hybrid
        self.pe0_hybrid_name = 'test_pe0_hybrid'
        example_hybrid_pe0 = '''
MPP : Non Inclusive timer summary

WALLCLOCK  TIMES
N ROUTINE  MEAN  MEDIAN  SD  % of mean  MAX (PE)  MIN (PE)
1 UM_SHELL  3685.30  3685.29  0.01  0.00%  3685.31 ( 608)  3685.29 (1060)
2 oasis3_geto2a  109.77  109.77  0.01  0.01%  109.78 ( 196)  109.75 ( 609)
3 oasis3_puta2o  20.91  20.91  0.00  0.00%  20.91 ( 941)  20.91 (  52)
4 oasis3_get_hybrid  11.30  11.30  0.00  0.00%  11.30 ( 240)  11.30 (  14)
5 oasis3_put_hybrid  3.45  3.45  0.00  0.00%  3.45 (   3)  3.45 (1001)
4 oasis3_grid  0.01  0.00  0.31  ******% 12.03 (   0)  0.00 (   1)
5 oasis3_inita2o  0.00  0.00  0.00  ******%  0.00 (   0)  0.00 (   1)

CPU TIMES (sorted by wallclock times)
N ROUTINE  MEAN  MEDIAN  SD % of mean  MAX (PE)  MIN  (PE)
1 UM_SHELL  3923.21  3665.44  2.08  0.06%  3669.20 ( 735)  3607.97 (   0)
        '''
        with open(self.pe0_hybrid_name, 'w') as test_pe0_hybrid:
            test_pe0_hybrid.write(example_hybrid_pe0)

    def tearDown(self):
        '''
        Remove any files at the end of the run
        '''
        for f_to_delete in [self.pe0_output_name, self.pe0_empty_outputname,
                            self.pe0_hybrid_name]:
            try:
                os.remove(f_to_delete)
            except FileNotFoundError:
                pass

    def test_peoutput(self):
        '''
        Test the measurement of oasis timings from the UM
        '''
        expected_result = (3685.3, 130.69, 20.91)
        self.assertEqual(cpmip_um.get_um_info(self.pe0_output_name),
                         expected_result)

    def test_peoutput_hybrid(self):
        '''
        Test the measurement of oasis timings from the UM for the hybrid
        model
        '''
        expected_result = (3685.3, 145.44, 24.36)
        self.assertEqual(cpmip_um.get_um_info(self.pe0_hybrid_name),
                         expected_result)

    def test_peoutput_error(self):
        '''
        Test the error message reports correctly
        '''
        expected_output = '[FAIL] Unable to determine Oasis timings from' \
                          ' the UM standard output\n'
        with mock.patch('sys.stderr', new=io.StringIO()) as patch_output:
            with self.assertRaises(SystemExit) as context:
                cpmip_um.get_um_info(self.pe0_empty_outputname)
        self.assertEqual(patch_output.getvalue(), expected_output)
        self.assertEqual(context.exception.code,
                         error.MISSING_CONTROLLER_FILE_ERROR)


class TestGetUMIO(unittest.TestCase):
    '''
    Test the retieval of the UM coupling timers
    '''
    def setUp(self):
        '''
        Create example processor output files
        '''
        self.pe0_output_name = 'test_pe0'
        self.pe0_empty_outputname = 'test_pe0_empty'
        open(self.pe0_empty_outputname, 'w').close()

        example_pe0 = '''
Number of OMP threads : 1

MPP : Inclusive timer summary

WALLCLOCK  TIMES
N ROUTINE  MEAN  MEDIAN  SD  % of mean  MAX (PE)  MIN (PE)
1 AS STASH  109.77  109.77  0.01  0.01%  109.78 ( 196)  109.75 ( 609)
2 DUMPCTL  20.91  20.91  0.00  0.00%  20.91 ( 941)  20.91 (  52)

CPU TIMES (sorted by wallclock times)
N ROUTINE  MEAN  MEDIAN  SD % of mean  MAX (PE)  MIN  (PE)
1 AS STASH  3665.21  3665.44  2.08  0.06%  3669.20 ( 735)  3607.97 (   0)
        '''
        with open(self.pe0_output_name, 'w') as test_pe0:
            test_pe0.write(example_pe0)

    def tearDown(self):
        '''
        Remove any files that still exist at the end of the test
        '''
        for f_to_delete in [self.pe0_output_name, self.pe0_empty_outputname]:
            try:
                os.remove(f_to_delete)
            except FileNotFoundError:
                pass

    def test_peoutput(self):
        '''
        Test the measurement of oasis timings from the UM
        '''
        expected_1 = '[INFO] IO timings running, routine IOS_Shutdown' \
                     ' unavaliable in this configuration\n'
        expected_2 = '[INFO] IO timings running, routine' \
                     ' IOS_stash_client_fini unavaliable in this' \
                     ' configuration\n'
        expected_3 = '[INFO] IO timings running, routine MEANCTL' \
                     ' unavaliable in this configuration\n'
        expected_result = 130.68
        with mock.patch('sys.stdout', new=io.StringIO()) as patch_output:
            result = cpmip_um.get_um_io(self.pe0_output_name)
        # The missing routines get written to stdout in an order that can't
        # be guarunteed
        self.assertTrue(expected_1 in patch_output.getvalue())
        self.assertTrue(expected_2 in patch_output.getvalue())
        self.assertTrue(expected_3 in patch_output.getvalue())
        self.assertEqual(result, expected_result)

    def test_peoutput_error(self):
        '''
        Test that in the absence of a pe output file to total time measured
        is zero
        '''
        self.assertEqual(cpmip_um.get_um_io(self.pe0_empty_outputname),
                         0)


class TestComplexity(unittest.TestCase):
    '''
    Test the calculation of complexity
    '''
    def setUp(self):
        '''
        Create a UM fields file class to mimic mule output
        '''
        class UMFileFromFile:
            class FixedLengthHeader:
                def __init__(self):
                    self.raw = {153: 25*85} # prognostic fields
            class IntegerConstants:
                def __init__(self):
                    self.raw = {6: 96, # horizontal resolution
                                7: 72, # vertical resolution
                                8: 85} # pressure levels
            def __init__(self):
                self.integer_constants = self.IntegerConstants()
                self.fixed_length_header = self.FixedLengthHeader()
        self.umfile = UMFileFromFile()


    @mock.patch('cpmip_um._is_mule', return_value=True)
    @mock.patch('cpmip_um.os.path.isfile', return_value=False)
    def test_no_dump(self, mock_isfile, mock_ismule):
        '''
        Test no dump file, and pass through a value for total complexity
        '''
        expected_msg = 'Unable to calculate imodel complexity and imodel' \
                       ' resolution\n'
        expected_return = (expected_msg, 10)
        self.assertEqual(cpmip_um.get_complexity_um('imodel', 'gc3oa',
                                                    'DATAM', '20211901',
                                                    '', 10),
                         expected_return)

    @mock.patch('cpmip_um._is_mule', return_value=False)
    @mock.patch('cpmip_um.os.path.isfile', return_value=True)
    def test_no_mule(self, mock_isfile, mock_ismule):
        '''
        Test no mule avaliable, and pass through a value for message
        '''
        input_msg = 'Input message\n'
        expected_msg = '%sUnable to calculate imodel complexity and imodel' \
                       ' resolution\n' % input_msg
        expected_return = (expected_msg, 0)
        self.assertEqual(cpmip_um.get_complexity_um('imodel', 'gc3oa',
                                                    'DATAM', '20211901',
                                                    input_msg, 0),
                         expected_return)

    @mock.patch('cpmip_um._is_mule', return_value=True)
    @mock.patch('cpmip_um.os.path.isfile', return_value=True)
    @mock.patch('cpmip_um.mule.UMFile.from_file')
    def test_complexity(self, mock_umfile, mock_isfile, mock_ismule):
        '''
        Test the correct determination of UM complexity from mule call
        '''
        mock_umfile.return_value = self.umfile
        input_complexity = 10
        input_msg = 'Input message\n'
        expected_msg = '%sThe imodel complexity is 25, and total resolution' \
                       ' 587520\n' % input_msg
        expected_return = (expected_msg, 35)
        dump_path = 'DATAM/gc3oaa.da20211901_00'
        self.assertEqual(cpmip_um.get_complexity_um('imodel', 'gc3oa',
                                                    'DATAM', '20211901',
                                                    input_msg,
                                                    input_complexity),
                         expected_return)
        mock_umfile.assert_called_with(dump_path, remove_empty_lookups=True)
