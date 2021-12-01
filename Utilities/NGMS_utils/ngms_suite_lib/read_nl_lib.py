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

Name:
  read_nl_lib.py

Description:
  File containing functions to manipulate rose-app.conf files, and also
  fortran namelists, either ones that are generated from these files or
  not.
'''

import re

class MultipleNameDictionary:
    '''
    A namelist can contain multiple instances of the same named namelist. To
    deal with them nicely in python we need to make sure they have an unique
    identifier internally. As we can have several groups of multiples with
    different names we need to account for this
    '''
    def __init__(self, mytype):
        '''
        Constructor for the object
        '''
        self.isnamelist = (mytype == 'namelist')
        self.dictionary_of_nls = {}
        self.initial_count_val = 1
        self.namelist_counter = {}

    def __iadd__(self, name_var_tuple):
        '''
        Override of the add function, takes in a tuple containing the
        namelist name and the variables within the namelist
        '''
        if self.isnamelist:
            self.add_namelist(name_var_tuple)
        else:
            self.add_non_namelist(name_var_tuple)
        return self

    def add_namelist(self, name_var_tuple):
        '''
        Add a namelist item, as this could have multiple entries
        '''
        name, variables = name_var_tuple
        if name in self.namelist_counter:
            i_name = '{}.{}'.format(name, self.namelist_counter[name])
            self.namelist_counter[name] += 1
        else:
            i_name = '{}'.format(name)
            self.namelist_counter[name] = self.initial_count_val
        self.dictionary_of_nls[i_name] = variables

    def add_non_namelist(self, name_var_tuple):
        '''
        Add a non namelist item, like a normal dictionary
        '''
        name, variables = name_var_tuple
        self.dictionary_of_nls[name] = variables

    def tidy_multiple(self):
        '''
        Remove any items from multiple items that are not multiple
        '''
        # We need the list to allow us to do the pop
        for key in list(self.namelist_counter.keys()):
            if self.namelist_counter[key] == 1:
                self.namelist_counter.pop(key)

    def zero_pad(self):
        '''
        Zeropad any multiple items
        '''
        singled_dict = {}
        for multiple_item in self.namelist_counter:
            # Minus 1 as we start at zero
            max_value = self.namelist_counter[multiple_item] - 1
            num_zeros = len(str(max_value))
            # we need the list as we change the size of the dictionary during
            # iteration
            for item in list(self.dictionary_of_nls.keys()):
                if multiple_item in item:
                    #print(item)
                    try:
                        name, number = item.split('.')
                    except ValueError:
                        name, number = (item, '0')
                    new_name = '{}.{}'.format(name, number.zfill(num_zeros))
                    singled_dict[new_name] = self.dictionary_of_nls.pop(item)
        return {**singled_dict, **self.dictionary_of_nls}

    def get_dir(self):
        '''
        Get the directory, and sort out the number of zeros in the unique
        identifiers to make it consistant
        '''
        if self.isnamelist:
            self.tidy_multiple()
            return self.zero_pad()
        return self.dictionary_of_nls

def is_array(test_line):
    '''
    Take in a variable that contains a comma, and work out if its a list, a
    string with a comma, or a list containing strings (with or without
    commas
    '''
    captured_variables = []
    capture_str = ''
    quotes = ('\"', '\'')
    quotes_open = False
    for i_char in test_line:
        if i_char in quotes:
            quotes_open = not quotes_open
        elif i_char == ',' and not quotes_open:
            captured_variables.append(capture_str)
            capture_str = ''
        elif i_char.isspace() and not quotes_open:
            pass
        else:
            capture_str += i_char
    # if there is only one variable, dont return a list, just the variable
    # itself
    if not captured_variables:
        return capture_str
    captured_variables.append(capture_str)
    return captured_variables

def get_item_name(val_type, type_linearray_0):
    '''
    Return the item name for the first element of a line array
    '''
    if val_type in ('file', 'namelist'):
        regex = r'\[(?:file|namelist):([\w\$\/\.]+(?:\(\w+\))?)\]'
        name = re.search(regex, type_linearray_0).group(1)
        return name
    return val_type

def read_variables_types(val_type, type_linearray):
    '''
    As the variables for command, namelist, or env are essentially all
    strings, these can be processed quite simply, we call out to test_vars
    function to do the formatting of namelists
    '''
    item_name = get_item_name(val_type, type_linearray[0])
    variables = {}
    for line in type_linearray[1:]:
        var_name = line.split('=')[0]
        var_string = line.split('=')[1]
        if val_type == 'namelist':
            # Format our namelist variables into python types
            if ',' in var_string:
                #this could be an array, could be a string containing a
                #comma, or an array containing strings that may or may
                #not contain commas
                var_value = is_array(var_string)
                if isinstance(var_value, list):
                    var_value = list(map(test_vars, var_string.split(',')))
                else:
                    var_value = test_vars(var_string)
            else:
                var_value = test_vars(var_string)
        else:
            var_value = var_string
        variables[var_name] = var_value
    return item_name, variables

def test_vars(var_string):
    '''
    Takes in namelist variables and turns them into something useful that
    can be manipulated by python, (booleans, empty variables, strings in
    single or doublee quotes, floating points, and integers
    '''
    if '.true.' in var_string.lower():
        return True
    if '.false.' in var_string.lower():
        return False
    if not var_string:
        # Empty variable
        return None
    # the code below determines if the variable is an integer
    # a float, or a string. A string may be enclosed in single
    # or double quotes
    if var_string[0] in ('\'', '\"'):
        #strip the unncessesary quotes
        return var_string[1:-1]
    try:
        if '.' in var_string:
            return float(var_string)
        return int(var_string)
    except ValueError:
        return var_string

def variable_dict(mytype, typelist):
    '''
    Take in a string representing one of the types, source, env, namelist or
    file, and iterate through the variables returning a dictionary
    '''
    variable_dictionary = MultipleNameDictionary(mytype)
    for item in typelist:
        variable_dictionary += read_variables_types(mytype, item)
    return_dict = variable_dictionary.get_dir()
    # A bit of formatting to make command and env types a bit easier to
    # deal with, as they cant have multiple entries
    if mytype in ('command', 'env'):
        return return_dict[mytype]
    return return_dict
