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
    control.py

DESCRIPTION
    Base class definition for running models within the post processing app
'''

import abc
import importlib

import utils


class runPostProc(object):
    '''
    Control class template for input models
    '''
    __metatclass__ = abc.ABCMeta

    @abc.abstractproperty
    def runpp(self):
        msg = 'runpp - Model Post-Processing logical trigger not defined.'
        msg += '\n\t return: boolean'
        utils.log_msg(msg, 4)
        raise NotImplementedError

    @abc.abstractproperty
    def methods(self):
        msg = 'runpp - Model Post-Processing property not defined.'
        msg += '\n\t return: OrderedDict([ ("MethodName", LogicalValue), ])'
        utils.log_msg(msg, 4)
        raise NotImplementedError

NL = {}

input_modules = ['suite', 'atmosNamelist', 'nemoNamelist', 'ciceNamelist', 'moo']

for mod in input_modules:
    try:
        name = importlib.import_module(mod)
        NL.update(name.NAMELISTS)

    except ImportError:
        if mod == 'suite':
            utils.log_msg('Unable to find suite module', 5)

    except AttributeError:
        utils.log_msg('Unable to determine default namelists for ' + mod, 3)
