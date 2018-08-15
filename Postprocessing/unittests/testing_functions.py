#!/usr/bin/env python
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2015-2018 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
'''
import sys


def logtest(msg, err=False):
    '''Print message to standard output stream'''
    if err:
        sys.stderr.write('\n[TEST_ERROR] ' + msg + '\n')
    else:
        sys.stdout.write('\n[TEST] ' + msg + '\n')


def capture(direct='out'):
    '''
    Capture the message set to specified output stream.
    Standard options for direct argument: 'out', 'err'
    '''
    if 'out' in str(direct).lower():
        stream = sys.stdout
    elif 'err' in str(direct).lower():
        stream = sys.stderr
    else:
        stream = direct

    try:
        return stream.getvalue().strip()
    except AttributeError:
        logtest('general.capture: Output stream not specified', err=True)
        return ''
