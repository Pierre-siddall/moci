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
NAME
    driver_dependencies.py

DESCRIPTION
    Dependency checker for drivers to ensure that only the files required
    for a given model run appear in the work directory
'''
import argparse
import os
import re
import sys

# Overrides for non python scripts. File(s) for each component must
# be in a set
OVERRIDE = {
    'common': {'link_drivers', os.path.join('dr_env_lib', 'common_def.py')},
    'nemo': {'update_nemo_nl'},
    'mct': {'OASIS_fields'}}

class FindDependencies():
    '''
    A class to define our find dependencies object. To initalise
    we need a list of python scripts to investigate, the directory, and a
    list of one for more files to start the testing
    '''
    def __init__(self, scripts_present, extract_dir, test_files):
        '''
        Initialise the object. As we dont need duplicates, we create a set of
        files to copy (to_copy), a list of files still to test, (to_test) and
        an empty list of tested files (tested)
        '''
        self.driver_scripts = scripts_present
        self.extract_dir = extract_dir
        self.to_copy = set()
        self.to_test = test_files
        self.tested = []

    def get_imports(self):
        '''
        Recursive function. Checks the files in to_test. If the file hasn't
        already been tested check if we need to copy files, add to to_copy set.
        Once a file has been tested it is added to the tested list and remove
        from the to_test list. Once to_test is empty the recursion stops.
        '''
        # This regex checks for a valid import module command in a python
        # script
        import_regex = r'^\s*(?:from|import)\s+([\w\.]+(?:\w*,\w*\w+)*)'
        if self.to_test:
            filename = self.to_test[0]
            filepath = os.path.join(self.extract_dir, filename)
            self.to_copy.add(filename)
            with open(filepath, 'r') as handle:
                for line in handle.readlines():
                    try:
                        module = re.match(import_regex, line).group(1)
                        if '.' in module:
                            # we are actually dealing with a package
                            self._handle_packages(module)
                        else:
                            module = '{}.py'.format(module)
                            if module in self.driver_scripts:
                                self.to_copy.add(module)
                                if module not in self.tested:
                                    self.to_test.append(module)
                    except AttributeError:
                        pass
            self.tested.append(filename)
            self.to_test.remove(filename)
            self.get_imports()
        return self.to_copy

    def _handle_packages(self, package):
        '''If a MOCI driver package is being used, then we must handle
        this also'''
        package_name = package.split('.')[0]
        module_name = '{}.py'.format(package.split('.')[1])
        test_module_path = os.path.join(package_name, module_name)
        if os.path.isfile(os.path.join(self.extract_dir, test_module_path)):
            self.to_copy.add(test_module_path)


def get_models():
    '''
    We need to get the environment variable manually as we dont yet have
    access to the drivers' libraries
    '''
    try:
        models = os.environ['models']
    except KeyError:
        sys.stderr.write('Unable to find the environment variable models\n'
                         ' containing a space separated list of components')
        sys.exit(1)
    try:
        using_top = os.environ['L_OCN_PASS_TRC']
        if 't' in using_top.lower() and 'top' not in models:
            models = '{} top'.format(models)
    except KeyError:
        pass
    models = models.split(' ')
    #si3 and top have controllers, the rest have drivers
    model_files = ['{}_controller.py'.format(i_mod)
                   if i_mod in ('si3', 'top') else '{}_driver.py'.format(i_mod)
                   for i_mod in models]
    return models, model_files

def apply_overrides(models):
    '''
    Apply any overrides needed
    '''
    models.append('common')
    overrides = set()
    for i_model in models:
        try:
            overrides = overrides.union(OVERRIDE[i_model])
        except KeyError:
            pass
    return overrides

def main(extractdir):
    '''
    Return a list of files that need to be extracted at this stage
    '''
    models, model_files = get_models()
    drivers_scripts = os.listdir(extractdir)
    dependencies = FindDependencies(drivers_scripts, extractdir, model_files)

    modules_to_copy = dependencies.get_imports()
    to_copy = modules_to_copy.union(apply_overrides(models))
    sys.stdout.write(' '.join(to_copy))

def run_interactive():
    '''
    Parse the arguments for interactive running of this script
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract-directory",
                        dest='extractdir',
                        help="Path the to the extract directory for the" \
                        " drivers python code")
    args = parser.parse_args()
    main(args.extractdir)

if __name__ == '__main__':
    run_interactive()
