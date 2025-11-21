#!/usr/bin/env python3
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2021-2025 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
'''

import unittest
import unittest.mock as mock

import xios_driver
import dr_env_lib.env_lib

class TestCopyIodefCustom(unittest.TestCase):
    '''
    If there is a custom iodef file it needs to be copied to a name that is
    acceptable to XIOS'
    '''
    @mock.patch('xios_driver.shutil.copy')
    def test_no_custom(self, mock_copy):
        '''If there is no custom name, there are no files to copy'''
        xios_evar = {'IODEF_CUSTOM': '',
                     'IODEF_FILENAME': 'iodef.xml'}
        xios_driver._copy_iodef_custom(xios_evar)
        mock_copy.assert_not_called()

    @mock.patch('xios_driver.shutil.copy')
    def test_custom(self, mock_copy):
        '''If there is a custom name, we copy the file'''
        xios_evar = {'IODEF_CUSTOM': 'iodef_custom.xml',
                     'IODEF_FILENAME': 'iodef.xml'}
        xios_driver._copy_iodef_custom(xios_evar)
        mock_copy.assert_called_once_with('iodef_custom.xml', 'iodef.xml')


class TestSetupCouplingComponents(unittest.TestCase):
    '''
    Test the seting up of the coupling components pertaining to XIOS
    '''
    def test_nemo_only(self):
        '''Test the setting up for a nemo only run'''
        xios_envar = dr_env_lib.env_lib.LoadEnvar()
        xios_envar.add('COUPLING_COMPONENTS', 'um nemo')
        xios_envar.add('OTHER_ENVAR', 'value')
        oasis_components, xios_envar \
            = xios_driver._setup_coupling_components(xios_envar)
        self.assertIsInstance(xios_envar, dr_env_lib.env_lib.LoadEnvar)
        self.assertEqual(oasis_components, 'toyoce')
        self.assertEqual(xios_envar.env_vars, {'OTHER_ENVAR': 'value'})
        del xios_envar

    def test_lfric_nemo(self):
        '''Test the setting up for a lfric nemo run'''
        xios_envar = dr_env_lib.env_lib.LoadEnvar()
        xios_envar.add('COUPLING_COMPONENTS', 'nemo lfric')
        xios_envar.add('OTHER_ENVAR', 'value')
        oasis_components, xios_envar \
            = xios_driver._setup_coupling_components(xios_envar)
        self.assertIsInstance(xios_envar, dr_env_lib.env_lib.LoadEnvar)
        self.assertEqual(oasis_components, 'lfric,toyoce')
        self.assertEqual(xios_envar.env_vars, {'OTHER_ENVAR': 'value'})
        del xios_envar
