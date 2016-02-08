#!/usr/bin/env python2.7
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2015 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
'''
import unittest
import mock
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(
                                os.path.dirname(__file__)))+'/nemocice')
sys.path.append(os.path.dirname(os.path.abspath(
                                os.path.dirname(__file__)))+'/common')

import runtimeEnvironment
import nemo
import nemoNamelist
import testing_functions as func


class rebuildTests(unittest.TestCase):
    def setUp(self):
        self.nemo = nemo.NemoPostProc()
        self.nemo.suite = mock.Mock()
        self.nemo.suite.finalcycle = False
        self.defaults = nemoNamelist.nemoNamelist()
        self.bufferRst = self.nemo.buffer_rebuild('rst')
        self.bufferMean = self.nemo.buffer_rebuild('mean')

    def tearDown(self):
        for fn in ('nemocicepp.nl', 'nam_rebuild'):
            try:
                os.remove(fn)
            except OSError:
                print "***EFN** file didn't exist:", fn

    def testNamlistProperties(self):
        '''Test definition of NEMO namelist properties'''
        func.logtest('Assert NEMO namelist properties:')
        self.assertEqual(self.defaults.exec_rebuild, self.nemo.rebuild_cmd)
        self.assertEqual(self.defaults.means_cmd, self.nemo.means_cmd)

    def testBufferRebuild(self):
        '''Test rebuild buffer value extraction'''
        func.logtest('Assert given value for rebuild buffer:')
        self.assertEqual(self.defaults.buffer_rebuild_rst, self.bufferRst)
        self.assertEqual(self.defaults.buffer_rebuild_mean, self.bufferMean)

    @mock.patch('utils.get_subset')
    def testRebuildRestartNotRequired(self, mock_subset):
        '''Test rebuild restarts function retaining all files'''
        func.logtest('Assert restart files fewer than buffer are retained:')
        mock_subset.return_value = ['file1']
        self.nemo.rebuild_fileset(os.environ['PWD'], 'restart')
        self.assertIn('{} retained'.format(self.bufferRst), func.capture())

    @mock.patch('utils.get_subset')
    def testRebuildMeanNotRequired(self, mock_subset):
        '''Test rebuild means function retaining all files'''
        func.logtest('Assert means files fewer than buffer (1) are retained:')
        mock_subset.return_value = ['file1']
        self.nemo.rebuild_fileset(os.environ['PWD'], 'field')
        self.assertIn('{} retained'.format(self.bufferMean), func.capture())

    @mock.patch('utils.get_subset')
    def testRebuildPeriodicOnly(self, mock_subset):
        '''Test rebuild function for periodic files not found'''
        func.logtest('Assert only periodic files are rebuilt:')
        mock_subset.return_value = ['file1', 'file2']
        self.nemo.rebuild_fileset(os.environ['PWD'], 'field')
        self.assertIn('only rebuilding periodic', func.capture().lower())
        self.assertIn('deleting component files', func.capture().lower())

    @mock.patch('nemo.NemoPostProc.rebuild_namelist')
    @mock.patch('utils.get_subset')
    def testRebuildAll(self, mock_subset, mock_nl):
        '''Test rebuild all function'''
        func.logtest('Assert rebuild all function:')
        mock_subset.return_value = ['file_19980530_yyyymmdd_0000.nc',
                                    'file_19980630_yyyymmdd_0000.nc',
                                    'file_19980730_yyyymmdd_0000.nc'
                                    ]
        self.nemo.rebuild_fileset(os.environ['PWD'], 'field', rebuildall=True)
        mock_nl.assert_called_with(os.environ['PWD'], 'file_19980630_yyyymmdd',
                                   1, omp=1)

    @mock.patch('nemo.NemoPostProc.rebuild_namelist')
    def testRebuildPattern(self, mock_nl):
        '''Test rebuild pattern matching function'''
        func.logtest('Assert rebuild pattern natching function:')
        myfiles = ['file_19980530_yyyymmdd_field_0000.nc',
                   'file_19980530_yyyymmdd_field_0001.nc',
                   'file_19980530_yyyymmdd_field_0002.nc',
                   'file_19980530_yyyymmdd_field.nc',
                   'file_19981130_yyyymmdd_field_0000.nc',
                   ]
        for fn in myfiles:
            open(fn, 'w').close()
        self.nemo.rebuild_fileset(os.environ['PWD'], 'field')
        mock_nl.assert_called_with(os.environ['PWD'],
                                   'file_19980530_yyyymmdd_field',
                                   3, omp=1)
        for fn in myfiles:
            os.remove(fn)

    @mock.patch('nemo.NemoPostProc.rebuild_namelist')
    @mock.patch('utils.get_subset')
    def testRebuildFinalCycle(self, mock_subset, mock_nl):
        '''Test final cycle behaviour'''
        func.logtest('Assert component files not deleted on final cycle:')
        mock_subset.return_value = ['file_19980530_yyyymmdd_0000.nc',
                                    'file_19980630_yyyymmdd_0000.nc']
        mock_nl.return_value = 0
        self.nemo.suite.finalcycle = True
        self.nemo.rebuild_fileset(os.environ['PWD'], 'field', rebuildall=True)
        mock_nl.assert_called_with(os.environ['PWD'], 'file_19980530_yyyymmdd',
                                   1, omp=1)
        self.assertNotIn('deleting component files', func.capture().lower())

    @mock.patch('utils.exec_subproc')
    @mock.patch('os.path.isfile')
    @mock.patch('os.remove')
    def testRebuildNamelist(self, mock_remove, mock_isfile, mock_exec):
        '''Test rebuild namelist function'''
        func.logtest('Assert behaviour of rebuild_namelist function:')
        mock_exec.return_value = (0, '')
        mock_isfile.return_value = True
        rtn = self.nemo.rebuild_namelist(os.environ['PWD'],
                                         'file_19980530_yyyymmdd',
                                         3)
        self.assertEqual(mock_exec.return_value[0], rtn)
        self.assertEqual(int(os.environ['OMP_NUM_THREADS']), 16)
        self.assertIn('successfully rebuilt', func.capture().lower())
        self.assertIn('file_19980530_yyyymmdd', func.capture().lower())
        mock_exec.assert_called_with(
            'cd {}; {}'.format(os.environ['PWD'],
                               self.defaults.exec_rebuild))
        self.assertTrue(os.path.exists('nam_rebuild'))
        txt = open('nam_rebuild', 'r').read()
        self.assertNotIn('dims=\'1\',\'2\'', txt)

    @mock.patch('utils.exec_subproc')
    @mock.patch('os.path.isfile')
    @mock.patch('os.remove')
    def testRebuildNamelistOptions(self, mock_remove, mock_isfile, mock_exec):
        '''Test rebuild namelist function with options'''
        func.logtest('Assert rebuild_namelist function with options:')
        mock_exec.return_value = (0, '')
        mock_isfile.return_value = True
        rtn = self.nemo.rebuild_namelist(os.environ['PWD'],
                                         'file_19980530_yyyymmdd',
                                         3,
                                         omp=1, chunk='opt_chunk', dims=[1, 2])
        self.assertEqual(int(os.environ['OMP_NUM_THREADS']), 1)
        txt = open('nam_rebuild', 'r').read()
        self.assertIn('dims=\'1\',\'2\'', txt)
        self.assertIn('nchunksize=opt_chunk', txt)

    @mock.patch('utils.exec_subproc')
    @mock.patch('os.path.isfile')
    def testRebuildNamelistNoNamelist(self, mock_isfile, mock_exec):
        '''Test failure to create namelist file'''
        func.logtest('Assert failure to create namelist file:')
        mock_exec.return_value = (0, '')
        mock_isfile.return_value = False
        rtn = self.nemo.rebuild_namelist(os.environ['PWD'],
                                         'file_19980530_yyyymmdd',
                                         3)
        self.assertIn('failed to create namelist file',
                      func.capture('err').lower())

    @mock.patch('utils.exec_subproc')
    def testRebuildNamelistFail(self, mock_exec):
        '''Test failure mode of rebuild namelist function'''
        func.logtest('Assert failure behaviour of rebuild_namelist function:')
        mock_exec.return_value = (0, '')
        with self.assertRaises(SystemExit):
            self.nemo.rebuild_namelist(os.environ['PWD'],
                                       'file_19980530_yyyymmdd',
                                       3)
        self.assertIn('failed to rebuild file', func.capture('err').lower())
        self.assertIn('file_19980530_yyyymmdd', func.capture('err').lower())


def main():
    unittest.main(buffer=True)


if __name__ == '__main__':
    main()
