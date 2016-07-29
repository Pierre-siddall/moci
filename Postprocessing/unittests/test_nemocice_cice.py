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
import os
import sys
import re
import mock

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, 'cicecice'))

import runtime_environment
runtime_environment.setup_env()
import testing_functions as func

import cice


class StencilTests(unittest.TestCase):
    '''Unit tests relating to the CICE output filename stencils'''
    def setUp(self):
        self.files = [
            'RUNIDi.restart.1981-12-01-00000',
            'RUNIDi.restart.1981-12-01-00000.nc',
            'RUNIDi.6h.1985-11-11-13.nc',
            'RUNIDi.5d.1985-11-06.nc',
            'RUNIDi.10d.1985-11-11.nc',
            'RUNIDi.1m.1985-11.nc',
            'RUNIDi.1s.1985-09_1985-11.nc',
            'RUNIDi.1y.1983-12_1984-11.nc',
            'RUNIDi.1y.1984-12_1985-11.nc'
            ]
        self.cice = cice.CicePostProc()
        self.cice.suite = mock.Mock()
        self.cice.suite.prefix = 'RUNID'
        self.date = ('1985', '09')
        self.ssn = ('09', '10', '11', 0)
        self.setstencil = self.cice.set_stencil
        self.endstencil = self.cice.end_stencil
        self.meanstencil = self.cice.mean_stencil

    def tearDown(self):
        for fname in runtime_environment.runtime_files:
            try:
                os.remove(fname)
            except OSError:
                pass

    def test_set_stencil_restarts(self):
        '''Test the regular expressions of the set_stencil method - restarts'''
        func.logtest('Assert restart pattern matching of set_stencil:')
        patt = re.compile(self.setstencil['Restarts']('', None, None, ''))
        cice_rst = [fname for fname in self.files if patt.search(fname)]
        self.assertEqual(cice_rst,
                         [fname for fname in self.files if 'restart' in fname])

    def test_set_stencil_monthly(self):
        '''Test the regex of the set_stencil method - monthly'''
        func.logtest('Assert monthly pattern matching of set_stencil:')
        args = (self.date[0], self.date[1], None, '')
        patt = re.compile(self.setstencil['Monthly'](*args))
        month_set = [fname for fname in self.files if patt.search(fname)]
        self.assertEqual(month_set,
                         [fname for fname in self.files if '10d_' in fname])

    def test_set_stencil_seasonal(self):
        '''Test the regex of the set_stencil method - seasonal'''
        func.logtest('Assert seasonal pattern matching of set_stencil:')
        args = (self.date[0], None, self.ssn, '')
        patt = re.compile(self.setstencil['Seasonal'](*args))
        season_set = [fname for fname in self.files if patt.search(fname)]
        self.assertEqual(season_set,
                         [fname for fname in self.files if '.1m.' in fname])

    def test_set_stencil_annual(self):
        '''Test the regex of the set_stencil method - annual'''
        func.logtest('Assert annual pattern matching of set_stencil:')
        args = (self.date[0], None, None, '')
        patt = re.compile(self.setstencil['Annual'](*args))
        annual_set = [fname for fname in self.files if patt.search(fname)]
        self.assertEqual(annual_set,
                         [fname for fname in self.files if '.1s.' in fname])

    def test_end_stencil_restarts(self):
        '''Test the regular expressions of the set_stencil method - restarts'''
        func.logtest('Assert restart pattern matching of end_stencil:')
        self.assertEqual(self.endstencil['Restarts'], None)

    def test_end_stencil_monthly(self):
        '''Test the regex of the end_stencil method - monthly'''
        func.logtest('Assert monthly pattern matching of end_stencil:')
        args = (None, '')
        patt = re.compile(self.endstencil['Monthly'](*args))
        annual_set = [fname for fname in self.files if patt.search(fname)]
        self.assertEqual(annual_set,
                         [fname for fname in self.files if
                          '10d_' in fname and '30.nc' in fname])

    def test_end_stencil_seasonal(self):
        '''Test the regex of the end_stencil method - seasonal'''
        func.logtest('Assert seasonal pattern matching of end_stencil:')
        args = (self.ssn, '')
        patt = re.compile(self.endstencil['Seasonal'](*args))
        annual_set = [fname for fname in self.files if patt.search(fname)]
        self.assertEqual(annual_set,
                         [fname for fname in self.files if '.1m.' in fname])

    def test_end_stencil_annual(self):
        '''Test the regex of the end_stencil method - annual'''
        func.logtest('Assert annual pattern matching of end_stencil:')
        args = (None, '')
        patt = re.compile(self.endstencil['Annual'](*args))
        annual_set = [fname for fname in self.files if patt.search(fname)]
        self.assertEqual(annual_set,
                         [fname for fname in self.files if '.1s.' in fname])

    def test_mean_stencil_hourly(self):
        '''Test the regular expressions of the mean_stencil method - hourly'''
        func.logtest('Assert hourly pattern matching of mean_stencil:')
        patt = re.compile(self.meanstencil['General']('6h', None, None, ''))
        sixhr_set = [fname for fname in self.files if patt.search(fname)]
        self.assertEqual(sixhr_set,
                         [fname for fname in self.files if '.6h.' in fname])

    def test_mean_stencil_daily(self):
        '''Test the regular expressions of the mean_stencil method - daily'''
        func.logtest('Assert daily pattern matching of mean_stencil:')
        patt = re.compile(self.meanstencil['General']('10d', None, None, ''))
        tenday_set = [fname for fname in self.files if patt.search(fname)]
        self.assertEqual(tenday_set,
                         [fname for fname in self.files if '.10d.' in fname])

    def test_mean_stencil_monthly(self):
        '''Test the regular expressions of the mean_stencil method - monthly'''
        func.logtest('Assert monthly pattern matching of mean_stencil:')
        args = (self.date[0], '11', None, '')
        patt = re.compile(self.meanstencil['Monthly'](*args))
        annual_set = [fname for fname in self.files if patt.search(fname)]
        self.assertEqual(annual_set,
                         [fname for fname in self.files if '.1m.' in fname])

    def test_mean_stencil_seasonal(self):
        '''Test the regexes of the mean_stencil method - seasonal'''
        func.logtest('Assert seasonal pattern matching of mean_stencil:')
        args = (self.date[0], self.date[1], self.ssn, '')
        patt = re.compile(self.meanstencil['Seasonal'](*args))
        annual_set = [fname for fname in self.files if patt.search(fname)]
        self.assertEqual(annual_set,
                         [fname for fname in self.files if '.1s.' in fname])

    def test_mean_stencil_annual(self):
        '''Test the regular expressions of the mean_stencil method - annual'''
        func.logtest('Assert annual pattern matching of mean_stencil:')
        args = (self.date[0], None, None, '')
        patt = re.compile(self.meanstencil['Annual'](*args))
        annual_set = [fname for fname in self.files if patt.search(fname)]
        self.assertEqual(annual_set,
                         [fname for fname in self.files if
                          '.1y.' in fname and self.date[0] + '-11.' in fname])

    def test_mean_stencil_all_years(self):
        '''Test the regex of the mean_stencil method - all years'''
        func.logtest('Assert all years pattern matching of mean_stencil:')
        args = ('.*', None, None, '')
        patt = re.compile(self.meanstencil['Annual'](*args))
        annual_set = [fname for fname in self.files if patt.search(fname)]
        self.assertEqual(annual_set,
                         [fname for fname in self.files if '.1y.' in fname])


class UtilityMethodTests(unittest.TestCase):
    '''Unit tests relating to the CICE utility methods'''
    def setUp(self):
        self.cice = cice.CicePostProc()

    def tearDown(self):
        try:
            os.remove('nemocicepp.nl')
        except OSError:
            pass

    def test_get_date_yyyymmdd(self):
        '''Test get_date method - YYYY-MM-DD format'''
        func.logtest('Assert functionality of get_date method (YYYY-MM-DD):')
        files = [
            'RUNIDi.restart.1982-11-01-00000',
            'RUNIDi.restart.1982-11-01-00000.nc',
            'RUNIDi.10d.1982-11-01.nc',
            'RUNIDi.1m.1982-11-01.nc',
            ]
        for fname in files:
            date = self.cice.get_date(fname)
            self.assertEqual(date, ('1982', '11', '01'))

    def test_get_date_yyyymm(self):
        '''Test get_date method - YYYY-MM format'''
        func.logtest('Assert functionality of get_date method (YYYY-MM):')
        files = {
            'RUNIDi.1m.1982-11.nc': ('1982', '11', None),
            'RUNIDi.1s.1982-11.nc': ('1982', '11', None),
            'RUNIDi.1s.1982-09_1982-11.nc': ('1982', '09', None),
            'RUNIDi.1y.1982-11.nc': ('1982', '11', None),
            'RUNIDi.1y.1981-12_1982-11.nc': ('1981', '12', None),
            }
        for fname in files:
            date = self.cice.get_date(fname)
            self.assertEqual(date, files[fname])

    def test_get_date_enddate(self):
        '''Test get_date method - end date requested'''
        func.logtest('Assert functionality of get_date method (YYYY-MM):')
        files = [
            'RUNIDi.restart.1982-11-01-00000.nc',
            'RUNIDi.10d.1982-11-01.nc',
            'RUNIDi.1m.1982-11.nc',
            'RUNIDi.1s.1982-09_1982-11.nc',
            'RUNIDi.1y.1981-12_1982-11.nc',
            ]
        for fname in files:
            date = self.cice.get_date(fname, startdate=False)
            self.assertEqual(date[:2], ('1982', '11'))

    def test_get_date_failure(self):
        '''Test get_date method - catch failure'''
        func.logtest('Assert error trapping in get_date method:')
        date = self.cice.get_date('RUNIDi_1m_YYYY-MM-DD.nc')
        self.assertEqual(date, (None,)*3)
        self.assertIn('[WARN]  Unable to get date', func.capture('err'))


class MeansProcessingTests(unittest.TestCase):
    '''Unit tests relating to the processing of means files'''
    def setUp(self):
        self.cice = cice.CicePostProc()
        self.cice.nl.means_directory = self.cice.nl.restart_directory = '.'
        self.cice.suite = mock.Mock()
        self.cice.suite.prefix = 'RUNID'
        self.meanfiles = [
            'RUNIDi.10d_24h.1987-12-13.nc',
            'RUNIDi.10d_24h.1988-01-01.nc',
            'RUNIDi.10d_24h.1988-01-02.nc',
            'RUNIDi.10d_24h.1988-01-17.nc',
            'RUNIDi.10d_24h.1988-01-30.nc',
            'RUNIDi.10d_24h.1988-02-01.nc',
            'RUNIDi.10d_24h.1988-02-10.nc',
            ]

    def tearDown(self):
        for fname in self.meanfiles + ['nemocicepp.nl']:
            try:
                os.remove(fname)
            except OSError:
                pass

    @mock.patch('utils.get_subset')
    @mock.patch('modeltemplate.ModelTemplate.move_to_share')
    def test_concat_daily(self, mock_mv, mock_set):
        '''Test method to compile list of means to concatenate'''
        func.logtest('Assert compilation of means to concatenate:')
        mock_set.side_effect = [['END.1111-22-33.nc'], ['SET1', 'SET2'], []]
        with mock.patch('utils.log_msg') as mock_log:
            # Mock log_msg because it will cause an exit with insufficient
            # components to mane a complete 30d file
            self.cice.archive_concat_daily_means()
            mock_log.assert_called_with(' -> Nothing to archive')
        self.cice.suite.preprocess_file.assert_called_with(
            'ncrcat', ['./END.1111-22-33.nc', './SET1', './SET2'],
            outfile='./RUNIDi_1d_11112101-11112201.nc'
            )
        self.assertEqual(mock_mv.mock_calls, [])

    @mock.patch('utils.get_subset')
    def test_concat_daily_shift_year(self, mock_set):
        '''Test method to compile list of means to concatenate - year shift'''
        func.logtest('Assert compilation of means to concatenate - yr shift:')
        mock_set.side_effect = [['END.1111-01-33.nc'], ['SET1', 'SET2'], []]
        with mock.patch('utils.log_msg'):
            self.cice.archive_concat_daily_means()
        self.cice.suite.preprocess_file.assert_called_with(
            'ncrcat', ['./END.1111-01-33.nc', './SET1', './SET2'],
            outfile='./RUNIDi_1d_11101201-11110101.nc'
            )

    def test_concat_daily_patterns(self):
        '''Test method to compile list of means to concatenate - patterns'''
        func.logtest('Assert compilation of means to concatenate - patterns:')
        for fname in self.meanfiles:
            open(fname, 'w').close()
        with mock.patch('utils.log_msg'):
            self.cice.archive_concat_daily_means()
        ncrcat = self.cice.suite.preprocess_file.mock_calls
        infiles1 = sorted('./' + fn for fn in self.meanfiles[:2])
        infiles2 = sorted('./' + fn for fn in self.meanfiles[2:6])
        self.assertIn(mock.call('ncrcat',
                                infiles1,
                                outfile='./RUNIDi_1d_19871201-19880101.nc'),
                      ncrcat)
        self.assertIn(mock.call('ncrcat',
                                infiles2,
                                outfile='./RUNIDi_1d_19880101-19880201.nc'),
                      ncrcat)

    @mock.patch('modeltemplate.ModelTemplate.move_to_share')
    def test_concat_daily_move(self, mock_mv):
        '''Test method to compile list of means to concatenate - move'''
        func.logtest('Assert compilation of means to concatenate - move:')
        self.cice.nl.means_directory = 'TestDir'
        with mock.patch('utils.get_subset', return_value=[]):
            self.cice.archive_concat_daily_means()
        mock_mv.assert_called_once_with(pattern=mock.ANY)

    @mock.patch('utils.get_subset')
    def test_concat_daily_insuffient(self, mock_set):
        '''Test concatenation of  means - insufficent components'''
        func.logtest('Assert concatenation not possible:')
        mock_set.side_effect = [['END.1111-22-33.nc'], ['SET1', 'SET2']]
        with self.assertRaises(SystemExit):
            self.cice.archive_concat_daily_means()
        self.assertIn('only got 3 files', func.capture('err'))

    @mock.patch('utils.remove_files')
    @mock.patch('modeltemplate.ModelTemplate.archive_files')
    @mock.patch('utils.get_subset')
    def test_concat_daily_arch(self, mock_set, mock_arch, mock_rm):
        '''Test concatenation of  means - archive'''
        func.logtest('Assert archive of catted file:')
        mock_set.side_effect = [[], ['ARCH1', 'ARCH2']]
        mock_arch.return_value = {'ARCH1': 'OK', 'ARCH2': 'OK'}
        self.cice.archive_concat_daily_means()
        self.assertIn('Deleting archive', func.capture())
        mock_rm.assert_called_with(['ARCH1', 'ARCH2'], '.')

    @mock.patch('modeltemplate.ModelTemplate.archive_files')
    @mock.patch('utils.get_subset')
    def test_concat_daily_archfail(self, mock_set, mock_arch):
        '''Test concatenation of  means - failed to archive'''
        func.logtest('Assert failure to archive catted file:')
        mock_set.side_effect = [[], ['ARCH1', 'ARCH2']]
        mock_arch.return_value = {'ARCH1': 'FAILED', 'ARCH2': 'OK'}
        self.cice.archive_concat_daily_means()
        self.assertNotIn('Deleting archive', func.capture())


def main():
    '''Main function'''
    unittest.main(buffer=True)


if __name__ == '__main__':
    main()
