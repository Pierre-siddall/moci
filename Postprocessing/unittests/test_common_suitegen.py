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
import mock
from collections import OrderedDict
import sys
sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(__file__)))+'/common')

import testing_functions as func
import suite


class suiteTests(unittest.TestCase):
    def setUp(self):
        os.environ['CYLC_TASK_LOG_ROOT'] = os.environ['PWD']
        print(self.id())
        if 'PreCylc6' in self.id():
            os.environ['CYLC_TASK_CYCLE_TIME'] = '1980090100'
        else:
            os.environ['CYLC_TASK_CYCLE_POINT'] = '19800901T0000Z'
        self.inputnl = OrderedDict([
            ('&suitegen', None),
            ('archive_set="SUITENAME"', 'suitename'),
            ('umtask_name="atmos"', 'umtask'),
            ('prefix="RUNID"', 'prefix'),
            ('cycleperiod=0, 1, 10, 0, 0', 'cycleperiod'),
            ('tasks_per_cycle=2', 'tasks_per_cycle'),
            ('archive_command="Moose"', None),
            ('/', None),
            ])
        self.myfile = 'input.nl'
        open(self.myfile, 'w').write('\n'.join(self.inputnl.keys()))
        self.mypath = 'somePath/directory'
        self.mySuite = suite.SuiteEnvironment(self.mypath, self.myfile)

    def tearDown(self):
        for fn in ['atmospp.nl', self.myfile]:
            try:
                os.remove(fn)
            except OSError:
                pass
        for var in ['CYLC_TASK_CYCLE_POINT', 'CYLC_TASK_CYCLE_TIME',
                    'ARCHIVE_FINAL']:
            try:
                del os.environ[var]
            except KeyError:
                pass

    def testSuiteObject(self):
        '''Test creation of suite object and assertion of Cylc6 environment'''
        func.logtest('Assert creation of a suite object:')
        self.assertEqual(self.mySuite.sourcedir, self.mypath)
        self.assertTrue(hasattr(self.mySuite.envars, 'CYLC_TASK_LOG_ROOT'))
        self.assertTrue(self.mySuite.cylc6)

    def testPreCylc6Suite(self):
        '''Test assertion of pre-Cylc6 environment'''
        func.logtest('Assert pre-Cylc6 suite creation:')
        self.assertFalse(self.mySuite.cylc6)
        self.assertTrue(hasattr(self.mySuite.envars, 'CYLC_TASK_CYCLE_TIME'))

    def testSuiteObjectBlankFile(self):
        '''Test creation of suite object with a blank namelist file'''
        func.logtest('Attempt to create suite obj with blank namelist file:')
        blank = 'blankfile.nl'
        open(blank, 'w').close()
        with self.assertRaises(SystemExit):
            blanksuite = suite.SuiteEnvironment(self.mypath, blank)
        os.remove(blank)

    def testProperties(self):
        '''Test access to suite properties'''
        func.logtest('Assert suite properties:')
        names = {x.split('=')[0]: [x.split('=')[1].strip('"\''),
                                   self.inputnl[x]]
                 for x in self.inputnl.keys() if self.inputnl[x]}
        for key in names:
            self.assertEqual(str(getattr(self.mySuite,
                                         names[key][1])).strip('[]'),
                             names[key][0])

    def testCyclestring(self):
        '''Test calculation of property "cyclestring in a Cylc6 environment"'''
        func.logtest('Assert cycletime as string array property:')
        self.assertTupleEqual(self.mySuite.cyclestring,
                              ('1980', '09', '01', '00', '00'))

    def testPreCylc6Cyclestring(self):
        '''Test calculation of property "cyclestring; pre-Cylc6 environment"'''
        func.logtest('Assert pre-Cylc6 cycletime as string array property:')
        self.assertTupleEqual(self.mySuite.cyclestring,
                              ('1980', '09', '01', '00'))

    def testCycledt(self):
        '''Test access to property "cycledt"'''
        func.logtest('Assert cycletime as integer array property:')
        self.assertListEqual(self.mySuite.cycledt, [1980, 9, 1, 0, 0])

    def testBadCycletime(self):
        '''Test failure mode with incorrect format for
        task cycle time environment variable'''
        func.logtest('Failure mode of cycletime property:')
        self.mySuite.envars.CYLC_TASK_CYCLE_POINT = 'Dummy'
        with self.assertRaises(SystemExit):
            print(self.mySuite.cyclestring)

    def testExistingCyclestring(self):
        '''Test access to previously calculated property "cyclestring"'''
        func.logtest('Retrieval existing cycle time string array:')
        mycycle = ('1981', '09', '01', '00', '00')
        self.mySuite._cyclestring = mycycle
        self.assertTupleEqual(self.mySuite.cyclestring, mycycle)

    def testFinalCycle(self):
        '''Test assertion of final cycle in Cylc6 environment'''
        func.logtest('Assert final cycle time property - TRUE:')
        os.environ['ARCHIVE_FINAL'] = 'true'
        self.assertTrue(self.mySuite.finalcycle)

    def testNotFinalCycle(self):
        '''Test negative assertion of final cycle in Cylc6 environment'''
        func.logtest('Assert final cycle time property - FALSE:')
        self.assertFalse(self.mySuite.finalcycle)

    def testPreCylc6FinalCycle(self):
        '''Test assertion of final cycle in pre-Cylc6 environment'''
        func.logtest('Assertpre-Cylc6 final cycle time property - TRUE:')
        os.environ['END_CYCLE_TIME'] = '1985090100'
        self.mySuite._cyclestring = ('1985', '09', '01', '00')
        self.assertTrue(self.mySuite.finalcycle)

    def testPreCylc6NotFinalCycle(self):
        '''Test negative assertion of final cycle in pre-Cylc6 environment'''
        func.logtest('Assert pre-Cylc6 final cycle time property - FALSE:')
        os.environ['END_CYCLE_TIME'] = '1985090100'
        self.assertFalse(self.mySuite.finalcycle)

    def testExistingFinalCycle(self):
        '''Test previously asserted final cycle'''
        func.logtest('Retrieval of existing final cycle time logical:')
        mycycle = ('2000', '09', '01', '00', '00')
        self.mySuite._finalcycle = mycycle
        self.assertTupleEqual(self.mySuite.finalcycle, mycycle)

    def testLog(self):
        '''Test creation of and access to property "logfile"'''
        func.logtest('Create a log file:')
        logfile = os.environ['PWD'] + '-archive.log'
        self.assertEqual(self.mySuite.logfile, logfile)


class archiveTests(unittest.TestCase):
    def setUp(self):
        os.environ['CYLC_TASK_LOG_ROOT'] = os.environ['PWD'] + '/job'
        self.logfile = os.environ['CYLC_TASK_LOG_ROOT'] + '-archive.log'
        os.environ['CYLC_TASK_CYCLE_POINT'] = '19800901T0000Z'
        self.mySuite = suite.SuiteEnvironment('somePath/directory', 'input.nl')

    def tearDown(self):
        for fn in ['input.nl', self.logfile]:
            if os.path.exists(fn):
                os.remove(fn)

    def testArchiveFile(self):
        '''Test archive_file command - moo is mocked out'''
        func.logtest('File archiving - success:')
        with mock.patch('moo.CommandExec') as dummy:
            moose_arch_inst = dummy.return_value
            moose_arch_inst.execute.return_value = {'TestFile': 0}
            rcode = self.mySuite.archive_file('TestFile')
            self.assertEqual(rcode, 0)
            self.assertIn('TestFile ARCHIVE OK',
                          open(self.mySuite.logfile, 'r').read())
            self.assertTrue(self.mySuite.archiveOK)

    def testArchiveFileFail(self):
        '''Test failure mode of archive_file command - moo is mocked out'''
        func.logtest('File archiving - failure:')
        with mock.patch('moo.CommandExec') as dummy:
            moose_arch_inst = dummy.return_value
            moose_arch_inst.execute.return_value = {'TestFile': -1}
            rcode = self.mySuite.archive_file('TestFile')
            self.assertNotEqual(rcode, 0)
            self.assertIn('TestFile ARCHIVE FAILED',
                          open(self.mySuite.logfile, 'r').read())
            self.assertFalse(self.mySuite.archiveOK)

    def testArchiveEmptyFile(self):
        '''Test attempt to archive an empty file - moo is mocked out'''
        func.logtest('File archiving - Empty file:')
        with mock.patch('moo.CommandExec') as dummy:
            moose_arch_inst = dummy.return_value
            moose_arch_inst.execute.return_value = {'TestFile': 11}
            rcode = self.mySuite.archive_file('TestFile')
            self.assertEqual(rcode, 11)
            self.assertIn('TestFile FILE NOT ARCHIVED',
                          open(self.mySuite.logfile, 'r').read())
            self.assertTrue(self.mySuite.archiveOK)

    def testArchiveFileDebug(self):
        '''Test debug mode of archive_file command with no file handle'''
        func.logtest('File archiving - debug:')
        rcode = self.mySuite.archive_file('TestFile', debug=True)
        self.assertEqual(rcode, 0)
        log = open(self.mySuite.logfile, 'r').read()
        self.assertIn('TestFile WOULD BE ARCHIVED', log)

    def testArchiveFileDebugOpenLog(self):
        '''Test debug mode of archive_file command with open file handle'''
        func.logtest('File archiving - log using open file:')
        logfile = 'OpenLog'
        with open(logfile, 'w') as fn:
            rcode = self.mySuite.archive_file('TestFile', fn, True)
        self.assertEqual(rcode, 0)
        self.assertIn('TestFile WOULD BE ARCHIVED', open(logfile, 'r').read())
        self.assertFalse(os.path.exists(self.logfile))
        os.remove(logfile)

    def testNoArchiveCommand(self):
        '''Test attempt to archive to alternative system'''
        func.logtest('Attempt to access alternative archiving system:')
        self.mySuite.nl.archive_command = 'Dummy'
        with self.assertRaises(SystemExit):
            rcode = self.mySuite.archive_file('TestFile')


def main():
    unittest.main(buffer=True)


if __name__ == '__main__':
    main()
