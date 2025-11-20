#!/usr/bin/env python
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2025 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
'''
import unittest
import os
import re
try:
    # mock is integrated into unittest as of Python 3.3
    import unittest.mock as mock
except ImportError:
    # mock is a standalone package (back-ported)
    import mock

import testing_functions as func
import runtime_environment

# Import of atmos requires RUNID from runtime_environment
runtime_environment.setup_env()
import unicicles

NAML = '''
&unicicles_pp
pp_run=true,
/
&suitegen
/
'''


class StencilTests(unittest.TestCase):
    '''Unit tests relating to the UniCiCles output filename stencils'''
    def setUp(self):
        self.files = [
            'TESTPa.da_19810101_00-pre_ice',
            'TESTPc_19810101_bisicles-AIS_restart.hdf5',
            'TESTPc_19810101_bisicles-GrIS_restart.hdf5',
            'TESTPc_19810101_glint-AIS_restart.nc',
            'TESTPc_19810101_glint-GrIS_restart.nc',
            'TESTPo_1m_19810101_19810201_isf_T.nc',
            'bisicles_TESTPc_1y_19800101-19810101_calving-AIS.hdf5',
            'bisicles_TESTPc_1y_19800101-19810101_calving-GrIS.hdf5',
            'bisicles_TESTPc_1y_19800101-19810101_nemo-icecouple-AIS.hdf5',
            'bisicles_TESTPc_1y_19800101-19810101_plot-AIS.hdf5',
            'bisicles_TESTPc_1y_19800101-19810101_plot-GrIS.hdf5',
            'unicicles_TESTPc_1y_19800101-19810101_atmos-icecouple.nc',
            'unicicles_TESTPc_1y_19800101-19810101_bisicles-icecouple.nc',
            'unicicles_TESTPc_1y_19800101-19810101_bisicles-icecouple-AIS.nc',
            'unicicles_TESTPc_1y_19800101-19810101_bisicles-icecouple-GrIS.nc',
            'unicicles_TESTPc_1y_19800101-19810101_calving.nc',
            'unicicles_TESTPc_1y_19800101-19810101_calv-AIS.nc',
            'unicicles_TESTPc_1y_19800101-19810101_calv-GrIS.nc',
            'unicicles_TESTPc_1y_19800101-19810101_nemo-bathy-isf.nc',
            'unicicles_TESTPc_1y_19800101-19810101_nemo-icecouple.nc',
            'unicicles_TESTPc_1y_19800101-19810101_orog-hi-AIS.anc',
            'unicicles_TESTPc_1y_19800101-19810101_orog-hi-GrIS.anc',
            'unicicles_TESTPc_1y_19800101-19810101_orog-lo-AIS.anc',
            'unicicles_TESTPc_1y_19800101-19810101_orog-lo-GrIS.anc',
            'unicicles_TESTPc_1y_19800101-19810101_orog-lo-AIS.anc.xml',
            'unicicles_TESTPc_1y_19800101-19810101_orog-lo-GrIS.anc.xml',
            'unicicles_TESTPc_1y_19800101-19810101_orog-lo.anc',
            ]
        self.diags = ['atmos-icecouple.nc', '_bisicles-icecouple.nc',
                      '_calving-', '_calving.nc', '_nemo-icecouple-AIS.hdf5',
                      'nemo-bathy-isf.nc', 'nemo-icecouple.nc',
                      '_plot-']

        with open('uniciclespp.nl', 'w') as fh:
            fh.write(NAML)
        self.unicicles = unicicles.UniciclesPostProc()

    def tearDown(self):
        for fname in runtime_environment.RUNTIME_FILES:
            try:
                os.remove(fname)
            except OSError:
                pass

    def test_archive_rst_template(self):
        '''Test the regular expressions for archiving restart files'''
        func.logtest('Assert template returns restart files to archive:')
        rst_files = [f for f in self.files if 'restart' in f]

        # All restart files should be archived and deleted
        for fname in rst_files:
            arch_file = False
            for pattern in self.unicicles.template_to_archive:
                if re.match(pattern, fname):
                    arch_file = True
                    break
            self.assertTrue(arch_file)

    def test_archive_diag_template(self):
        '''Test the regular expressions for archiving diagnostic files'''
        func.logtest('Assert template returns diag files to archive:')
        diag_files = [f for f in self.files if 'restart' not in f]

        # Files should be archived according to the patterns
        # returned by unicicles.template_to_archive
        for fname in diag_files:
            arch_file = False
            for pattern in self.unicicles.template_to_archive:
                if re.match(pattern, fname):
                    arch_file = True
                    break
            if any([p for p in self.diags if p in fname]):
                self.assertTrue(arch_file)
            else:
                self.assertFalse(arch_file)

    def test_delete_template(self):
        '''Test the regular expressions for deleting diagnostic files'''
        func.logtest('Assert template returns diagnostic files to delete:')
        diag_files = [f for f in self.files if 'restart' not in f]

        # Files should be deleted according to the patterns
        # returned by unicicles.template_to_delete
        for fname in diag_files:
            del_file = False
            for pattern in self.unicicles.template_to_delete:
                if re.match(pattern, fname):
                    del_file = True
                    break
            if any([p for p in self.diags if p in fname]):
                self.assertFalse(del_file)
            else:
                self.assertTrue(del_file)


class CyclepointTests(unittest.TestCase):
    '''Unit tests relating to the tests on UniCiCles cycle point'''
    def setUp(self):
        with open('uniciclespp.nl', 'w') as fh:
            fh.write(NAML)
        self.unicicles = unicicles.UniciclesPostProc()

    def tearDown(self):
        for fname in runtime_environment.RUNTIME_FILES:
            try:
                os.remove(fname)
            except OSError:
                pass

    def test_cyclepoint(self):
        ''' Test the creation of the UniCiCles cyclepoint '''
        func.logtest('Assert selection flag up to end of current cycle:')
        self.assertTrue(self.unicicles.current_cycle, unicicles.utils.CylcCycle)
        self.assertEqual(self.unicicles.current_cycle.endcycle['iso'],
                         self.unicicles.suite.cyclepoint.endcycle['iso'])
        self.assertEqual(self.unicicles.current_cycle.period, '1y')

    def test_select_file_thiscycle(self):
        '''Test select files dated during the current the cycle'''
        func.logtest('Assert selection flag during the current cycle:')
        # File ends before the initial cycle point: 1995-08-21 
        self.assertFalse(
            self.unicicles.select_file('model_19950101_filetype.nc',
                                       thiscycle=True)
        )
        # File ends at start of current cycle
        self.assertTrue(
            self.unicicles.select_file('model_19990221_filetype.nc',
                                       thiscycle=True)
        )
        # File ends during current cycle
        self.assertTrue(
            self.unicicles.select_file('model_20000101_filetype.nc',
                                       thiscycle=True)
        )
        # File ends at end of current cycle
        self.assertFalse(
            self.unicicles.select_file('model_19990221-20000221_filetype.nc',
                                       thiscycle=True)
        )

    def test_select_file_to_endcycle(self):
        '''Test select files up to & including the end of the cycle'''
        func.logtest('Assert selection flag up to end of current cycle:')
        # File ends at the initial cycle point: 1995-08-21 
        self.assertFalse(
            self.unicicles.select_file('model_19950821_filetype.nc')
        )
        # File ends at start of current cycle
        self.assertTrue(
            self.unicicles.select_file('model_19990221_filetype.nc')
        )       
        # File ends during current cycle
        self.assertTrue(
            self.unicicles.select_file('model_20000101_filetype.nc')
        )
        # File ends at end of current cycle
        self.assertTrue(
            self.unicicles.select_file('model_19990221-20000221_filetype.nc')
        )
        # File ends during next cycle
        self.assertFalse(
            self.unicicles.select_file('model_20000101-20010101_filetype.nc')
        )


class ArchiveDeleteTests(unittest.TestCase):
    '''Unit tests relating to the UniCiCles archive and delete methods'''
    def setUp(self):
        self.files = [
            'TESTPa.da_20000101_00-pre_ice',
            'TESTPc_20000101_bisicles-AIS_restart.hdf5',
            'TESTPc_20000101_bisicles-GrIS_restart.hdf5',
            'TESTPc_20000101_glint-AIS_restart.nc',
            'TESTPc_20000101_glint-GrIS_restart.nc',
            'TESTPo_1m_20000101_20000201_isf_T.nc',
            'bisicles_TESTPc_1y_19990101-20000101_calving-AIS.hdf5',
            'bisicles_TESTPc_1y_19990101-20000101_calving-GrIS.hdf5',
            'bisicles_TESTPc_1y_19990101-20000101_nemo-icecouple-AIS.hdf5',
            'bisicles_TESTPc_1y_19990101-20000101_plot-AIS.hdf5',
            'bisicles_TESTPc_1y_19990101-20000101_plot-GrIS.hdf5',
            'unicicles_TESTPc_1y_19990101-20000101_atmos-icecouple.nc',
            'unicicles_TESTPc_1y_19990101-20000101_bisicles-icecouple.nc',
            'unicicles_TESTPc_1y_19990101-20000101_bisicles-icecouple-AIS.nc',
            'unicicles_TESTPc_1y_19990101-20000101_bisicles-icecouple-GrIS.nc',
            'unicicles_TESTPc_1y_19990101-20000101_calving.nc',
            'unicicles_TESTPc_1y_19990101-20000101_calv-AIS.nc',
            'unicicles_TESTPc_1y_19990101-20000101_calv-GrIS.nc',
            'unicicles_TESTPc_1y_19990101-20000101_nemo-bathy-isf.nc',
            'unicicles_TESTPc_1y_19990101-20000101_nemo-icecouple.nc',
            'unicicles_TESTPc_1y_19990101-20000101_orog-hi-AIS.anc',
            'unicicles_TESTPc_1y_19990101-20000101_orog-hi-GrIS.anc',
            'unicicles_TESTPc_1y_19990101-20000101_orog-lo-AIS.anc',
            'unicicles_TESTPc_1y_19990101-20000101_orog-lo-GrIS.anc',
            'unicicles_TESTPc_1y_19990101-20000101_orog-lo-AIS.anc.xml',
            'unicicles_TESTPc_1y_19990101-20000101_orog-lo-GrIS.anc.xml',
            'unicicles_TESTPc_1y_19990101-20000101_orog-lo.anc',
            ]

        with open('uniciclespp.nl', 'w') as fh:
            fh.write(NAML)
        self.unicicles = unicicles.UniciclesPostProc()

    def tearDown(self):
        for fname in runtime_environment.RUNTIME_FILES:
            try:
                os.remove(fname)
            except OSError:
                pass

    @mock.patch('unicicles.utils')
    def test_do_archive(self, mock_utils):
        '''Test do_archive method'''
        func.logtest('Assert files to be archived.')

        mock_utils.get_subset.return_value = self.files
        mock_utils.add_path.return_value = self.files
        self.unicicles.suite.archive_file = mock.MagicMock(return_value=0)
        self.unicicles.suite.finalcycle = False

        with mock.patch('unicicles.UniciclesPostProc.do_delete') as mock_del:
            self.unicicles.do_archive()

            self.assertEqual(mock_utils.get_subset.call_count,
                             len(self.unicicles.template_to_archive))
            self.assertEqual(self.unicicles.suite.archive_file.call_count,
                             len(self.files))

            self.assertIn('Archive successful', mock_utils.log_msg.call_args[0][0])
            mock_del.assert_called_once_with(filelist=self.files)

    @mock.patch('unicicles.utils')
    def test_do_archive_finalcycle(self, mock_utils):
        '''Test do_archive method - finalcycle'''
        func.logtest('Assert files to be archived - final .')
        unicicles.timer = mock.Mock()
        mock_utils.get_subset.return_value = self.files
        mock_utils.add_path.return_value = self.files
        self.unicicles.suite.archive_file = mock.MagicMock(return_value=0)
        self.unicicles.suite.finalcycle = True

        with mock.patch('unicicles.UniciclesPostProc.do_delete') as mock_del:
            self.unicicles.do_archive()

            self.assertEqual(mock_utils.get_subset.call_count,
                             2*len(self.unicicles.template_to_archive))
            self.assertEqual(self.unicicles.suite.archive_file.call_count,
                             2*len(self.files))

            self.assertIn('Archive successful', mock_utils.log_msg.call_args[0][0])
            mock_del.assert_called_once_with(filelist=self.files)
            self.assertIn(mock.call('Running do_archive on final cycle...'),
                          mock_utils.log_msg.mock_calls)

    @mock.patch('unicicles.utils')
    def test_do_archive_fail(self, mock_utils):
        '''Test do_archive method - failure mode'''
        func.logtest('Assert files to be archived - failure mode.')

        mock_utils.get_subset.return_value = self.files
        mock_utils.add_path.return_value = self.files
        self.unicicles.suite.archive_file = mock.MagicMock(return_value=-1)
        self.unicicles.suite.finalcycle = False

        with mock.patch('unicicles.UniciclesPostProc.do_delete') as mock_del:
            self.unicicles.do_archive()

            self.assertEqual(mock_utils.get_subset.call_count,
                             len(self.unicicles.template_to_archive))
            self.assertEqual(self.unicicles.suite.archive_file.call_count,
                             len(self.files))

            self.assertIn('Failed to archive', mock_utils.log_msg.call_args[0][0])
            mock_del.assert_not_called()


    @mock.patch('unicicles.utils')
    def test_do_delete(self, mock_utils):
        '''Test do_delete method for intermediate files'''
        func.logtest('Assert intermediate files to be deleted.')

        mock_utils.get_subset.return_value = self.files
        mock_utils.get_debugmode.return_value = False

        self.unicicles.do_delete()

        self.assertEqual(mock_utils.get_subset.call_count,
                         len(self.unicicles.template_to_delete))
        self.assertEqual(mock_utils.remove_files.call_count, 1)
        self.assertListEqual(sorted(mock_utils.remove_files.call_args[0][0]),
                              sorted(self.files))
        self.assertIn('Deleting intermediate file(s):',
                      mock_utils.log_msg.call_args[0][0])

    @mock.patch('unicicles.utils')
    def test_do_delete_debugmode(self, mock_utils):
        '''Test do_delete method for intermediate files'''
        func.logtest('Assert intermediate files to be deleted.')

        mock_utils.get_subset.return_value = self.files

        self.unicicles.do_delete()

        self.assertEqual(mock_utils.get_subset.call_count,
                         len(self.unicicles.template_to_delete))
        self.assertIn('Would delete intermediate file(s)',
                      mock_utils.log_msg.call_args[0][0])

    @mock.patch('unicicles.utils')
    def test_do_delete_filelist(self, mock_utils):
        '''Test do_delete method for archived files'''
        func.logtest('Assert archived files to be deleted.')

        mock_utils.get_debugmode.return_value = False

        self.unicicles.do_delete(self.files)

        self.assertEqual(mock_utils.remove_files.call_count, 1)
        self.assertListEqual(sorted(mock_utils.remove_files.call_args[0][0]),
                              sorted(self.files))
        self.assertIn('Deleting archived file(s):',
                      mock_utils.log_msg.call_args[0][0])

    def test_do_delete_filelist_debugmode(self):
        '''Test do_delete method for archived files'''
        func.logtest('Assert archived files to be deleted.')

        with mock.patch('unicicles.utils.get_debugmode', return_value=True):
            with mock.patch('unicicles.os.rename') as mock_rename:
                self.unicicles.do_delete(self.files)

        self.assertEqual(mock_rename.call_count,
                         len(self.files))
        self.assertIn('[DEBUG]  Selecting files for deletion...',
                      func.capture('err'))
        self.assertIn('Would delete archived file(s)',
                      func.capture('err'))
