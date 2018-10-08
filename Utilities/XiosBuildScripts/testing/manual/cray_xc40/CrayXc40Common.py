#!/usr/bin/env python
"""
*****************************COPYRIGHT******************************
 (C) Crown copyright Met Office. All rights reserved.
 For further details please refer to the file COPYRIGHT.txt
 which you should have received as part of this distribution.
*****************************COPYRIGHT******************************

Settings for running build scripts manual on the UKMO Cray XC40.
"""
import os
import sys

def setup_path_to_scripts():
    """
    Get the path to the scripts to be tested, which should be 3 levels up
    """

    run_script_dir_path = os.path.realpath(os.path.dirname(__file__))
    root_dir = os.path.abspath(os.path.join(run_script_dir_path,
                                            os.pardir,
                                            os.pardir,
                                            os.pardir))
    script_dir = os.path.abspath(os.path.join(root_dir,
                                              'bin'))

    lib_dir = os.path.abspath(os.path.join(root_dir,
                                           'lib'))

    test_dir = os.path.abspath(os.path.join(root_dir,
                                            'testing'))

    settings_dir = os.path.abspath(os.path.join(test_dir,
                                                'settings'))

    sys.path += [script_dir, lib_dir, test_dir]
    script_env = os.environ
    script_env['PATH'] += ':{0}'.format(script_dir)

    try:
        script_env['PYTHONPATH'] += ':'.join([script_env['PYTHONPATH'],
                                              lib_dir,
                                              test_dir])
    except KeyError:
        script_env['PYTHONPATH'] = ':'.join([lib_dir, test_dir])

    dir_dict = {'lib': lib_dir,
                'root': root_dir,
                'bin': script_dir,
                'testing': test_dir,
                'settings': settings_dir}

    return (dir_dict, script_env)
