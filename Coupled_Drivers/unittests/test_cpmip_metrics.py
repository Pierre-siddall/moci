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
try:
    # mock is integrated into unittest as of Python 3.3
    import unittest.mock as mock
except ImportError:
    # mock is a standalone package (back-ported)
    import mock

import io
import os
import cpmip_metrics

class TestGlobals(unittest.TestCase):
    '''
    Test global variables
    '''
    def test_global_timeout(self):
        '''
        Test the variable for file system operational timeout
        '''
        self.assertEqual(cpmip_metrics.FS_OPERATION_TIMEOUT, 60)

class TestDataIntensity(unittest.TestCase):
    '''
    Test the functions for the generation of data intensity metrics
    '''
    def remove_datam_size(self):
        '''
        Remove the datam.size file
        '''
        try:
            os.remove('datam.size')
        except FileNotFoundError:
            pass

    def create_datam_1000(self):
        '''
        Create a datam file containing 1000
        '''
        with open('datam.size', 'w') as dm_fh:
            dm_fh.write('1000')

    def tearDown(self):
        '''
        Tidy up any tempoarary files used for the test
        '''
        self.remove_datam_size()

    @mock.patch('cpmip_metrics.cpmip_utils.get_datam_output_runonly')
    def test_data_intensity_initial(self, mock_get_datam):
        '''
        Test the creation of a file containing the initial datam size
        '''
        mock_get_datam.return_value = 1000
        cpmip_metrics.data_intensity_initial('common', 'cpmip')
        mock_get_datam.assert_called_with('common', 'cpmip',
                                          cpmip_metrics.FS_OPERATION_TIMEOUT)
        with open('datam.size', 'r') as f_size:
            file_contents = f_size.read()
        self.assertEqual(file_contents, '1000')
        self.remove_datam_size()

    def test_data_intensity_final_null_behaviour(self):
        '''
        Test that when no models are found we get output of zero
        '''
        common_envar = {'models': []}
        self.assertEqual(cpmip_metrics.data_intensity_final(10, common_envar,
                                                            None),
                         (0, 0))

    @mock.patch('cpmip_metrics.cpmip_utils.get_datam_output_runonly')
    def test_data_intensity_final_timeout_um(self, mock_get_datam):
        '''
        Test the um timeout behaviour
        '''
        self.create_datam_1000()
        cpmip_envar = {}
        common_envar = {'models': ['um']}
        mock_get_datam.return_value = 0
        expected_err = '[WARN] The du operation to determine the data volume' \
                       ' has timed out. This metric will be ignored\n'
        with mock.patch('sys.stderr', new=io.StringIO()) as patch_err:
            rvalue = cpmip_metrics.data_intensity_final(0, common_envar,
                                                        cpmip_envar)
        self.assertEqual(patch_err.getvalue(), expected_err)
        self.assertEqual(rvalue, (-1, -1))
        self.remove_datam_size()

    @mock.patch('cpmip_metrics.cpmip_utils.get_workdir_netcdf_output')
    def test_data_intensity_final_timeout_nemo(self, mock_get_workdir):
        '''
        Test the nemo timeout behaviour
        '''
        cpmip_envar = {}
        common_envar = {'models': ['nemo']}
        mock_get_workdir.return_value = -1
        expected_err = '[WARN] The du operation to determine the data volume' \
                       ' has timed out. This metric will be ignored\n'
        with mock.patch('sys.stderr', new=io.StringIO()) as patch_err:
            rvalue = cpmip_metrics.data_intensity_final(0, common_envar,
                                                        cpmip_envar)
        self.assertEqual(patch_err.getvalue(), expected_err)
        self.assertEqual(rvalue, (-1, -1))

    @mock.patch('cpmip_metrics.cpmip_utils.get_datam_output_runonly')
    def test_data_intensity_final_um(self, mock_get_datam):
        '''
        Test the um retrival of data
        '''
        self.create_datam_1000()
        common_envar = {'models': ['um']}
        mock_get_datam.return_value = 10000
        rvalue = cpmip_metrics.data_intensity_final(10, common_envar, 'cpmip')
        mock_get_datam.assert_called_with(common_envar, 'cpmip',
                                          cpmip_metrics.FS_OPERATION_TIMEOUT)
        self.assertEqual(rvalue, (0.00858306884765625,
                                  0.000858306884765625))
        self.remove_datam_size()

    @mock.patch('cpmip_metrics.cpmip_utils.get_workdir_netcdf_output')
    def test_data_intensity_final_nemo(self, mock_get_workdir):
        '''
        Test the nemo retrival of data
        '''
        common_envar = {'models': ['nemo']}
        mock_get_workdir.return_value = 9000
        rvalue = cpmip_metrics.data_intensity_final(10, common_envar, None)
        self.assertEqual(rvalue, (0.00858306884765625,
                                  0.000858306884765625))

    @mock.patch('cpmip_metrics.cpmip_utils.get_datam_output_runonly')
    @mock.patch('cpmip_metrics.cpmip_utils.get_workdir_netcdf_output')
    def test_data_intensity_final_both(self, mock_get_workdir, mock_get_datam):
        '''
        Test the infromation retrieval for both models
        '''
        self.create_datam_1000()
        common_envar = {'models': ['um', 'nemo']}
        mock_get_datam.return_value = 5500
        mock_get_workdir.return_value = 4500
        rvalue = cpmip_metrics.data_intensity_final(10, common_envar, None)
        self.assertEqual(rvalue, (0.00858306884765625,
                                  0.000858306884765625))
        self.remove_datam_size()


class TestJPSYMetric(unittest.TestCase):
    '''
    Test the JPSY metric
    '''
    def test_no_total_power(self):
        '''
        Test the error essage if total power not provided
        '''
        expected_output = '[INFO] Unable to determine the JPSY metric\n'
        with mock.patch('sys.stdout', new=io.StringIO()) as patch_output:
            self.assertEqual(cpmip_metrics.jpsy_metric('', '5000', '64',
                                                       3600, 4.2), '')
        self.assertEqual(patch_output.getvalue(), expected_output)

    def test_no_total_nodes(self):
        '''
        Test error message if total_hpc_nodes not provided
        '''
        expected_output = '[INFO] Unable to determine the JPSY metric\n'
        with mock.patch('sys.stdout', new=io.StringIO()) as patch_output:
            self.assertEqual(cpmip_metrics.jpsy_metric('4.8', '', '64',
                                                       3600, 4.2), '')
        self.assertEqual(patch_output.getvalue(), expected_output)

    def test_jpsy_metric(self):
        '''
        Test the calculation of the metric
        '''
        expected_rvalue = 'Energy cost for run 2.56E+08 Joules per simulated' \
                          ' year\n'
        self.assertEqual(cpmip_metrics.jpsy_metric('4.8', '12932', '64',
                                                   3600, 0.334),
                         expected_rvalue)


class TestCHSYMetric(unittest.TestCase):
    '''
    Test the CHSY metric
    '''
    def test_chsy(self):
        '''
        Test core hours per simulated years returns the correct message
        '''
        expected_rvalue = 'This run uses 90.00 percent of the allocated CPUS' \
                          ' (90/100)\n' \
                          'Corehours per simulated year (CHSY): 400.00\n'
        self.assertEqual(cpmip_metrics.chsy_metric(100, 90, 0.25, 1),
                         expected_rvalue)


class TestComplexityMetric(unittest.TestCase):
    '''
    Test the determination of the complexity metric
    '''
    @mock.patch('cpmip_metrics.cpmip_utils.increment_dump')
    def test_complexity_metric_null(self, mock_inc_dump):
        '''
        Test with no models the function doesn't crash, and the call to
        cpmip_utils.increment_dump is correct
        '''
        cpmip_envar = {'CYLC_TASK_CYCLE_POINT': '20210201T0000Z',
                       'RESUB': 'M',
                       'CYCLE': 1}
        common_envar = {'models': []}
        mock_inc_dump.return_value = '20210301'
        expected_msg = 'Total model complexity is 0\n'
        self.assertEqual(cpmip_metrics.complexity_metric(common_envar,
                                                         cpmip_envar),
                         expected_msg)
        mock_inc_dump.assert_called_with(
            cpmip_envar['CYLC_TASK_CYCLE_POINT'].split('T')[0],
            cpmip_envar['RESUB'],
            cpmip_envar['CYCLE'])

    @mock.patch('cpmip_metrics.cpmip_utils.increment_dump')
    @mock.patch('cpmip_metrics.cpmip_um.get_complexity_um')
    def test_complexity_metric_um(self, mock_complex_um, mock_inc_dump):
        '''
        Test UM model
        '''
        cpmip_envar = {'CYLC_TASK_CYCLE_POINT': '20210201T0000Z',
                       'RESUB': 'M',
                       'CYCLE': 1,
                       'DATAM' : 'datam'}
        common_envar = {'models': ['um'],
                        'RUNID': 'gc3ao'}
        mock_inc_dump.return_value = '20210301'
        mock_complex_um.return_value = ('UM Msg\n', 1)
        expected_msg = 'UM Msg\n' \
                       'Total model complexity is 1\n'
        self.assertEqual(cpmip_metrics.complexity_metric(common_envar,
                                                         cpmip_envar),
                         expected_msg)
        mock_complex_um.assert_called_once_with('UM',
                                                common_envar['RUNID'],
                                                cpmip_envar['DATAM'],
                                                '20210301',
                                                '', 0)

    @mock.patch('cpmip_metrics.cpmip_utils.increment_dump')
    @mock.patch('cpmip_metrics.cpmip_um.get_complexity_um')
    def test_complexity_metric_junior(self, mock_complex_um, mock_inc_dump):
        '''
        Test Junior model
        '''
        cpmip_envar = {'CYLC_TASK_CYCLE_POINT': '20210201T0000Z',
                       'RESUB': 'M',
                       'CYCLE': 1,
                       'DATAM' : 'datam',
                       'RUNID_JNR': 'gc3ao_jnr'}
        common_envar = {'models': ['jnr']}
        mock_inc_dump.return_value = '20210301'
        mock_complex_um.return_value = ('Jnr Msg\n', 10)
        expected_msg = 'Jnr Msg\n' \
                       'Total model complexity is 10\n'
        self.assertEqual(cpmip_metrics.complexity_metric(common_envar,
                                                         cpmip_envar),
                         expected_msg)
        mock_complex_um.assert_called_once_with('Jnr',
                                                cpmip_envar['RUNID_JNR'],
                                                cpmip_envar['DATAM'],
                                                '20210301',
                                                '', 0)

    @mock.patch('cpmip_metrics.cpmip_utils.increment_dump')
    @mock.patch('cpmip_metrics.cpmip_utils.get_component_resolution')
    @mock.patch('cpmip_metrics.cpmip_utils.get_glob_usage')
    def test_complexity_metric_nemo_sizek_lt_zero(self, mock_glob,
                                                  mock_comp_res, mock_inc_dump):
        '''
        Test NEMO with size k less than zero, and check the calls to
        get_component_resolution and get_glob_usage
        '''
        mock_inc_dump.return_value = '20210301'
        mock_comp_res.return_value = 1000
        mock_glob.return_value = -4.3
        cpmip_envar = {'CYLC_TASK_CYCLE_POINT': '20210201T0000Z',
                       'RESUB': 'M',
                       'CYCLE': 1,
                       'NEMO_NL': 'namelist_ref',
                       'DATAM': 'datam'}
        common_envar = {'models': ['nemo']}
        expected_msg = 'Total model complexity is 0\n'
        self.assertEqual(cpmip_metrics.complexity_metric(common_envar,
                                                         cpmip_envar),
                         expected_msg)
        mock_comp_res.assert_called_with(cpmip_envar['NEMO_NL'],
                                         ('jpiglo', 'jpjglo', 'jpkdta'))
        mock_glob.assert_called_with('%s/NEMOhist/*%s*' %
                                     (cpmip_envar['DATAM'], '20210301'))


    @mock.patch('cpmip_metrics.cpmip_utils.increment_dump')
    @mock.patch('cpmip_metrics.cpmip_utils.get_component_resolution')
    @mock.patch('cpmip_metrics.cpmip_utils.get_glob_usage')
    def test_complexity_metric_nemo(self, mock_glob, mock_comp_res,
                                    mock_inc_dump):
        '''
        Test NEMO with size k greater tham zerp
        '''
        mock_inc_dump.return_value = '20210301'
        mock_comp_res.return_value = 1000
        mock_glob.return_value = 10000
        cpmip_envar = {'CYLC_TASK_CYCLE_POINT': '20210201T0000Z',
                       'RESUB': 'M',
                       'CYCLE': 1,
                       'NEMO_NL': 'namelist_ref',
                       'DATAM': 'datam'}
        common_envar = {'models': ['nemo']}
        expected_msg = 'NEMO complexity is 1280, and total resolution 1000\n' \
                       'Total model complexity is 1280\n'
        self.assertEqual(cpmip_metrics.complexity_metric(common_envar,
                                                         cpmip_envar),
                         expected_msg)

    @mock.patch('cpmip_metrics.cpmip_utils.increment_dump')
    @mock.patch('cpmip_metrics.cpmip_utils.get_glob_usage')
    def test_complexity_metric_cice_sizek_lt_zero(self, mock_glob,
                                                  mock_inc_dump):
        '''
        Test CICE with size k less than zero, and check the calls to
        get_component_resolution and get_glob_usage
        '''
        mock_inc_dump.return_value = '20210301'
        mock_glob.return_value = -4.3
        cpmip_envar = {'CYLC_TASK_CYCLE_POINT': '20210201T0000Z',
                       'RESUB': 'M',
                       'CYCLE': 1,
                       'DATAM': 'datam',
                       'CICE_COL': 10,
                       'CICE_ROW': 20}
        common_envar = {'models': ['cice']}
        expected_msg = 'Total model complexity is 0\n'
        self.assertEqual(cpmip_metrics.complexity_metric(common_envar,
                                                         cpmip_envar),
                         expected_msg)
        mock_glob.assert_called_with('%s/CICEhist/*%s*' %
                                     (cpmip_envar['DATAM'], '2021-03-01'))

    @mock.patch('cpmip_metrics.cpmip_utils.increment_dump')
    @mock.patch('cpmip_metrics.cpmip_utils.get_glob_usage')
    def test_complexity_metric_cice(self, mock_glob, mock_inc_dump):
        '''
        Test CICE with size k more than zero
        '''
        mock_inc_dump.return_value = '20210301'
        mock_glob.return_value = 500
        cpmip_envar = {'CYLC_TASK_CYCLE_POINT': '20210201T0000Z',
                       'RESUB': 'M',
                       'CYCLE': 1,
                       'DATAM': 'datam',
                       'CICE_COL': 10,
                       'CICE_ROW': 20}
        common_envar = {'models': ['cice']}
        expected_msg = 'CICE complexity is 320, and total resolution 200\n' \
                       'Total model complexity is 320\n'
        self.assertEqual(cpmip_metrics.complexity_metric(common_envar,
                                                         cpmip_envar),
                         expected_msg)

    @mock.patch('cpmip_metrics.cpmip_utils.increment_dump')
    @mock.patch('cpmip_metrics.cpmip_um.get_complexity_um')
    @mock.patch('cpmip_metrics.cpmip_utils.get_component_resolution')
    @mock.patch('cpmip_metrics.cpmip_utils.get_glob_usage')
    def test_complexity_metric_all(self, mock_glob, mock_comp_res,
                                   mock_complex_um, mock_inc_dump):
        '''
        Test All models
        '''
        cpmip_envar = {'CYLC_TASK_CYCLE_POINT': '20210201T0000Z',
                       'RESUB': 'M',
                       'CYCLE': 1,
                       'DATAM' : 'datam',
                       'RUNID_JNR': 'gc3ao_jnr',
                       'NEMO_NL': 'namelist_ref',
                       'CICE_COL': 10,
                       'CICE_ROW': 20}
        common_envar = {'models': ['um', 'jnr', 'nemo', 'cice'],
                        'RUNID': 'gc3ao'}
        mock_inc_dump.return_value = '20210301'
        mock_complex_um.side_effect = [('UM msg\n', 200),
                                       ('UM msg\nJnr msg\n', 400)]
        mock_comp_res.return_value = 1000
        mock_glob.side_effect = [10000, 500]
        expected_msg = 'UM msg\n' \
                       'Jnr msg\n' \
                       'NEMO complexity is 1280, and total resolution 1000\n' \
                       'CICE complexity is 320, and total resolution 200\n' \
                       'Total model complexity is 2000\n'
        self.assertEqual(cpmip_metrics.complexity_metric(common_envar,
                                                         cpmip_envar),
                         expected_msg)
        complex_um_calls = [mock.call('UM', common_envar['RUNID'],
                                      cpmip_envar['DATAM'], '20210301',
                                      '', 0),
                            mock.call('Jnr', cpmip_envar['RUNID_JNR'],
                                      cpmip_envar['DATAM'], '20210301',
                                      'UM msg\n', 200)]
        mock_complex_um.assert_has_calls(complex_um_calls)
