#!/usr/bin/env python
# -*- coding: utf-8 -*-
# *****************************COPYRIGHT******************************
# (C) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT.txt
# which you should have received as part of this distribution.
# *****************************COPYRIGHT******************************
"""
This module contains code to Import and Export STASH related namelists
from UM rose-app.conf files and all optional configurations.
"""

import rose.macro
import rose.config
import os.path
import stash_handling_funcs as stash


class STASHExport(rose.macro.MacroBase):
    """Export all STASH profiles associated with a list of user
       supplied package names. The None response results in all STASH"""

    def transform(self, config, meta_config=None,
                  stash_export_filename='STASHexport.ini',
                  package_filters=None):
        """Build a list of required STASH profiles based on user
           supplied list of package names. Then copy those profiles to
           a new config and dump that to disk.
           Whilst this macro doesn't alter the config, it is a transform
           macro and not a validate one specifically so it doesn't get run
           by \"validate all\"."""

        self.reports = []

        if package_filters is not None:
            stuff_to_find = stash.profile_list_by_package(package_filters,
                                                          config)
        else:
            stuff_to_find = [(stash.IS_STASH_NL, None, None)]
            print "Exporting all STASH related profiles"
        messages, temp_config = stash.filter_on_match(stuff_to_find, config)
    
        rose.config.dump(temp_config, stash_export_filename)
    

        namelist_count = len(messages)
        print ("Exported {0:d} namelists related to STASH packages"
               " requested".format(namelist_count))

        return config, self.reports


class STASHImport(rose.macro.MacroBase):
    """Import additional STASH from a user specified UM rose-app.conf"""

    def transform(self, config, meta_config=None,
                  stash_donor_job="STASHImport.ini", package_filters=None):
        """Import STASH namelists from a file of ini/config format.
           Add loaded STASH to pre-existing STASH namelists in the current
           configuration"""

        self.reports = []

        # The macro will prompt the user for the path to donor config.
        donor_config = self.get_donor_config(stash_donor_job)
    
        # Find required profiles in donor file and copy to temp ConfigNode
        if package_filters is not None:
            stuff_to_find = stash.profile_list_by_package(package_filters,
                                                          donor_config)
            messages = []
        else:  # No user supplied pattern
            # Delete the existing STASH records.
            stuff_to_find = [(stash.IS_STASH_NL, None, None)]
            messages, config = stash.delete_on_match(stuff_to_find, config)
            # Set search to match all STASH records from the donor file.
            stuff_to_find = [(stash.IS_STASH_NL, None, None)]
            print "Importing all STASH related profiles"
        stash.messages_to_reports(self, messages)

        # Add STASH nodes from donor config to temp config
        messages, temp = stash.filter_on_match(stuff_to_find, donor_config)
    
        # Add temp config to main config
        messages, config = stash.merge_configs(config, temp)

        stash.messages_to_reports(self, messages)

        return config, self.reports


    def get_donor_config(self, filename_or_path):
        """If supplied a directory use it to construct a path to a
           rose-app.conf file therein.
           Otherwise assume path supplied is to the file to be used.
           Return a ConfigNode object of the loaded file"""
        donor_job_fullpath = os.path.realpath(filename_or_path)
        if os.path.isdir(donor_job_fullpath):
            donor_job_filename = os.path.join(donor_job_fullpath,
                                              "rose-app.conf")
        else:
            donor_job_filename = donor_job_fullpath
        # Load the donor rose-app config or other ini format file
        if os.path.exists(donor_job_filename):
            donor_config = rose.config.load(donor_job_filename)
        else:
            error_msg = ("Donor configuration : Not found at : \"{0:s}\"".format
                         (donor_job_filename))
            raise Exception(error_msg)
        return donor_config
