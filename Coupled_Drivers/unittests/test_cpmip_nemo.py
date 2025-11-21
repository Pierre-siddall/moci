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
try:
    # mock is integrated into unittest as of Python 3.3
    import unittest.mock as mock
except ImportError:
    # mock is a standalone package (back-ported)
    import mock

import io
import os
import cpmip_nemo
import error

class TestUpdateInput(unittest.TestCase):
    '''
    Test the namelist update for the NEMO
    '''
    def setUp(self):
        '''
        Create an example namelist file to be updated
        '''
        self.nemo_nl = 'NEMO_NAMELST_FILE'
        nemo_nl_file = '&TEST_NL\n' \
                       'nn_step=1000,\n' \
                       'nn_timing=0,\n' \
                       'nn_xios=42,\n' \
                       '/\n'
        with open(self.nemo_nl, 'w') as nl_fh:
            nl_fh.write(nemo_nl_file)

    def tearDown(self):
        '''
        Remove namelist file to clear up at end of run
        '''
        try:
            os.remove(self.nemo_nl)
        except FileNotFoundError:
            pass

    def test_update_nemo_nl(self):
        '''
        Check that the nemo namelist updates correctly for timing
        '''
        cpmip_envar = {'NEMO_NL': self.nemo_nl}
        expected_file = '&TEST_NL\n' \
                        'nn_step=1000,\n' \
                        'nn_timing=3,\n' \
                        'nn_xios=42,\n' \
                        '/\n'
        cpmip_nemo.update_namelists_for_timing_nemo(cpmip_envar, 3)
        with open(self.nemo_nl, 'r') as nl_fh:
            constructed_file = nl_fh.read()
            self.assertEqual(constructed_file, expected_file)


class TestGetNemoInfo(unittest.TestCase):
    '''
    Test the retrieval of NEMO coupling timers
    '''
    def setUp(self):
        '''
        Create example timing output files
        '''
        self.empty_file = 'timing.output.empty'
        self.default_file = 'timing.output'
        self.cice_file = 'timing.output.cice'
        open(self.empty_file, 'w').close()

        example_no_cice = '''
 Total timing (sum) :
 --------------------
Elapsed Time (s)  CPU Time (s)
       208118.238   192910.140
 
Averaged timing on all processors :
-----------------------------------
Section             Elap. Time(s)  Elap. Time(%)  CPU Time(s)  CPU Time(%)  CPU/Elap Max elap(%)  Min elap(%)  Freq
sbc_cpl_rcv         22.715    6.81            23.50       7.31        1.00         11.03      6.49     144.00
sbc_cpl_init        5.068    1.46             4.64       1.44        0.91          1.46      1.46       1.00
sbc_cpl_snd         0.979  0.28             0.92       0.29        0.94          0.29      0.27     144.00
iom_rstput          0.799    0.23             0.62       0.19        0.78          0.36      0.05      21.00
sbc_cpl_ice_flx     0.49    0.14             0.16       0.05        0.33          0.16      0.12     144.00
 -------------|------------------|--------------|------------------
 Total        |  208118.238      |  192910.140  |    556.155
 -------------|------------------|--------------|------------------
        '''

        example_cice = '''
Averaged timing on all processors :
-----------------------------------
Section             Elap. Time(s)  Elap. Time(%)  CPU Time(s)  CPU Time(%)  CPU/Elap Max elap(%)  Min elap(%)  Freq
sbc_ice_cice        45.430    13.01           47.00       14.62       1.00         22.06     13.00     144.00
sbc_cpl_rcv         22.715    6.81            23.50       7.31        1.00         11.03      6.49     144.00
sbc_cpl_init        5.068    1.46             4.64       1.44        0.91          1.46      1.46       1.00
sbc_cpl_snd         0.979    0.28             0.92       0.29        0.94          0.29      0.27     144.00
iom_rstput          0.799    0.23             0.62       0.19        0.78          0.36      0.05      21.00
sbc_cpl_ice_flx     0.49    0.14             0.16       0.05        0.33          0.16      0.12     144.00
 -------------|------------------|--------------|------------------
 Total        |  208118.238      |  192910.140  |    556.155
 -------------|------------------|--------------|------------------
        '''
        files = [self.default_file, self.cice_file]
        contents = [example_no_cice, example_cice]
        for ifile, cont in zip(files, contents):
            with open(ifile, 'w') as f_handle:
                f_handle.write(cont)

    def tearDown(self):
        '''
        At the end of the test remove files if they still exist
        '''
        for f_to_del in [self.default_file, self.cice_file, self.empty_file]:
            try:
                os.remove(f_to_del)
            except FileNotFoundError:
                pass

    def test_get_nemo_info_empty_file(self):
        '''
        Test with an empty timing file
        '''
        expected_error = '[FAIL] Unable to determine Oasis timings from' \
                         ' the NEMO standard output\n'
        with mock.patch('sys.stderr', new=io.StringIO()) as patch_err:
            with self.assertRaises(SystemExit) as context:
                cpmip_nemo.get_nemo_info(self.empty_file)
        self.assertEqual(patch_err.getvalue(), expected_error)
        self.assertEqual(context.exception.code,
                         error.MISSING_CONTROLLER_FILE_ERROR)

    def test_get_nemo_info_nocice(self):
        '''
        Test retrieval on information with no CICE. This uses the default
        value for nemo_timing_output of timing.output
        '''
        expected_out = '[INFO] Unable to determine time in CICE for this' \
                       ' configuration'
        expected_rvalue = (190324.12865100004, 17794.109349000002,
                           582.7310664, False)
        with mock.patch('sys.stdout', new=io.StringIO()) as patch_out:
            rvalue = cpmip_nemo.get_nemo_info()
        self.assertEqual(patch_out.getvalue(), expected_out)
        self.assertEqual(rvalue, expected_rvalue)

    def test_get_nemo_info_cice(self):
        '''
        Test retrieval on information with CICE.
        '''
        expected_rvalue = (190324.12865100004, 17794.109349000002,
                           582.7310664, 27076.182763800003)
        rvalue = cpmip_nemo.get_nemo_info(self.cice_file)
        self.assertEqual(rvalue, expected_rvalue)


class TestGetNemoIO(unittest.TestCase):
    '''
    Test the retrival of the IO timing information
    '''
    def setUp(self):
        '''
        Create example timing output files
        '''
        self.empty_file = 'timing.output.empty'
        self.no_put_file = 'timing.output.no_put'
        self.no_get_file = 'timing.output.no_get'
        self.all_items_file = 'timing.output'
        open(self.empty_file, 'w').close()

        put_line = 'iom_rstput        45.430    13.01           47.00       14.62       1.00         22.06     13.00     144.00\n'
        get_line = 'iom_rstget        20.430    5.01           11.00       3.92       1.00         5.16     3.04     144.00\n'
        total_time = ''' -------------|------------------|--------------|------------------
 Total        |  208118.238      |  192910.140  |    556.155
 -------------|------------------|--------------|------------------\n
        '''
        with open(self.no_put_file, 'w') as noput_fh:
            noput_fh.write('%s%s' % (total_time, get_line))
        with open(self.no_get_file, 'w') as noget_fh:
            noget_fh.write('%s%s' % (total_time, put_line))
        with open(self.all_items_file, 'w') as allitems_fh:
            allitems_fh.write('%s%s%s' % (total_time, put_line, get_line))

    def tearDown(self):
        '''
        At the end of the test remove files if they still exist
        '''
        for f_to_del in [self.empty_file, self.no_put_file, self.no_get_file,
                         self.all_items_file]:
            try:
                os.remove(f_to_del)
            except FileNotFoundError:
                pass

    def test_get_nemo_io_empty(self):
        '''
        Test the empty file
        '''
        self.assertEqual(cpmip_nemo.get_nemo_io(self.empty_file), 0.0)

    def test_get_nemo_io_no_put(self):
        '''
        Test the value returned without a put
        '''
        self.assertEqual(cpmip_nemo.get_nemo_io(self.no_put_file),
                         10426.723723800002)

    def test_get_nemo_io_no_get(self):
        '''
        Test the value returned without a put
        '''
        self.assertEqual(cpmip_nemo.get_nemo_io(self.no_get_file),
                         27076.182763800003)

    def test_get_nemo_io_default_fn(self):
        '''
        Test both put and get, with the default filename timing.output
        '''
        self.assertEqual(cpmip_nemo.get_nemo_io(),
                         37502.906487600005)
