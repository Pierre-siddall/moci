#!/usr/bin/env python
# -*- coding: utf-8 -*-
# *****************************COPYRIGHT******************************
# (C) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT.txt
# which you should have received as part of this distribution.
# *****************************COPYRIGHT******************************
"""This module contains small utility routines used by STASH printing
   and Importing macros"""

import re
import rose.config

# Define regexes to be used as part of the match_criteria.
# Pattern match for the namelists recognised as STASH namelists
IS_STASH_NL = re.compile(r'namelist:('
                         'umstash_streq\(\d{5}_[0-9a-f]+\)'
                         '|umstash_use\(\w+_[0-9a-f]+\)'
                         '|umstash_domain\(\w+_[0-9a-f]+\)'
                         '|umstash_time\(\w+_[0-9a-f]+\)'
                         '|nlstcall_pp\(\w+\)'
                         ')')
# Patterns to match individual STASH namelists
IS_STASH_STREQ_NL = re.compile(r'namelist:umstash_streq\(\d{5}_[0-9a-f]+\)')
IS_STASH_USAGE_NL = re.compile(r'namelist:umstash_use\(\w+_[0-9a-f]+\)')
IS_STASH_DOMAIN_NL = re.compile(r'namelist:umstash_domain\(\w+_[0-9a-f]+\)')
IS_STASH_TIME_NL = re.compile(r'namelist:umstash_time\(\w+_[0-9a-f]+\)')
IS_STASH_STREAM_NL = re.compile(r'namelist:nlstcall_pp\(\w+\)')

_INCLUDED_DICT = {"!": "No", "!!": "Nope"}


def filter_on_match(match_criteria, config):
    """Loop over a config node matching those nodes whose name match one of
       the supplied regexes in match_criteria, a list of tuples, and which
       contains a matching name,value pair.
       Return a config containing the matched nodes and a list of messages"""
    messages = []
    temp_config = rose.config.ConfigNode()
    for node_key, node in config.walk(no_ignore=False):
        # Skip top level info, looking only for config nodes (dictionaries)
        if not isinstance(node.value, dict):
            continue
        # Loop over criteria of interest.
        for regex, key, values in match_criteria:
            # If match found add node to new config
            if regex.match(node_key[0]):
                if ((key is None and values is None) or
                    node.value[key].value in values):
                    messages.append((node_key[0], None, None,
                                    '{0:s} will be added.'.format
                                     (node_key[0])))
                    temp_config.set(keys=node_key, value=node.value,
                                    state=node.state, comments=node.comments)
    return messages, temp_config


def merge_configs(target, donor):
    """Add the 'namelist' level config nodes from a donor config node object
       to the target one."""
    messages = []
    for node_key, node in donor.walk(no_ignore=False):
        if not isinstance(node.value, dict):
            continue

        messages.append((node_key[0], None, None,
                        '{0:s} will be added.'.format(node_key[0])))
        target.set(keys=node_key, value=node.value,
                   state=node.state, comments=node.comments)

    return messages, target


def delete_on_match(match_criteria, config):
    """Loop over a config matching nodes whose name matches one of the
       supplied regexes and which contains a matching name,value pair.
       Delete matching nodes and return the altered config"""
    messages = []
    for node_key, node in config.walk(no_ignore=False):
        # Skip top level info, looking only for config nodes (dictionaries)
        if not isinstance(node.value, dict):
            continue

        # Loop over criteria of interest.
        for regex, key, values in match_criteria:
            # If match found delete node from config
            if regex.match(node_key[0]):
                if ((key is None and values is None) or
                    node.value[key].value in values):
                    messages.append((node_key[0], None, None,
                                    '{0:s} will be deleted.'.format
                                     (node_key[0])))
                    config.unset(keys=[node_key[0]])

    return messages, config


def messages_to_reports(macro_obj, messages):
    """Turns and array of message tuples into rose macro reports"""
    for message in messages:
        macro_obj.add_report(message[0], message[1], message[2], message[3])
    return


def messages_to_screen(messages):
    """Turns and array of message tuples into screen output"""
    for message in messages:
        print " ".join(message)
    return


def profile_list_by_package(package_list, config):
    """Build a list of required STASH profiles based on user
       supplied list of package names."""
    domains = []
    times = []
    uses = []
    streams = []

    # Add enforced quotes to package names.
    packages = []
    if package_list is not None:
        for package in package_list.split(","):
            packages.append("'" + package + "'")

    # Find the STREQ profiles which match the supplied package names.
    for node_key, node in config.walk(no_ignore=False):
        # Skip top level info, looking only for config nodes (dictionaries)
        if not isinstance(node.value, dict):
            continue

        if IS_STASH_STREQ_NL.match(node_key[0]):
            if node.value["package"].value in packages:
                # Extract the required domain, time and usage profiles.
                for profile_list, marker in [[domains, "dom_name"],
                                             [times, "tim_name"],
                                             [uses, "use_name"]]:
                    if node.value[marker].value not in profile_list:
                        profile_list.append(node.value[marker].value)

    # Find the STREAM profiles which match those in the usage profiles
    for node_key, node in config.walk(no_ignore=False):
        # Skip top level info, looking only for config nodes (dictionaries)
        if not isinstance(node.value, dict):
            continue

        if IS_STASH_USAGE_NL.match(node_key[0]):
            if node.value["use_name"].value in uses:
                if node.value["file_id"].value not in streams:
                    streams.append(node.value["file_id"].value)

    # Setup search criteria and name/value pair lists for required profiles.
    list_to_find = [(IS_STASH_STREQ_NL, "package", packages),
                    (IS_STASH_STREAM_NL, "file_id", streams),
                    (IS_STASH_DOMAIN_NL, "dom_name", domains),
                    (IS_STASH_USAGE_NL, "use_name", uses),
                    (IS_STASH_TIME_NL, "tim_name", times)
                    ]
    return list_to_find


def debug_print_config(config, leader):
    '''Function to loop through a config node list printing out the basics
       for each node therein.'''
    for node_key, node in config.walk(no_ignore=False):
        if not isinstance(node.value, dict):
            continue

        debug_print_node(node, node_key, leader)
    return


def debug_print_node(node, node_key, leader):
    '''Function to print out the basic information (key value pairs)
       for a node.'''
    print leader + " ================================="
    print leader + " node_key = ", node_key[0]
    print leader + " ================================="
    for key in node.value.keys():
        section_node = node.value.get(key)
        print (leader + " key = {0:10s} value    = {1:15s}".format(
               key, section_node.value)
               + "state    = {0:10s}".format(section_node.state)
               + "comments = {0:10s}".format(section_node.comments))
    return
