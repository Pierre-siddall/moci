#!/usr/bin/env python
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2021 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    env_lib.py

DESCRIPTION
    Common functions and classes required to handle environment variables
'''
import copy
import os
import sys


ENV_LIB_ERROR = 10

class LoadEnvar(object):
    '''
    Container to hold loaded environemnt variables so they can be easily
    accessed and modified as needed
    '''

    def __init__(self):
        '''
        Initialise a container dictionary for the variables
        '''
        self.env_vars = {}

    def load_envar(self, name, default_value=None):
        '''
        Load an environment variable, if it doesn't exist and no default is
        specified return an error code. If a default is specified set to
        default and alert the user that this has occured
        '''
        try:
            self.env_vars[name] = os.environ[name]
            return 0
        except KeyError:
            if default_value is not None:
                sys.stdout.write('[INFO] environment variable %s doesn\'t '
                                 'exist, setting to default value %s\n' %
                                 (name, default_value))
                self.env_vars[name] = default_value
                return 0
            return 1

    def contains(self, varname):
        '''
        Does the container contain the variable varname
        '''
        does_contain = varname in self.env_vars
        return does_contain

    def is_set(self, varname):
        '''
        Is the variable varname set in the environment
        '''
        try:
            _ = os.environ[varname]
            return True
        except KeyError:
            return False

    def add(self, varname, value):
        '''
        Add a variable to the container
        '''
        self.env_vars[varname] = value

    def remove(self, varname):
        '''
        Remove a variable from the container
        '''
        del self.env_vars[varname]

    def export(self):
        '''
        Export environment variable to the calling process
        '''
        for i_key in self.env_vars.keys():
            os.environ[i_key] = self.env_vars[i_key]

    def __getitem__(self, var_name):
        '''
        Return an environment variable value using the syntax
        LoadEnvar['variable_name']. Will exit with an error if the variable
        is not contained in the class instance.
        '''
        try:
            return self.env_vars[var_name]
        except KeyError:
            sys.stderr.write('[FAIL] Attempt to access environment variable'
                             ' %s. This has not been loaded\n' %
                             var_name)
            sys.exit(ENV_LIB_ERROR)

    def __setitem__(self, var_name, value):
        '''
        Allow an environment variable to be added to the container by
        using the syntax LoadEnvar['variable_name'] = x.
        '''
        self.add(var_name, value)


def load_envar_apply_triggers(envar_definition):
    '''
    Apply any triggers to the namelist definition. Triggers can not be
    nested
    '''
    dummy_container = LoadEnvar()
    to_remove = []
    new_definition = copy.deepcopy(envar_definition)
    for variable, definition in envar_definition.items():
        if 'triggers' in definition:
            if 'default_val' in definition:
                dummy_container.load_envar(variable, definition['default_val'])
            else:
                dummy_container.load_envar(variable)
            for trigger in definition['triggers']:
                if not trigger[0](dummy_container[variable]):
                    to_remove += trigger[1]
    err_msg = ''
    for i_remove in to_remove:
        if 'triggers' in envar_definition[i_remove]:
            err_msg += 'Triggers cant be nested, look at variable %s\n' \
                      % i_remove
        new_definition.pop(i_remove)
    if err_msg:
        sys.stderr.write(err_msg)
        sys.exit(ENV_LIB_ERROR)
    else:
        return new_definition

def load_envar_check_dict(envar_definition):
    '''
    Check an environment variable definition and make sure the dictionary
    contains the correct itemas
    '''
    n_errors = 0
    for variable, definition in envar_definition.items():
        try:
            if not isinstance(definition['default_val'], (str, bool)):
                sys.stderr.write('[FAIL] default_val must be of type'
                                 ' string or boolean. For variable %s'
                                 ' it is %s\n' %
                                 (variable,
                                  type(definition['default_val'])))
                n_errors += 1
        except KeyError:
            pass
    if n_errors:
        sys.exit(ENV_LIB_ERROR)
    else:
        return 0


def load_envar_from_definition(envar_container, envar_definition):
    '''
    Load the environment variables from a dictionary definition. The
    definition dictionary contains the names of environment variables each
    with a subdictionary to define them. This contains
       'default_val' - Optional key containing the default value for
                       the environment variable should it be not set. Must
                       be string or boolean.
       'desc' - Optional a description of the contents of the variable
    '''
    # check that the definition is suitiable
    _ = load_envar_check_dict(envar_definition)
    envar_definition = load_envar_apply_triggers(envar_definition)
    n_errors = 0
    for variable, definition in envar_definition.items():
        if 'default_val' in definition:
            _ = envar_container.load_envar(variable, definition['default_val'])
        else:
            if envar_container.load_envar(variable) != 0:
                err_msg = '[FAIL] Environment variable %s%s not set\n' \
                          % (variable,
                             ' containing ' + definition['desc'] \
                             if 'desc' in definition else '')
                sys.stderr.write(err_msg)
                n_errors += 1
    if n_errors:
        sys.exit(ENV_LIB_ERROR)
    else:
        return envar_container


def set_continue_cont_from_fail(envar_container):
    '''
    The variables CONTINUE and CONTINUE_FROM_FAIL require modification
    to allow for running in climate and coupled NWP contexts.
    '''
    # Ensure that CONTINUE is always lower case false, unless explicitly
    # set to true (in which chase make sure it's lower case true
    if 't' in envar_container['CONTINUE'].lower():
        envar_container['CONTINUE'] = 'true'
    else:
        envar_container['CONTINUE'] = 'false'
    if 't' in envar_container['CONTINUE_FROM_FAIL'].lower():
        envar_container['CONTINUE_FROM_FAIL'] = 'true'
        # If continue from fail is true, then continue must also be true
        envar_container['CONTINUE'] = 'true'
    else:
        envar_container['CONTINUE_FROM_FAIL'] = 'false'
    return envar_container


def string_for_export(envinsts):
    '''
    Create a bash command to (re)export all the environmnet variables for
    all models. Takes a list of environment variable instances. Will fail
    if there are any duplicates
    '''
    envar_str = ''
    exported = []
    duplicates = set()
    for mod, inst in envinsts.items():
        for var, val in inst.env_vars.items():
            # If there is a space in the environment variable string and
            # it isn't already in quotes, we need to place it in quotes.
            # Note some environment variables may be unset currently
            if val:
                if val[0] not in ('\'', '\"') and ' ' in val:
                    val = "'%s'" % val
            envar_str += 'export %s=%s; ' % (var, val)
            if var in exported:
                duplicates.add(var)
            exported.append(var)
    duplicates = list(duplicates)
    if duplicates:
        msg = '\n[FAIL] The following environment variables have been set in' \
              ' more than one driver, please ensure this is not the case:\n' \
              '%s\n' % duplicates
        sys.stderr.write(msg)
        sys.exit(ENV_LIB_ERROR)

    return envar_str[:-1]
