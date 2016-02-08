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
from __future__ import print_function

import unittest
import mock
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(__file__)))+'/common')

import runtimeEnvironment
import nlist
import testing_functions as func


class namelistFileTests(unittest.TestCase):
    def setUp(self):
        self.nlfile = 'pp.nl'
        open(self.nlfile, 'w').close()
        self.newnlfile = 'NoFile'
        self.testnl = '''
&testnl
test_variable="Blue",
/
'''
        if not hasattr(sys.stdout, 'getvalue'):
            msg = 'This test requires buffered mode to run (buffer=True)'
            self.fail(msg)

    def tearDown(self):
        for fn in [self.nlfile, self.newnlfile]:
            if os.path.exists(fn):
                os.remove(fn)

    def testLoadOneFile(self):
        '''Test load one namelist file'''
        func.logtest('Load single namelist file:')
        with open(self.nlfile, 'w') as handle:
            handle.write(self.testnl)
        namelists = nlist.loadNamelist(self.nlfile)
        self.assertEqual(namelists.testnl.test_variable, 'Blue')

    def testLoadTwoFiles(self):
        '''Test load two namelists - one blank, one non-existent'''
        func.logtest('Load two namelists - one blank, one non-existent:')
        namelists = nlist.loadNamelist(self.nlfile, self.newnlfile)
        self.assertTrue(os.path.exists(self.newnlfile),
                        msg='Failed to create new namelist file: {}'.
                        format(self.newnlfile))
        self.assertEqual(namelists.suitegen.archive_command, 'Moose',
                         msg='Failed to load default &suitegen '
                         '(archive_command=Moose)')

    def testLoadBlankFile(self):
        '''Test load one blank file'''
        func.logtest('Load single blank namelist file:')
        namelists = nlist.loadNamelist(self.nlfile)
        attributes = [a for a in dir(namelists) if not a.startswith('__')]
        self.assertListEqual(attributes, [])

    def testCreateUnwritableFile(self):
        '''Test attempt to create a file in unwritable location'''
        func.logtest('Attempt to create a file in an unwritable location:')
        with self.assertRaises(SystemExit):
            nlist.create_example_nl('NoDir/' + self.newnlfile)


class readNamelistTests(unittest.TestCase):
    def setUp(self):
        self.nlvars = {
            'integerVar=1': 1,
            'floatVar=1.0': 1.0,
            'arrayVar="a","b",,1,2.5,false': ['a', 'b', '', 1, 2.5, False],
            'stringVar="$Hello There $$$"': '$Hello There $$$',
            'envVar=$PWD': os.environ['PWD'],
            'boolVar=true': True
        }
        if not hasattr(sys.stdout, 'getvalue'):
            msg = 'This test requires buffered mode to run (buffer=True)'
            self.fail(msg)

    def testReadNamlist(self):
        '''Test reading suitegen namelist'''
        func.logtest('Read in namelist with defaults available (suitegen):')
        namelist = nlist.ReadNamelist('suitegen', self.nlvars.keys())
        for line in self.nlvars:
            var, val = line.split('=')
            self.assertEqual(getattr(namelist, var), self.nlvars[line])
        self.assertEqual(namelist.prefix, os.environ['RUNID'])

    def testReadNoDefaultNL(self):
        '''Test reading namelist with no defaults'''
        func.logtest('Attempt to read in namelist with no defaults:')
        namelist = nlist.ReadNamelist('noDefault', self.nlvars.keys())
        self.assertIn('[WARN]', func.capture(direct='err'))

    def testTypeCasting(self):
        '''Test type casting functionality of _testVal - single values only'''
        func.logtest('Type casting in _testVal (single values only):')
        for line in self.nlvars:
            if type(self.nlvars[line]) == list:
                continue
            var, val = line.split("=")
            self.assertEqual(type(nlist.ReadNamelist._testVal(val)),
                             type(self.nlvars[line]))

    def testReadVariablesSingleLine(self):
        '''Test reading a single line array'''
        func.logtest('Read in array length of one:')
        mymock = mock.Mock(nlist.ReadNamelist)
        mymock._uppercase_vars = True
        mymock._testVal = nlist.ReadNamelist._testVal
        nlist.ReadNamelist._readVariables(mymock, 'myColour="blue"')
        self.assertEqual(mymock.MYCOLOUR, 'blue')


def main():
    unittest.main(buffer=True)

if __name__ == '__main__':
    main()
