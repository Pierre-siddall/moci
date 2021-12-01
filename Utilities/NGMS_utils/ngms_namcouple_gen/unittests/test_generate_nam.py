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
import os
import sys
import unittest
import unittest.mock as mock

sys.modules['read_nl'] = mock.MagicMock()
sys.modules['read_rose_app_conf'] = mock.MagicMock()
import generate_nam

class TestGlobal(unittest.TestCase):
    '''
    Test any global variables in the module
    '''
    def test_error(self):
        '''An error code must be between 1 and 127 inclusive'''
        self.assertTrue(1 <= generate_nam.GENERATE_NAM_ERROR <= 127)

class TestIdentifyNameLists(unittest.TestCase):
    '''
    Test the identifying and stripping out of header and coupling
    namelists from the namelist dictionaries
    '''
    def setUp(self):
        '''Make a namelist dictionary that can be used to test everything'''
        self.namelist = {'namcheader': {'atm_wrap': 0, 'runtime': 86400},
                         'atm1': {'src_name': 'atmos1'},
                         'atm2': {'src_name': 'atmos2'},
                         'ocn1': {'src_name': 'ocean1'},
                         'top1': {'src_name': 'top1'},
                         'namctl': {'dump_freq_im': 3600}}

    def test_default_behavior(self):
        '''The default assumes atmosphere ocean as coupled models'''
        expected_header = {'atm_wrap': 0, 'runtime': 86400}
        expected_nls = [{'src_name': 'atmos1'},
                        {'src_name': 'atmos2'},
                        {'src_name': 'ocean1'}]
        self.assertEqual((expected_header, expected_nls),
                         generate_nam.identify_namelists(self.namelist))

    def test_custom_models(self):
        '''We check that for passing in custom models we identify the correct
        namelists'''
        expected_header = {'atm_wrap': 0, 'runtime': 86400}
        expected_nls = [{'src_name': 'ocean1'},
                        {'src_name': 'top1'}]
        self.assertEqual((expected_header, expected_nls),
                         generate_nam.identify_namelists(
                             self.namelist, model_types=('ocn', 'top')))

class TestLoadData(unittest.TestCase):
    '''
    Test the load_data function
    '''
    @mock.patch('generate_nam.sys.stderr.write')
    def test_incorrect_mode(self, mock_stderr):
        '''An incorrect mode should cause a message to standard error and
        an exit'''
        expected_err = '[FAIL] The file loading mode wrong_mode is not' \
                       ' valid\n  The mode must be either:\n      ' \
                       'rose_app_conf\n      namelist\n'
        with self.assertRaises(SystemExit) as context:
            generate_nam.load_data('filename', 'wrong_mode')
        self.assertEqual(context.exception.code,
                         generate_nam.GENERATE_NAM_ERROR)
        mock_stderr.assert_called_once_with(expected_err)

    @mock.patch('generate_nam.read_nl.read_nl')
    @mock.patch('generate_nam.read_rose_app_conf.read_rose_app_conf')
    def test_load_namelist_succeed(self, mock_rose, mock_nl):
        '''Test successful load of a namelist'''
        mock_nl.return_value = (0, 'nl_namelists')
        expected_rvalue = 'nl_namelists'
        self.assertEqual(expected_rvalue,
                         generate_nam.load_data('filename', 'namelist'))
        mock_nl.assert_called_once_with('filename')
        mock_rose.assert_not_called()

    @mock.patch('generate_nam.sys.stderr.write')
    @mock.patch('generate_nam.read_nl.read_nl')
    @mock.patch('generate_nam.read_rose_app_conf.read_rose_app_conf')
    def test_load_namelist_fail(self, mock_rose, mock_nl, mock_stderr):
        '''Test failed load of a namelist'''
        mock_nl.return_value = (1, None)
        expected_err = '[FAIL] There has been an error loading file filename\n'
        with self.assertRaises(SystemExit) as context:
            generate_nam.load_data('filename', 'namelist')
        self.assertEqual(context.exception.code,
                         generate_nam.GENERATE_NAM_ERROR)
        mock_nl.assert_called_once_with('filename')
        mock_rose.assert_not_called()
        mock_stderr.assert_called_once_with(expected_err)

    @mock.patch('generate_nam.read_nl.read_nl')
    @mock.patch('generate_nam.read_rose_app_conf.read_rose_app_conf')
    def test_load_rose_succeed(self, mock_rose, mock_nl):
        '''Test successful load of a rose conf file'''
        mock_rose.return_value = (0, {'env': 'environments',
                                      'namelist': 'rose_namelists'})
        expected_rvalue = 'rose_namelists'
        self.assertEqual(expected_rvalue,
                         generate_nam.load_data('filename', 'rose_app_conf'))
        mock_rose.assert_called_once_with('filename')
        mock_nl.assert_not_called()

    @mock.patch('generate_nam.sys.stderr.write')
    @mock.patch('generate_nam.read_nl.read_nl')
    @mock.patch('generate_nam.read_rose_app_conf.read_rose_app_conf')
    def test_load_rose_fail(self, mock_rose, mock_nl, mock_stderr):
        '''Test failed load of a rose conf file'''
        mock_rose.return_value = (1, {})
        expected_err = '[FAIL] There has been an error loading file filename\n'
        with self.assertRaises(SystemExit) as context:
            generate_nam.load_data('filename', 'rose_app_conf')
        self.assertEqual(context.exception.code,
                         generate_nam.GENERATE_NAM_ERROR)
        mock_rose.assert_called_once_with('filename')
        mock_nl.assert_not_called()
        mock_stderr.assert_called_once_with(expected_err)

    @mock.patch('generate_nam.read_rose_app_conf.read_rose_app_conf')
    def test_rose_no_namelist_dict(self, mock_rose):
        '''Test the sucessful return of a rose conf namelist, but with a
        dictionary that doesnt have a namelist key. Should return an empty
        dictionary'''
        mock_rose.return_value = (0, {'env': 'environment_variables'})
        self.assertEqual({},
                         generate_nam.load_data('filename', 'rose_app_conf'))


class TestBuildNamcouple(unittest.TestCase):
    '''
    Test the building of the namcouple file
    '''
    @mock.patch('generate_nam.generate_nam_s1.construct_section_one')
    @mock.patch('generate_nam.generate_nam_s2.gen_section_two_item')
    def test_build_namcouple(self, mock_sect2, mock_sect1):
        '''Test the calling out to build the namcouple file from section
        one and section two'''
        mock_sect1.return_value = 'section_one'
        mock_sect2.side_effect = ['section_two_i1',
                                  'section_two_i2',
                                  'section_two_i3']
        expected_start_strings = '##################\n###\n### Coupling fields'\
                                 '\n###\n##################\n$STRINGS\n'
        expected_end_strings = '$END'
        expected_rvalue = 'section_one{}section_two_i1' \
                          'section_two_i2section_two_i3{}'. \
                          format(expected_start_strings, expected_end_strings)
        rvalue = generate_nam.build_namcouple('header', ['a', 'b', 'c'])
        mock_sect1.assert_called_once_with('header', 3)
        mock_sect2.assert_has_calls([mock.call('header', 'a'),
                                     mock.call('header', 'b'),
                                     mock.call('header', 'c')])
        self.assertEqual(expected_rvalue, rvalue)


class TestWriteNamcouple(unittest.TestCase):
    '''
    Test the writing of a file is correct
    '''
    def setUp(self):
        '''Set up the testing'''
        self.filename = 'test_namcouple'
        self.file_contents = 'line1\nline2'

    def tearDown(self):
        '''Clean up after the test'''
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

    def test_write_namcouple(self):
        '''Test the write namcouple function'''
        generate_nam.write_namcouple(self.file_contents, self.filename)
        # check the contents of the file
        with open(self.filename, 'r') as test_fh:
            test_contents = test_fh.read()
        self.assertEqual(test_contents, self.file_contents)


class CommandLineInterface(unittest.TestCase):
    '''
    Test the aspects of the command line interface to the script
    '''
    @mock.patch('generate_nam.argparse.ArgumentParser')
    def test_gather_argument_description(self, mock_argparse):
        '''Check the description of the script is correct'''
        expected_description = ('Convert a fortran namelist, or rose-app.conf'
                                ' file from a coupled model configuration into'
                                ' a namcouple file')
        generate_nam.gather_arguments()
        mock_argparse.assert_called_once_with(description=expected_description)

    @mock.patch('generate_nam.argparse.ArgumentParser')
    def test_gather_argument_arguments(self, mock_argparse):
        '''Check that all the helps/default values/variable names etc are
        correct'''
        # a list of expected calls
        calls = [mock.call('-o', '--output_file',
                           action='store',
                           dest='namcouple_fn', default='namcouple',
                           help='Filename for the namcouple file produced'),
                 mock.call('mode',
                           choices=('namelist', 'rose_app_conf'),
                           help='Select the type of input file'),
                 mock.call('input_file',
                           help='The input file from which the namecouple is'
                           ' to be produced')]
        generate_nam.gather_arguments()
        mock_argparse.return_value.add_argument.assert_has_calls(
            calls, any_order=False)
        self.assertEqual(
            mock_argparse.return_value.add_argument.call_count, 3)

    @mock.patch('generate_nam.argparse.ArgumentParser')
    def test_gather_argument_return_value(self, mock_argparse):
        '''Check we are returning a the return value from
        argparse.ArgumentParser.parse_args() correctly'''
        mock_argparse.return_value.parse_args.return_value = 'parsed_arguments'
        self.assertEqual('parsed_arguments', generate_nam.gather_arguments())
        mock_argparse.return_value.parse_args.assert_called_once_with()


class TestGenerateNam(unittest.TestCase):
    '''
    Test the interface function of the script, that provides an interface to
    any other code that might want to call it
    '''
    @mock.patch('generate_nam.load_data')
    @mock.patch('generate_nam.identify_namelists')
    @mock.patch('generate_nam.build_namcouple')
    @mock.patch('generate_nam.write_namcouple')
    def test_generate_nam(
            self, mock_write, mock_build, mock_identify, mock_load):
        '''Ensure that the correct arguments are passed to the functions that
        do the work generating and writing the namcouple file'''
        # mock our return values that we require, using strings for variable
        # names
        mock_load.return_value = 'namelist_data'
        mock_identify.return_value = ('header_namelist', 'coupling_namelists')
        mock_build.return_value = 'namcouple_contents'
        generate_nam.generate_nam('inputfile', 'outputfile', 'mode')
        mock_load.assert_called_once_with('inputfile', 'mode')
        mock_identify.assert_called_once_with('namelist_data')
        mock_build.assert_called_once_with('header_namelist',
                                           'coupling_namelists')
        mock_write.assert_called_once_with('namcouple_contents', 'outputfile')


class TestMain(unittest.TestCase):
    '''
    Test the main function when the code is run interactively
    '''
    def setUp(self):
        '''Set up variables for the unit test'''
        class ArgParseSim:
            '''Class for our fake arg_parse object'''
            def __init__(self):
                '''Create our variables'''
                self.input_file = 'input_file'
                self.namcouple_fn = 'namcouple_fn'
                self.mode = 'mode'

        self.args = ArgParseSim()

    @mock.patch('generate_nam.gather_arguments')
    @mock.patch('generate_nam.generate_nam')
    def test_main(self, mock_generate, mock_gather):
        '''Test the main interactive function'''
        mock_gather.return_value = self.args
        generate_nam.main()
        mock_gather.assert_called_once_with()
        mock_generate.assert_called_once_with(self.args.input_file,
                                              self.args.namcouple_fn,
                                              self.args.mode)
