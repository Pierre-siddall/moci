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
NAME
    main_pp.py

SYNOPSIS
    main_pp.py [atmos] [nemocice]

DESCRIPTION
    Post-Processing app for use with Rose Suites - UM vn9.1 ->

ARGUMENTS
    The models to run. Default:
        atmos nemocice
'''

import os
import sys
import importlib

import utils

if len(sys.argv) > 1:
    additional_modules = sys.argv[1:]
else:
    additional_modules = ['atmos', 'nemocice']

for mod in ['common'] + additional_modules:
    sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/'+mod)


def main():
    models = {}

    for name in ['ATMOS', 'NEMO', 'CICE']:
        try:
            mod = importlib.import_module(name.lower())
            models[name] = mod.INSTANCE
        except ImportError:
            # Either the optional import was not requested, or it is not
            # available.
            # A module may not be available if it was not required by the
            # repository extract.
            pass
        except AttributeError:
            utils.log_msg('Unable to find object instance for ' + name, 5)

    for m in models:
        nlfile, mclass = models[m]
        model = mclass(nlfile)
        if model.runpp:
            for meth in model.methods:
                if model.methods[meth]:
                    utils.log_msg('Running {} for {}...'.format(meth, m))
                    getattr(model, meth)()
            exitCheck = model.suite.archiveOK

    if not exitCheck:
        exit(999)

if __name__ == '__main__':
    main()
