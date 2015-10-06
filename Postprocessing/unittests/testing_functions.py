#!/usr/bin/env python2.7

import sys


def logtest(msg, err=False):
    if err:
        print('\n[TEST_ERROR] ' + msg)
    else:
        print('\n[TEST] ' + msg)


def capture(direct='out'):
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
