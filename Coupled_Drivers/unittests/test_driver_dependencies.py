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
import unittest.mock as mock

import collections
import io
import os
import driver_dependencies


class TestGetImports(unittest.TestCase):
    '''
    Test the get_imports method of the FindDependencies class. We construct
    a series of test files to check the imports
    '''
    def setUp(self):
        '''Create dummy container for scripts present to make sure things will
        always work correctly'''
        self.scripts_present = []

    def write_file(self, filedictionary):
        '''Writes string to text file from file dictionarys, and append
        to scripts_present'''
        for filename, contents in filedictionary.items():
            with open(filename, 'w') as handle:
                handle.write(contents)
            self.scripts_present.append(filename)

    def clearup_files(self):
        '''Remove any files used for the test'''
        for filename in self.scripts_present:
            os.remove(filename)
        self.scripts_present = []

    def remove_file_items(self, *filenames):
        '''Remove all traces of a single file to customise tests'''
        for filename in filenames:
            assert filename in self.scripts_present
            os.remove(filename)
            self.scripts_present.remove(filename)

    def tearDown(self):
        '''Make sure the cleanup happens at the end'''
        self.clearup_files()

    def setup_test_different_formats(self):
        '''Setup test files for differing syntaxes of import'''
        self.multi_format_files = {
            'module_test_driver.py': 'import moduleA\n' \
            'from moduleB import function1\n' \
            'from moduleC import function2, function3\n' \
            'import packageA.moduleB\n', \
            'moduleA.py': '', \
            'moduleB.py': '', \
            'moduleC.py': ''}
        self.write_file(self.multi_format_files)

    @mock.patch('os.path.isfile')
    def test_different_formats(self, mock_isfile):
        '''Test the differing import formats'''
        self.setup_test_different_formats()
        test_dependencies = driver_dependencies.FindDependencies(
            self.scripts_present,
            './',
            ['module_test_driver.py'])
        expected_return = {'moduleA.py', 'moduleB.py', 'moduleC.py',
                           'module_test_driver.py', 'packageA/moduleB.py'}
        mock_isfile.return_value = True
        self.assertEqual(test_dependencies.get_imports(),
                         expected_return)
        mock_isfile.assert_called_once_with('./packageA/moduleB.py')
        self.clearup_files()

    @mock.patch('os.path.isfile')
    def test_different_formats_package_not_present(self, mock_isfile):
        '''Test the differing import formats with the file in the package
        not present'''
        self.setup_test_different_formats()
        test_dependencies = driver_dependencies.FindDependencies(
            self.scripts_present,
            './',
            ['module_test_driver.py'])
        expected_return = {'moduleA.py', 'moduleB.py', 'moduleC.py',
                           'module_test_driver.py'}
        mock_isfile.return_value = False
        self.assertEqual(test_dependencies.get_imports(),
                         expected_return)
        mock_isfile.assert_called_once_with('./packageA/moduleB.py')
        self.clearup_files()

    def setup_test_correct(self):
        '''Setup files for the correct syntax
         module_test_driver.py IMPORTS moduleA AND module B
         moduleA IMPORTS module1 AND module2
         moduleB IMPORTS module2 and moduleA
         module1 IMPORTS moduleZ
        '''
        self.correct_files = {
            'module_test_driver.py': 'import moduleA\nimport moduleB\n',
            'module_test_driver2.py': 'import moduleZ',
            'moduleA.py': 'import module1\nimport module2\n',
            'moduleB.py': 'import module2\nimport moduleA\n',
            'module1.py': 'import moduleZ\n',
            'module2.py': 'not an import to be picked up\n',
            'moduleZ.py': '#commented\n#import'}
        self.write_file(self.correct_files)

    def test_all_present_one_test_file(self):
        '''Test When all the modules are present to be tested, we pick up
        all the import dependencies'''
        self.setup_test_correct()
        test_dependencies = driver_dependencies.FindDependencies(
            self.scripts_present,
            './',
            ['module_test_driver.py'])

        expected_to_copy = {
            'moduleA.py', 'moduleB.py', 'module1.py',
            'module2.py', 'moduleZ.py', 'module_test_driver.py'}
        self.assertEqual(test_dependencies.get_imports(), expected_to_copy)
        del test_dependencies
        self.clearup_files()

    def test_some_not_present_two_test_file(self):
        '''Test two test driver files, however module1 and moduleB are not
        in the directory'''
        self.setup_test_correct()
        # Remove module1 and moduleB prior to test.
        self.remove_file_items('module1.py', 'moduleB.py')
        test_dependencies = driver_dependencies.FindDependencies(
            self.scripts_present,
            './',
            ['module_test_driver.py', 'module_test_driver2.py'])
        expected_to_copy = {
            'moduleA.py', 'module2.py', 'moduleZ.py',
            'module_test_driver.py', 'module_test_driver2.py'}
        self.assertEqual(test_dependencies.get_imports(), expected_to_copy)
        del test_dependencies
        self.clearup_files()

    def test_model_driver_not_present(self):
        '''Test error occurs when model driver is not present in the
        directory'''
        self.setup_test_correct()
        test_dependencies = driver_dependencies.FindDependencies(
            self.scripts_present,
            './',
            ['non_present_driver.py'])
        with self.assertRaises(FileNotFoundError):
            test_dependencies.get_imports()
        del test_dependencies


class TestGlobalVariables(unittest.TestCase):
    '''
    Test the global variables in the modules
    '''
    def test_override(self):
        '''Test the list of overrides for non .py files'''
        self.assertEqual(
            driver_dependencies.OVERRIDE,
            {'common': {'link_drivers', os.path.join('dr_env_lib',
                                                     'common_def.py')},
             'nemo': {'update_nemo_nl'},
             'mct': {'OASIS_fields'}})

class TestApplyOverrides(unittest.TestCase):
    '''
    Check the overrides are applied correctly
    '''
    def test_coupled_configuration_GC45(self):
        '''A GC4/GC5 model uses common, nemo, mct and should ignore um/xios'''
        models = ['um', 'nemo', 'mct', 'xios']
        expected_out = {'link_drivers', 'update_nemo_nl', 'OASIS_fields',
                        'dr_env_lib/common_def.py'}
        self.assertEqual(driver_dependencies.apply_overrides(models),
                         expected_out)

    def test_no_extra_models(self):
        '''If no models specified, the common ovveride is used'''
        models = []
        expected_out = {'link_drivers', 'dr_env_lib/common_def.py'}
        self.assertEqual(driver_dependencies.apply_overrides(models),
                         expected_out)

class TestMain(unittest.TestCase):
    '''
    Test the main function which sets up the driver depenencies and writes
    the list of files to standard output
    '''
    @mock.patch('driver_dependencies.get_models')
    @mock.patch('driver_dependencies.os.listdir')
    @mock.patch('driver_dependencies.FindDependencies')
    @mock.patch('driver_dependencies.apply_overrides')
    def test_main(self, mock_override, mock_dependencies, mock_listdir,
                  mock_models):
        '''Test the main function, this is basically just a list of mocked
        calls'''
        mock_models.return_value = ('models', 'model_files')
        mock_listdir.return_value = ['script1', 'script2']
        mock_depend_inst = mock_dependencies.return_value
        mock_depend_inst.get_imports.return_value = {'import1', 'import2',
                                                     'package_module'}
        # as we are using sets, the union method in the function under test
        # should ensure that only one import1 is written out
        mock_override.return_value = {'import1', 'override1', 'override2'}
        with mock.patch('driver_dependencies.sys.stdout',
                        new=io.StringIO()) as mock_stdout:
            driver_dependencies.main('extractdir')
        mock_models.assert_called_once_with()
        mock_listdir.assert_called_once_with('extractdir')
        mock_dependencies.assert_called_once_with(
            ['script1', 'script2'], 'extractdir', 'model_files')
        mock_depend_inst.get_imports.assert_called_once_with()
        mock_override.assert_called_once_with('models')
        # As the output string is created from an unordered set, we need to
        # do something a bit convoluted to make sure it contains what we
        # want it to
        output_string = mock_stdout.getvalue()
        # The output string needs to be five items separated by one space each
        self.assertRegex(output_string,
                         r'^\w+\s{1}\w+\s{1}\w+\s{1}\w+\s{1}\w+$')
        self.assertEqual(set(output_string.split(' ')),
                         {'import1', 'import2', 'override1', 'override2',
                          'package_module'})


class TestGetModels(unittest.TestCase):
    '''
    Test the retrieval of the models environmnet variable
    '''
    def unset_environment_variables(self):
        '''Unset the environment variables defined in the tests in this class'''
        environment_variables = ['models', 'L_OCN_PASS_TRC']
        for envar in environment_variables:
            try:
                del os.environ[envar]
            except KeyError:
                pass

    def tearDown(self):
        '''Clearup at end of test'''
        self.unset_environment_variables()

    @mock.patch('driver_dependencies.sys.stderr.write')
    def test_not_found(self, mock_stderr):
        '''Test we get an error message and exit when the environment variable
        is't found'''
        with self.assertRaises(SystemExit) as context:
            driver_dependencies.get_models()
        mock_stderr.assert_called_once_with(
            'Unable to find the environment variable models\n'
            ' containing a space separated list of components')
        self.assertEqual(context.exception.code, 1)

    def test_filename_construction(self):
        '''Test the construction of filenames from model list. SI3 and TOP
        have controllers, everything else has drivers'''
        #setup os environ
        os.environ['models'] = 'um nemo si3 top'
        expected_models_out = ['um', 'nemo', 'si3', 'top']
        expected_model_files = ['um_driver.py',
                                'nemo_driver.py',
                                'si3_controller.py',
                                'top_controller.py']
        self.assertEqual(driver_dependencies.get_models(),
                         (expected_models_out, expected_model_files))
        #check we dont modify os environ
        self.assertEqual(os.environ['models'], 'um nemo si3 top')
        self.unset_environment_variables()

    def test_filename_construction_l_ocn_pass_trc(self):
        '''Test the construction when TOP comes through from l_ocn_pass_trc'''
        #setup os environ
        os.environ['models'] = 'um nemo si3'
        os.environ['L_OCN_PASS_TRC'] = 'True'
        expected_models_out = ['um', 'nemo', 'si3', 'top']
        expected_model_files = ['um_driver.py',
                                'nemo_driver.py',
                                'si3_controller.py',
                                'top_controller.py']
        self.assertEqual(driver_dependencies.get_models(),
                         (expected_models_out, expected_model_files))
        #check we dont modify os environ
        self.assertEqual(os.environ['models'], 'um nemo si3')
        self.unset_environment_variables()

class CommandLineInterface(unittest.TestCase):
    '''
    Test the aspects of the command line interface to the script
    '''
    @mock.patch('driver_dependencies.argparse.ArgumentParser')
    @mock.patch('driver_dependencies.main')
    def test_run(self, mock_main, mock_argparse):
        '''Test the correct behaviour of command line arguments'''
        # get a list of the calls to add_argument
        calls = [mock.call("--extract-directory",
                           dest='extractdir',
                           help="Path the to the extract directory for the" \
                           " drivers python code")]
        mock_argparse.return_value.parse_args.return_value \
            = collections.namedtuple('args', 'extractdir')('direc')
        driver_dependencies.run_interactive()
        mock_argparse.return_value.add_argument.assert_has_calls(calls)
        mock_argparse.return_value.parse_args.assert_called_once_with()
        mock_main.assert_called_once_with('direc')
