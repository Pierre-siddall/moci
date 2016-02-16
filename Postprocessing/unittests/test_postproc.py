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
import argparse
import unittest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help='Specify test directory')
    parser.add_argument('-g', '--group', help='Specify test group',
                        action='append')
    args = parser.parse_args()

    if args.path:
        testpath = args.path
    else:
        testpath = '.'

    print testpath

    groups = {
        'all':      'test_*.py',
        'common':   'test_common_*.py',
        'suitegen': 'test_common_suitegen.py',
        'nlist':    'test_common_nlist.py',
        'utils':    'test_common_utils.py',
        'moo':      'test_common_moo.py',
        'nemocice': 'test_nemocice*.py',
        'nemo':     'test_nemocice_nemo.py',
        'template': 'test_nemocice_template.py',
        }

    if args.group:
        testgroup = args.group
    else:
        testgroup = ['all']

    for g in testgroup:
        try:
            testSuite = unittest.TestLoader().discover(testpath,
                                                       pattern=groups[g])
        except KeyError:
            print '[ERROR] UnitTest - Unknown group: {}'.format(g)
            continue
        print '[INFO] Running test group: {}'.format(g)
        testResults = unittest.TextTestRunner(buffer=True).run(testSuite)


if __name__ == '__main__':
    main()
