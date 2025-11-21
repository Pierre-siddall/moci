#!/usr/bin/env python3
'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2020-2025 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
'''

import unittest
try:
    # mock is integrated into unittest as of Python 3.3
    import unittest.mock as mock
except ImportError:
    # mock is a standalone package (back-ported)
    import mock
import io
import mct_validate

# testing paramaters for function calls
UM_TS_800 = 800
UM_TS_1000 = 1000
UM_TS_1200 = 1200
UM_TS_1500 = 1500
UM_TS_1600 = 1600
UM_TS_4800 = 4800
NEMO_TS_1200 = 1200
NEMO_TS_1500 = 1500
NEMO_TS_3600 = 3600

class TestUtilityFns(unittest.TestCase):
    '''
    Test standalone functions that provide common utilities
    '''
    def test_to_seconds_zero(self):
        '''
        Zero hours, minutes and seconds
        '''
        self.assertEqual(mct_validate.to_seconds(0, 0, 0), 0)

    def test_to_seconds_secs(self):
        '''
        30 seconds
        '''
        self.assertEqual(mct_validate.to_seconds(0, 0, 30), 30)

    def test_to_seconds_mins(self):
        '''
        2 minutes is 120 seconds
        '''
        self.assertEqual(mct_validate.to_seconds(0, 2, 0), 120)

    def test_to_seconds_hours(self):
        '''
        2 hours is 7200 seconds
        '''
        self.assertEqual(mct_validate.to_seconds(2, 0, 0), 7200)

    def test_to_seconds_all(self):
        '''
        1 hour, 1 minute and 1 second is 3661 seconds
        '''
        self.assertEqual(mct_validate.to_seconds(1, 1, 1), 3661)


class TestNamCouple(unittest.TestCase):
    '''
    Test reading of the Oasis3-MCT namcouple file
    '''

    def setUp(self):
        '''
        Set up a sample of a correct and a broken namcouple file
        '''
        self.read_data = '# TRANSDEF: OCNT ATMT 1 25  #####\n' \
                         ' model01_O_SSTSST ocn_sst 1 3600 1 atmos_restart.nc' \
                         '  EXPORTED\n' \
                         '1442 1207 192 144  tor1 atm3 SEQ=+1\n' \
                         ' P  2  P 0\n' \
                         '#\n' \
                         ' MAPPING\n' \
                         '#\n' \
                         ' rmp_tor1_to_atm3_CONSERV_FRACAREA_1st.nc\n' \
                         '#\n' \
                         '# TRANSDEF: ATMT OCNT 56 22 2 #####\n' \
                         ' sublim05 model01_OIceEvp_cat05 472 3600 1 ' \
                         'atmos_restart.nc   EXPORTED\n' \
                         '192 144 1442 1207  atm3 tor1 SEQ=+2\n' \
                         ' P  0  P  2\n' \
                         '#\n' \
                         ' MAPPING\n' \
                         '#\n' \
                         ' rmp_atm3_to_tor1_CONSERV_DESTAREA_2nd.nc\n' \
                         '#\n'

        self.read_mangled = '# TRANSDEF: OCNT ATMT 1 25  #####\n' \
                            ' model01_O_SSTSST ocn_sst 1 3600 1' \
                            ' atmos_restart.nc  EXPORTED\n' \
                            '1442 1207 192 144  tor1 atm3 SEQ=+1\n' \
                            ' P  2  P 0\n' \
                            '#\n' \
                            ' MAPPING\n' \
                            '#\n' \
                            ' rmp_tor1_to_atm3_CONSERV_FRACAREA_1st.nc\n' \
                            '#\n' \
                            '# TRANSDEF: OCNT ATMT 1 25  #####\n' \
                            ' wrong_src wrong_dest 1 3600 1' \
                            ' atmos_restart.nc  EXPORTED\n' \
                            '1442 1207 192 144  tor1 bad_grid SEQ=+1\n' \
                            ' P  2  P 0\n' \
                            '#\n' \
                            ' MAPPING\n' \
                            '\n' \
                            ' rmp_tor1_to_atm3_CONSERV_FRACAREA_1st.nc\n' \
                            '#\n' \

    def test_get_coupling_fields_namcouple(self):
        '''
        Check we are trying to read the namecouple file
        '''
        with mock.patch("builtins.open",
                        mock.mock_open(read_data=self.read_data)) as mock_file:
            _ = mct_validate.get_coupling_fields()
            mock_file.assert_called_with('namcouple', 'r')

    def test_get_coupling_fields(self):
        '''
        Test the reading of sucessful NAMCOUPLE fields
        '''
        expected_output = {'a2o': [{'src_field': 'sublim05',
                                    'freq_s': 3600,
                                    'dest_field': 'model01_OIceEvp_cat05'}],
                           'o2a': [{'src_field': 'model01_O_SSTSST',
                                    'freq_s': 3600,
                                    'dest_field': 'ocn_sst'}]}
        with mock.patch("builtins.open",
                        mock.mock_open(read_data=self.read_data)):
            self.assertEqual(mct_validate.get_coupling_fields(),
                             expected_output)

    def test_get_coupling_fields_bad_input(self):
        '''
        Test the reading of namcouple if an atmosphere grid is unable to be
        identified
        '''
        expected_output = {'a2o': [],
                           'o2a': [{'src_field': 'model01_O_SSTSST',
                                    'freq_s': 3600,
                                    'dest_field': 'ocn_sst'}]}
        expected_err = 'Can not determine source and destination for' \
                       ' field wrong_src\n'
        with mock.patch("builtins.open",
                        mock.mock_open(read_data=self.read_mangled)):
            with mock.patch("sys.stderr", new=io.StringIO()) as fake_err:
                rvalue = (mct_validate.get_coupling_fields())
                self.assertEqual(fake_err.getvalue(), expected_err)
                self.assertEqual(rvalue, expected_output)


class TestCompareUmToNamcouple(unittest.TestCase):
    '''
    Compare the coupling frequencies in the UM to those from the namcouple
    file
    '''

    def test_valid(self):
        '''
        Test a match
        '''
        um_freq_in = {'a2o': 3600.0, 'o2a': 3600.0}
        namcouple_in = {'a2o': [{'src_field': 'sublim05',
                                 'freq_s': 3600,
                                 'dest_field': 'model01_OIceEvp_cat05'},
                                {'src_field': 'sublim04',
                                 'freq_s': 3600,
                                 'dest_field': 'model01_OIceEvp_cat04'}],
                        'o2a': [{'src_field': 'model01_O_SSTSST',
                                 'freq_s': 3600,
                                 'dest_field': 'ocn_sst'}]}
        expected_rvalue = 0
        self.assertEqual(mct_validate.check_um_vs_namcouple(um_freq_in,
                                                            namcouple_in),
                         expected_rvalue)

    def test_invalid(self):
        '''
        Test incorrect a2o and correct o2a
        '''
        um_freq_in = {'a2o': 3600.0, 'o2a': 3600.0}
        namcouple_in = {'a2o': [{'src_field': 'sublim05',
                                 'freq_s': 3600,
                                 'dest_field': 'model01_OIceEvp_cat05'},
                                {'src_field': 'wrong_field',
                                 'freq_s': 1800,
                                 'dest_field': 'model01_OIceEvp_cat04'}],
                        'o2a': [{'src_field': 'model01_O_SSTSST',
                                 'freq_s': 3600,
                                 'dest_field': 'ocn_sst'}]}
        expected_rvalue = 1
        expected_err = 'Source field wrong_field in direction a2o:\n' \
                       '  UM expects coupling frequency to be 3600\n' \
                       '  namcouple expects frequency to be 1800\n\n'
        with mock.patch("sys.stderr", new=io.StringIO()) as fake_err:
            rvalue = mct_validate.check_um_vs_namcouple(um_freq_in,
                                                        namcouple_in)
            self.assertEqual(fake_err.getvalue(), expected_err)
            self.assertEqual(rvalue, expected_rvalue)


class TestCheckTimestepChoice(unittest.TestCase):
    '''
    Check the coupling timesteps match river routing and model timesteps
    '''

    def setUp(self):
        '''
        Valid (no rr), Valid (inc rr) and Invalid frequency dictionaries
        '''
        self.um_freq_in = {'a2o': 3600.0, 'o2a': 2400.}
        self.um_freq_in_rr = {'a2o': 3600.0, 'o2a': 2400., 'rr': 3600.}
        self.um_freq_in_invalid_rr = {'a2o': 3600.0, 'o2a': 2400., 'rr': 2400.}

    def test_check_valid_no_rr(self):
        '''
        Check with valid timesteps on both components
        '''
        expected_rvalue = 0
        rvalue = mct_validate.check_timestep_choice(self.um_freq_in,
                                                    UM_TS_1200, NEMO_TS_1200)
        self.assertEqual(rvalue, expected_rvalue)

    def test_check_invalid_um_no_rr(self):
        '''
        Check with valid timestep on nemo, invalid on um
        '''
        expected_err = 'Atmosphere timestemps must be an exact divisor of' \
                       ' Atmosphere -> Ocean coupling timesteps:\n' \
                       '  Atmos timestep 1500 s\n' \
                       '  Coupling timestep 3600 s\n\n'
        expected_rvalue = 1
        with mock.patch("sys.stderr", new=io.StringIO()) as fake_err:
            rvalue = mct_validate.check_timestep_choice(self.um_freq_in,
                                                        UM_TS_1500,
                                                        NEMO_TS_1200)
            self.assertEqual(fake_err.getvalue(), expected_err)
            self.assertEqual(rvalue, expected_rvalue)

    def test_check_invalid_ocean_no_rr(self):
        '''
        Check with valid timestep on um, invalid on nemo
        '''
        expected_err = 'Ocean timesteps must be an exact divisor of Ocean ->' \
                       ' Atmosphere coupling timesteps:\n' \
                       '  Ocean timestep 1500 s\n' \
                       '  Coupling timestep 2400 s\n\n'
        expected_rvalue = 1
        with mock.patch("sys.stderr", new=io.StringIO()) as fake_err:
            rvalue = mct_validate.check_timestep_choice(self.um_freq_in,
                                                        UM_TS_1200,
                                                        NEMO_TS_1500)
            self.assertEqual(fake_err.getvalue(), expected_err)
            self.assertEqual(rvalue, expected_rvalue)

    def test_check_both_invalid_no_rr(self):
        '''
        Check if both are invalid, with a model timestep that is
        longer than the coupling frequency
        '''
        expected_err = 'Atmosphere timestemps must be an exact divisor of' \
                       ' Atmosphere -> Ocean coupling timesteps:\n' \
                       '  Atmos timestep 4800 s\n' \
                       '  Coupling timestep 3600 s\n\n' \
                       'Ocean timesteps must be an exact divisor of Ocean ->' \
                       ' Atmosphere coupling timesteps:\n' \
                       '  Ocean timestep 3600 s\n' \
                       '  Coupling timestep 2400 s\n\n'
        expected_rvalue = 1
        with mock.patch("sys.stderr", new=io.StringIO()) as fake_err:
            rvalue = mct_validate.check_timestep_choice(self.um_freq_in,
                                                        UM_TS_4800,
                                                        NEMO_TS_3600)
            self.assertEqual(fake_err.getvalue(), expected_err)
            self.assertEqual(rvalue, expected_rvalue)

    def test_check_valid_with_rr(self):
        '''
        Check with valid timesteps on both components, and valid river routing
        '''
        expected_rvalue = 0
        rvalue = mct_validate.check_timestep_choice(self.um_freq_in_rr,
                                                    UM_TS_1200, NEMO_TS_1200)
        self.assertEqual(rvalue, expected_rvalue)

    def test_check_with_invalid_rr(self):
        '''
        Check with valid timesteps on both components and invalid river routing
        '''
        expected_err = 'River routing coupling and Atmosphere ->' \
                       ' Ocean coupling frequencies must be identical:\n' \
                       '  Atmosphere coupling every 3600 s\n' \
                       '  River routing every 2400 s\n'
        expected_rvalue = 1
        with mock.patch("sys.stderr", new=io.StringIO()) as fake_err:
            rvalue = mct_validate.check_timestep_choice(
                self.um_freq_in_invalid_rr, UM_TS_1200, NEMO_TS_1200)
            self.assertEqual(fake_err.getvalue(), expected_err)
            self.assertEqual(rvalue, expected_rvalue)



class TestReadUMCouplingFreq(unittest.TestCase):
    '''
    Test the reading of couplinf frequencies of the UM from shared namelist
    '''
    def setUp(self):
        '''
        Sample SHARED namelist
        '''
        self.read_data = '&coupling_control\n' \
                         'l_oasis_wave=.false.,\n' \
                         'oasis_couple_freq_ao=1,0,\n' \
                         'oasis_couple_freq_aw=0,0,\n' \
                         'oasis_couple_freq_oa=1,0,\n' \
                         '/\n' \
                         '&model_domain\n' \
                         'l_regular=.true.,\n' \
                         'model_type=1,\n' \
                         '/\n'

        self.read_data_rr = '%s' \
                            '&jules_rivers\n' \
                            'nstep_rivers=3,\n' \
                            '/\n' % self.read_data

    def test_get_um_ocean_coupling_freq_namelist(self):
        '''
        Check we are trying to read the SHARED namelist
        '''
        with mock.patch("builtins.open",
                        mock.mock_open(read_data=self.read_data)) as mock_file:
            _ = mct_validate.get_um_ocean_coupling_freq()
            mock_file.assert_called_with('SHARED', 'r')

    def test_get_um_ocean_coupling_freq_no_river_routing(self):
        '''
        Test the reading of what the UM thinks the coupling frequency should
        be
        '''
        expected_output = {'a2o': 3600, 'o2a': 3600}
        with mock.patch("builtins.open",
                        mock.mock_open(read_data=self.read_data)):
            self.assertEqual(mct_validate.get_um_ocean_coupling_freq(),
                             expected_output)

    def test_get_um_ocean_coupling_freq_with_river_routing(self):
        '''
        Test the reading of what the UM thinks the coupling frequency should
        be, and when the river routing happens
        '''
        expected_output = {'a2o': 3600, 'o2a': 3600, 'rr': 3600}
        with mock.patch("builtins.open",
                        mock.mock_open(read_data=self.read_data_rr)):
            self.assertEqual(mct_validate.get_um_ocean_coupling_freq(
                UM_TS_1200), expected_output)


class TestVerifyStashProfiles(unittest.TestCase):

    '''
    In all cases um timestep is 1200s, coupling frequency is 3600s
    '''

    def setUp(self):
        self.um_ts = 1200
        self.couple_freq = 3600

        self.valid_mean = {'tim_name': 'VALID_MEAN', 'offset': 0, 'freq': 3600,
                           'type': 'timemean'}
        self.valid_inst = {'tim_name': 'VALID_INST', 'start': 2400,
                           'freq': 3600, 'type': 'instantaneous'}
        self.invalid_mean_offset = {'tim_name': 'WRONG_MEAN', 'offset': 1200,
                                    'freq': 3600, 'type': 'timemean'}
        self.invalid_mean_freq = {'tim_name': 'WRONG_MEAN', 'offset': 0,
                                  'freq': 2400, 'type': 'timemean'}
        self.invalid_inst_start = {'tim_name': 'WRONG_INST', 'start': 3600,
                                   'freq': 3600, 'type': 'instantaneous'}

    def test_valid_timemean(self):
        '''
        Valid mean profile
        '''
        expected_rcode = 0
        self.assertEqual(mct_validate.verify_stash_profiles(
            [self.valid_mean], self.couple_freq, self.um_ts), expected_rcode)

    def test_valid_inst(self):
        '''
        Valid river routing instantaneous profile
        '''
        expected_rcode = 0
        self.assertEqual(mct_validate.verify_stash_profiles(
            [self.valid_inst], self.couple_freq, self.um_ts), expected_rcode)

    def test_invalid_mean_offset(self):
        '''
        Non zero mean offset
        '''
        expected_rcode = 1
        expected_err = 'Timemean profile WRONG_MEAN not valid. Should have' \
                       ' an offset of zero\n  offset 1200 s\n\n'
        with mock.patch("sys.stderr", new=io.StringIO()) as fake_err:
            rcode = mct_validate.verify_stash_profiles(
                [self.invalid_mean_offset], self.couple_freq, self.um_ts)
            self.assertEqual(fake_err.getvalue(), expected_err)
            self.assertEqual(rcode, expected_rcode)

    def test_invalid_mean_freq(self):
        '''
        Stash mean frequency not equal to coupling frequency
        '''
        expected_rcode = 1
        expected_err = 'Time profile WRONG_MEAN not valid. Needs to have a' \
                       ' frequency identical to UM coupling frequency\n' \
                       '  coupling frequency 3600 s\n' \
                       '  stash profile frequency 2400 s\n\n'
        with mock.patch("sys.stderr", new=io.StringIO()) as fake_err:
            rcode = mct_validate.verify_stash_profiles(
                [self.invalid_mean_freq], self.couple_freq, self.um_ts)
            self.assertEqual(fake_err.getvalue(), expected_err)
            self.assertEqual(rcode, expected_rcode)

    def test_invalid_inst_start(self):
        '''
        Test the instantaneous stash with a start time equal to the coupling
        frequency
        '''
        expected_rcode = 1
        expected_err = 'Instantaneous (river routing) profile WRONG_INST not' \
                       ' valid. Should start on the timestep before the first' \
                       ' coupling timestep\n' \
                       '  Expected value 2400 s\n' \
                       '  Actual value 3600 s\n\n'
        with mock.patch("sys.stderr", new=io.StringIO()) as fake_err:
            rcode = mct_validate.verify_stash_profiles(
                [self.invalid_inst_start], self.couple_freq, self.um_ts)
            self.assertEqual(fake_err.getvalue(), expected_err)
            self.assertEqual(rcode, expected_rcode)

    def test_multiple_correct(self):
        '''
        Test two correct profiles
        '''
        expected_rcode = 0
        self.assertEqual(mct_validate.verify_stash_profiles(
            [self.valid_inst, self.valid_mean], self.couple_freq, self.um_ts),
                         expected_rcode)

    def test_correct_and_error(self):
        '''
        Test two correct and one incorrect stash profiles
        '''
        expected_rcode = 1
        expected_err = 'Timemean profile WRONG_MEAN not valid. Should have' \
                       ' an offset of zero\n  offset 1200 s\n\n'
        with mock.patch("sys.stderr", new=io.StringIO()) as fake_err:
            rcode = mct_validate.verify_stash_profiles(
                [self.valid_mean, self.invalid_mean_offset, self.valid_inst],
                self.couple_freq, self.um_ts)
            self.assertEqual(fake_err.getvalue(), expected_err)
            self.assertEqual(rcode, expected_rcode)


class TestHumanReadableStash(unittest.TestCase):
    '''
    Test the turning of stash namlist dictionaries into dictionaries with
    additional human readable components
    '''
    def setUp(self):

        self.wrong_profile = {'iend': -1, 'ifre': 3, 'iopt': 1, 'istr': 2,
                              'ityp': 4, 'tim_name': 'WRONG', 'unt3': 1}
        self.inst_profile = {'iend': -1, 'ifre': 3, 'iopt': 1, 'istr': 2,
                             'ityp': 1, 'tim_name': 'TCOUP', 'unt3': 1}
        self.mean_profile = {'iend': -1, 'ifre': 1, 'intv': 1, 'ioff': 0,
                             'iopt': 1, 'isam': 1, 'istr': 1, 'ityp': 3,
                             'tim_name': 'TCOUPMN', 'unt1': 2, 'unt2': 1,
                             'unt3': 2}


    def test_wrong_itype(self):
        '''
        Timestep 1200s
        '''
        expected_err = 'Unable to validate stash type (ityp) 4\n'
        with mock.patch("sys.stderr", new=io.StringIO()) as fake_err:
            output = mct_validate.human_readable_stash([self.wrong_profile],
                                                       UM_TS_1200)
            self.assertEqual(fake_err.getvalue(), expected_err)
            self.assertEqual(output, [])

    def test_instantaneous_type(self):
        '''
        Timestep 1600s
        '''
        out_profile = [{'iend': -1, 'ifre': 3, 'iopt': 1, 'istr': 2,
                        'ityp': 1, 'tim_name': 'TCOUP', 'unt3': 1,
                        'type': 'instantaneous', 'start': 3200, 'freq': 4800}]
        out = mct_validate.human_readable_stash([self.inst_profile], UM_TS_1600)
        self.assertEqual(out, out_profile)

    def test_mean_type_nooffset(self):
        '''
        Timestep 800s
        '''
        out_profile = [{'iend': -1, 'ifre': 1, 'intv': 1, 'ioff': 0,
                        'iopt': 1, 'isam': 1, 'istr': 1, 'ityp': 3,
                        'tim_name': 'TCOUPMN', 'unt1': 2, 'unt2': 1,
                        'unt3': 2, 'type': 'timemean', 'freq': 3600,
                        'offset' :0}]
        out = mct_validate.human_readable_stash([self.mean_profile], UM_TS_800)
        self.assertEqual(out, out_profile)

    def test_mean_type_offset(self):
        '''
        Timestep 800s, two timestep offset
        '''
        mean_profile = {'iend': -1, 'ifre': 1, 'intv': 1, 'ioff': 2,
                        'iopt': 1, 'isam': 1, 'istr': 1, 'ityp': 3,
                        'tim_name': 'TCOUPMN', 'unt1': 2, 'unt2': 1,
                        'unt3': 2}
        out_profile = [{'iend': -1, 'ifre': 1, 'intv': 1, 'ioff': 2,
                        'iopt': 1, 'isam': 1, 'istr': 1, 'ityp': 3,
                        'tim_name': 'TCOUPMN', 'unt1': 2, 'unt2': 1,
                        'unt3': 2, 'type': 'timemean', 'freq': 3600,
                        'offset': 1600}]
        out = mct_validate.human_readable_stash([mean_profile], UM_TS_800)
        self.assertEqual(out, out_profile)

    def test_multiple(self):
        '''
        Timestep 1200s
        '''
        in_profiles = [self.inst_profile, self.mean_profile,
                       self.wrong_profile, self.inst_profile]
        expected_out = [
            {'iend': -1, 'ifre': 3, 'iopt': 1, 'istr': 2, 'ityp': 1,
             'tim_name': 'TCOUP', 'unt3': 1, 'type': 'instantaneous',
             'start': 2400, 'freq': 3600},
            {'iend': -1, 'ifre': 1, 'intv': 1, 'ioff': 0, 'iopt': 1,
             'isam': 1, 'istr': 1, 'ityp': 3, 'tim_name': 'TCOUPMN',
             'unt1': 2, 'unt2': 1, 'unt3': 2, 'type': 'timemean', 'freq': 3600,
             'offset': 0},
            {'iend': -1, 'ifre': 3, 'iopt': 1, 'istr': 2, 'ityp': 1,
             'tim_name': 'TCOUP', 'unt3': 1, 'type': 'instantaneous',
             'start': 2400, 'freq': 3600}]
        expected_err = 'Unable to validate stash type (ityp) 4\n'
        with mock.patch("sys.stderr", new=io.StringIO()) as fake_err:
            output = mct_validate.human_readable_stash(in_profiles, UM_TS_1200)
            self.assertEqual(fake_err.getvalue(), expected_err)
            self.assertEqual(output, expected_out)

    def test_meaning_units(self):
        '''
        Test the units for meaning_freq, timestep = 800s
        '''
        in_profile = {'ityp': 3, 'intv': 1, 'ioff': 1, 'unt2': 1}
        unt1_opts = [1, 2, 3, 5, 6]
        frequency_outs = [800, 3600, 86400, 60, 1]
        for i_unt1, expected_freq in zip(unt1_opts, frequency_outs):
            in_profile['unt1'] = i_unt1
            out = mct_validate.human_readable_stash([in_profile], UM_TS_800)
            self.assertEqual(out[0]['freq'], expected_freq)

    def test_meaning_offset_units(self):
        '''
        Test the units for the offset for meaning frequency, timestep = 800
        '''
        in_profile = {'ityp': 3, 'intv': 1, 'ioff': 2, 'unt1': 6}
        unt2_opts = [1, 2, 3, 5, 6]
        offset_outs = [1600, 7200, 172800, 120, 2]
        for i_unt2, expected_offset in zip(unt2_opts, offset_outs):
            in_profile['unt2'] = i_unt2
            out = mct_validate.human_readable_stash([in_profile], UM_TS_800)
            self.assertEqual(out[0]['offset'], expected_offset)

    def test_instantaneous_units(self):
        '''
        Test the units for instantaneous time profiles, timestep = 1000
        '''
        in_profile = {'ityp': 1, 'iopt': 1, 'istr': 2, 'ifre': 3}
        unt3_opts = [1, 2, 3, 5, 6]
        frequency_outs = [3000, 10800, 259200, 180, 3]
        start_outs = [2000, 7200, 172800, 120, 2]
        for i_unt3, expected_freq, expected_start in zip(unt3_opts,
                                                         frequency_outs,
                                                         start_outs):
            in_profile['unt3'] = i_unt3
            out = mct_validate.human_readable_stash([in_profile], UM_TS_1000)
            self.assertEqual(out[0]['freq'], expected_freq)
            self.assertEqual(out[0]['start'], expected_start)


class TestReadUmTs(unittest.TestCase):
    '''
    Test the reading of UM timestep from ATMOSCNTL namelist
    '''
    def setUp(self):

        self.read_data = '&configid\n' \
                         '/\n' \
                         '&nlstcgen\n' \
                         'i_dump_output=2,\n' \
                         'l_meaning_sequence=.false.,\n' \
                         'secs_per_periodim=86400,\n' \
                         'steps_per_periodim=72,\n' \
                         '/\n'

    def test_get_um_ts_namelist(self):
        '''
        Check we are trying to read the ATMOSCNTL namelist
        '''
        with mock.patch("builtins.open",
                        mock.mock_open(read_data=self.read_data)) as mock_file:
            _ = mct_validate.get_um_ts()
            mock_file.assert_called_with('ATMOSCNTL', 'r')

    def test_get_um_ts(self):
        '''
        Test the reading of what the UM thinks its timestep length should be
        '''
        expected_output = 1200.0
        with mock.patch("builtins.open",
                        mock.mock_open(read_data=self.read_data)):
            self.assertEqual(mct_validate.get_um_ts(), expected_output)


class TestReadCouplingInformationNEMO(unittest.TestCase):
    '''
    Test the reading of information from NEMO namelist_cfg
    '''
    def setUp(self):

        self.read_data = '&namdom\n' \
                         'jphgr_msh=0,\n' \
                         'ldbletanh=.true.,\n' \
                         'rn_rdt=1200.0,\n' \
                         '/\n' \
                         '&namrun\n' \
                         'cn_exp=\'bm897o\'\n,' \
                         'cn_ocerst_in=\'restart\'\n,'

    def test_get_nemo_ts_namelist(self):
        '''
        Check we are trying to read the namelist_cfg namelist
        '''
        with mock.patch("builtins.open",
                        mock.mock_open(read_data=self.read_data)) as mock_file:
            _ = mct_validate.get_nemo_ts()
            mock_file.assert_called_with('namelist_cfg', 'r')

    def test_get_nemo_ts(self):
        '''
        Test the reading of the timestep from rn_rdt variable
        '''
        expected_output = 1200.0
        with mock.patch("builtins.open",
                        mock.mock_open(read_data=self.read_data)):
            self.assertEqual(mct_validate.get_nemo_ts(), expected_output)


class TestReadCouplingProfilesUM(unittest.TestCase):
    '''
    Test the reading of UM stash time profiles from STASHC namelist
    '''
    def setUp(self):

        self.read_data = '&umstash_streq\n' \
                         'dom_name=\'DIAG\',\n' \
                         'isec=5,\n' \
                         'item=206,\n' \
                         'package=\'Dump Mean Diagnostics\',\n' \
                         'tim_name=\'TMONMN\',\n' \
                         'use_name=\'UPM\',\n' \
                         '/\n' \
                         '&umstash_time\n' \
                         'iend=-1,\n' \
                         'ifre=3,\n' \
                         'iopt=1,\n' \
                         'istr=2,\n' \
                         'ityp=1,\n' \
                         'tim_name=\'TCOUP\',\n' \
                         'unt3=1,\n' \
                         '/\n' \
                         '&umstash_time\n' \
                         'iend=-1,\n' \
                         'ifre=1,\n' \
                         'intv=1,\n' \
                         'ioff=0,\n' \
                         'iopt=1,\n' \
                         'isam=1,\n' \
                         'istr=1,\n' \
                         'ityp=3,\n' \
                         'tim_name=\'TCOUPMN\',\n' \
                         'unt1=2,\n' \
                         'unt2=1,\n' \
                         'unt3=2,\n' \
                         '/\n' \
                         '&umstash_time\n' \
                         'iend=-1,\n' \
                         'ifre=1,\n' \
                         'intv=1,\n' \
                         'ioff=0,\n' \
                         'iopt=1,\n' \
                         'isam=1,\n' \
                         'istr=1,\n' \
                         'ityp=3,\n' \
                         'tim_name=\'TDAYM\',\n' \
                         'unt1=3,\n' \
                         'unt2=1,\n' \
                         'unt3=3,\n' \
                         '/n'

    def test_get_coupling_timeprofiles_strs_namelist(self):
        '''
        Check we are trying to read the STASHC namelist
        '''
        with mock.patch("builtins.open",
                        mock.mock_open(read_data=self.read_data)) as mock_file:
            _ = mct_validate.get_coupling_timeprofiles_strs()
            mock_file.assert_called_with('STASHC', 'r')

    def test_get_coupling_timeprofiles_strs(self):
        '''
        Check we can read the time profiles for coupling correctly
        '''
        expected_output = [
            ['&umstash_time\n', 'iend=-1,\n', 'ifre=3,\n', 'iopt=1,\n', \
             'istr=2,\n', 'ityp=1,\n', 'tim_name=\'TCOUP\',\n', 'unt3=1,\n'],
            ['&umstash_time\n', 'iend=-1,\n', 'ifre=1,\n', 'intv=1,\n', \
             'ioff=0,\n', 'iopt=1,\n', 'isam=1,\n', 'istr=1,\n', 'ityp=3,\n', \
             'tim_name=\'TCOUPMN\',\n', 'unt1=2,\n', 'unt2=1,\n', 'unt3=2,\n']]
        with mock.patch("builtins.open",
                        mock.mock_open(read_data=self.read_data)):
            self.assertEqual(mct_validate.get_coupling_timeprofiles_strs(),
                             expected_output)

    def test_timeprofiles_str_2_dict(self):
        '''
        Test correct construction of timeprofile dictionaries
        '''
        input_strings = [
            ['&umstash_time\n', 'iend=-1,\n', 'ifre=3,\n', 'iopt=1,\n', \
             'istr=2,\n', 'ityp=1,\n', 'tim_name=\'TCOUP\',\n', 'unt3=1,\n'],
            ['&umstash_time\n', 'iend=-1,\n', 'ifre=1,\n', 'intv=1,\n', \
             'ioff=0,\n', 'iopt=1,\n', 'isam=1,\n', 'istr=1,\n', 'ityp=3,\n', \
             'tim_name=\'TCOUPMN\',\n', 'unt1=2,\n', 'unt2=1,\n', 'unt3=2,\n']]
        expected_output = [{'iend': -1, 'ifre': 3, 'iopt': 1, 'istr': 2,
                            'ityp': 1, 'tim_name': 'TCOUP', 'unt3': 1},
                           {'iend': -1, 'ifre': 1, 'intv': 1, 'ioff': 0,
                            'iopt': 1, 'isam': 1, 'istr': 1, 'ityp': 3,
                            'tim_name': 'TCOUPMN', 'unt1': 2, 'unt2': 1,
                            'unt3': 2}]
        self.assertEqual(mct_validate.timeprofiles_str_2_dict(input_strings),
                         expected_output)

class TestFinalise(unittest.TestCase):
    '''
    Test the script will return the appropriate error code
    '''
    def test_success(self):
        '''
        Test a successful completion
        '''
        expected_out = 'This coupling configuration has been successfully' \
                       ' validated\n'
        with mock.patch("sys.stdout", new=io.StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as error_context:
                mct_validate.finalise(0)
            self.assertEqual(fake_out.getvalue(), expected_out)
            self.assertEqual(error_context.exception.code, 0)

    def test_fail(self):
        '''
        Test a failed completion with error code 3
        '''
        expected_out = 'This coupling configuration has problems in its' \
                       ' validation. Please see stderr for details\n'
        with mock.patch("sys.stdout", new=io.StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as error_context:
                mct_validate.finalise(3)
            self.assertEqual(fake_out.getvalue(), expected_out)
            self.assertEqual(error_context.exception.code, 3)
