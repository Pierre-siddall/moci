#!/usr/bin/env python2.7

import unittest
import mock
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(
                                os.path.dirname(__file__)))+'/common')
import moo


def logtest(msg):
    print('\n[TEST] ' + msg)


class commandTests(unittest.TestCase):
    def setUp(self):
        self.cmd = {
            'CURRENT_RQST_ACTION': 'ARCHIVE',
            'CURRENT_RQST_NAME':   'TestFile',
            'DATAM':               os.environ['PWD'],
            'RUNID':               'runid',
            'CATEGORY':            'UNCATEGORISED'
        }

    def tearDown(self):
        pass

    def testInstanceCommandExec(self):
        '''Test creation of moose archiving object'''
        logtest('Check creation of moose object instance')
        inst = moo.CommandExec()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
