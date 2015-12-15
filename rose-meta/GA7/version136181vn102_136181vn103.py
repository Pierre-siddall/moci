import rose.upgrade
import re
import sys

class UpgradeError(Exception):

      """Exception created when an upgrade fails."""

      def __init__(self, msg):
          self.msg = msg

      def __repr__(self):
          sys.tracebacklimit = 0
          return self.msg

      __str__ = __repr__


class vn102_t764(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #764 by andymalcolm."""

    BEFORE_TAG = "ga6_136.18.1"
    AFTER_TAG = "vn10.2_t764"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, ["namelist:run_precip", "precip_segment_size"], "32")
        self.add_setting(config, ["namelist:run_bl", "bl_segment_size"], "16")
        return config, self.reports

class vn102_t852(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #852 by AdrianLock."""

    BEFORE_TAG = "vn10.2_t764"
    AFTER_TAG = "vn10.2_t852"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, ["namelist:run_bl","l_bl_mix_qcf"],".true.")
        return config, self.reports

class vn102_t859(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #859 by Nick Savage."""

    BEFORE_TAG = "vn10.2_t852"
    AFTER_TAG = "vn10.2_t859"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, 
          ["namelist:run_aerosol", "l_sulpc_2_way_coupling"],".true.")
        
        return config, self.reports

class vn102_t646(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #646 by Carlos Ordonez."""

    BEFORE_TAG = "vn10.2_t859"
    AFTER_TAG = "vn10.2_t646"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
	self.add_setting(config, 
            ["namelist:temp_fixes", "l_fix_nh4no3_equilibrium"], ".false.")
        return config, self.reports

class vn102_t911(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #911 by David Walters."""

    BEFORE_TAG = "vn10.2_t646"
    AFTER_TAG = "vn10.2_t911"

### NOT REQUIRED for GA6+ upgrade ### 

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # # Include the option to set the ENDGame w-damping reference height 
        # # to the height of the lid, but switch this off on upgrade
        # self.add_setting(config, ["namelist:temp_fixes", "l_eg_damp_height_lid"], ".false.")
        return config, self.reports

class vn102_t155(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #155 by Nick Savage."""

    BEFORE_TAG = "vn10.2_t911"
    AFTER_TAG = "vn10.2_t155"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, 
          ["namelist:run_aerosol", "l_temporal_emi"],".false.")
        return config, self.reports

class vn102_t897(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #897 by David Walters."""

    BEFORE_TAG = "vn10.2_t155"
    AFTER_TAG = "vn10.2_t897"

### NOT REQUIRED for GA6+ upgrade ### 

    def upgrade(self, config, meta_config=None):
          # # Find value of l_mcr_iter
          # is_mcr_iter = self.get_setting_value(config,
          #                                ['namelist:run_precip',
          #                                 'l_mcr_iter'])
          # # If switched off, add new variables switched off
          # if '.false.' in is_mcr_iter:
          #       self.add_setting(config,
          #                    ['namelist:run_precip', 'i_mcr_iter'],
          #                    value = '0')
          #       self.add_setting(config,
          #                    ['namelist:run_precip', 'niters_mp'],
          #                    value = '1',
          #                    state = rose.config.ConfigNode.STATE_SYST_IGNORED)
          #       self.add_setting(config,
          #                    ['namelist:run_precip', 'timestep_mp_in'],
          #                    value = '120',
          #                    state = rose.config.ConfigNode.STATE_SYST_IGNORED)

          # # If switched on, add new variables with number of
          # # iterations (niters_mp) defined as the product of the 2
          # # old types of iterations (niter_bs and lsiter)
          # else:
          #       niter_bs = self.get_setting_value(config,
          #                                ['namelist:run_precip',
          #                                 'niter_bs'])
          #       lsiter = self.get_setting_value(config,
          #                                ['namelist:run_precip',
          #                                 'lsiter'])
          #       self.add_setting(config,
          #                    ['namelist:run_precip', 'i_mcr_iter'],
          #                    value = '1')
          #       self.add_setting(config,
          #                    ['namelist:run_precip', 'niters_mp'],
          #                    value = str(int(niter_bs)*int(lsiter)))
          #       self.add_setting(config,
          #                    ['namelist:run_precip', 'timestep_mp_in'],
          #                    value = '120',
          #                    state = rose.config.ConfigNode.STATE_SYST_IGNORED)
    
          # # Finally, in either case, remove old redundant variables
          # self.remove_setting(config, ["namelist:run_precip", "l_mcr_iter"])
          # self.remove_setting(config, ["namelist:run_precip", "lsiter"])
          # self.remove_setting(config, ["namelist:run_precip", "niter_bs"])
                
          return config, self.reports

class vn102_t926(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #926 by David Walters."""

    BEFORE_TAG = "vn10.2_t897"
    AFTER_TAG = "vn10.2_t926"

### NOT REQUIRED for GA6+ upgrade ### 

    def upgrade(self, config, meta_config=None):
          # Find value of l_emcorr
          # is_emcorr = self.get_setting_value(config,
          #                                ['namelist:run_eng_corr',
          #                                 'l_emcorr'])

          # # Find values of secs_per_periodim, 
          # # steps_per_periodim and a_energysteps
          # secs_per_periodim = self.get_setting_value(config,
          #                                ['namelist:nlstcgen',
          #                                 'secs_per_periodim'])
          # steps_per_periodim = self.get_setting_value(config,
          #                                ['namelist:nlstcgen',
          #                                 'steps_per_periodim'])
          # a_energysteps = self.get_setting_value(config,
          #                                ['namelist:run_eng_corr',
          #                                 'a_energysteps'])
          # # Calculate a_energyhours (as a string)
          # isec_per_hour = 3600
          # a_energyhours = str( int(a_energysteps)
          #                      * int(secs_per_periodim)
          #                      / int(steps_per_periodim) 
          #                      / isec_per_hour )

          # # If switched off, add new variable switched off
          # if '.false.' in is_emcorr:
          #       self.add_setting(config,
          #                    ['namelist:run_eng_corr', 'a_energyhours'],
          #                    value = a_energyhours,
          #                    state = rose.config.ConfigNode.STATE_SYST_IGNORED)
          # # If switched off, add new variable switched on
          # else:
          #     self.add_setting(config,
          #                    ['namelist:run_eng_corr', 'a_energyhours'],
          #                    value = a_energyhours)
          
          # # Finally, in either case, remove old redundant variables
          # self.remove_setting(config, ["namelist:run_eng_corr", "a_energysteps"])

          return config, self.reports

class vn102_t61(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #61 by Rachel Stratton."""

    BEFORE_TAG = "vn10.2_t926"
    AFTER_TAG = "vn10.2_t61"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Removing 4A convection so need to upgrade apps that are still trying to use the 4A scheme
        i_convection_local = self.get_setting_value(
                config, ["namelist:run_convection", "i_convection_vn"])
        cape_opt_local = self.get_setting_value(
                config, ["namelist:run_convection", "cape_opt"])
        ent_fac_local = self.get_setting_value(
                config, ["namelist:run_convection", "ent_fac"])
        if i_convection_local == "4":
	    # Changing to convection version 5A
            self.change_setting_value(config, ["namelist:run_convection", "i_convection_vn"],"5")
            # Need to reset convection diagnosis options as settings from 4A will be wrong and will fail
	    # Taking values from GA6 physics which uses 5A convection - this is considered
	    # the best choice at present. It will change the science but this comes as part of the 
	    # change to the 5A scheme. Not altering limit_pert_opt or tv1_sd_opt.
            self.change_setting_value(config, ["namelist:run_convection", "icvdiag"],"1")
            self.change_setting_value(config, ["namelist:run_convection", "cvdiag_inv"],"0")
            self.change_setting_value(config, ["namelist:run_convection", "cvdiag_sh_wtest"],"0.02")
            self.change_setting_value(config, ["namelist:run_convection", "plume_water_load"],"0")
            self.change_setting_value(config, ["namelist:run_convection", "dil_plume_water_load"],"0")
            # Decided to put on safety checks as this as a better settings for 5A scheme
	    # This came with GA5 physics and is used in GA6 physics.
            self.change_setting_value(config, ["namelist:run_convection", "l_safe_conv"],".true.")
            # Entrainment need to set values for mid and deep separately for 5A scheme
	    # Taking entrainment settings from 4A value and translating to same for 5A
            self.change_setting_value(config, ["namelist:run_convection", "ent_opt_dp"],"0")
            self.change_setting_value(config, ["namelist:run_convection", "ent_fac_dp"],ent_fac_local)
            self.change_setting_value(config, ["namelist:run_convection", "ent_opt_md"],"0")
            self.change_setting_value(config, ["namelist:run_convection", "ent_fac_md"],ent_fac_local)
            # Cape closure option 5A scheme now has separate options for mid and deep
	    # Keeping the same by settings the 5A variables to the 4A value
            self.change_setting_value(config, ["namelist:run_convection", "cldbase_opt_dp"],cape_opt_local)
            self.change_setting_value(config, ["namelist:run_convection", "cldbase_opt_md"],cape_opt_local)
            # Ensuring shallow value set sensibly
            self.change_setting_value(config, ["namelist:run_convection", "cldbase_opt_sh"],"0")
        # Remove variables no longer required in convection namelist
        self.remove_setting(config, ["namelist:run_convection", "cape_opt"])
        self.remove_setting(config, ["namelist:run_convection", "ent_fac"])
        self.remove_setting(config, ["namelist:run_convection", "l4a_kterm"])
        # remove the existing Random Parameter items related to convection scheme 4A
	# This part provided by Warren Tennant for the stochastic scheme
        self.remove_setting(config,["namelist:run_stochastic", "cape_timescale_max"])
        self.remove_setting(config,["namelist:run_stochastic", "cape_timescale_min"])
        self.remove_setting(config,["namelist:run_stochastic", "entcoef_max"])
        self.remove_setting(config,["namelist:run_stochastic", "entcoef_min"])
        return config, self.reports


class vn102_t954(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #954 by Eddy Robertson."""

    BEFORE_TAG = "vn10.2_t61"
    AFTER_TAG = "vn10.2_t954"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""

        # add settings for wood products
        self.add_setting(config, ["namelist:jules_triffid", "alloc_fast_io"],  "0.6,0.6,1.0,1.0,0.8")
        self.add_setting(config, ["namelist:jules_triffid", "alloc_med_io"],  "0.3,0.4,0.0,0.0,0.2")
        self.add_setting(config, ["namelist:jules_triffid", "alloc_slow_io"],  "0.1,0.0,0.0,0.0,0.0")

        return config, self.reports


class vn102_t212(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #212 by Alejandro Bodas-Salcedo."""

    BEFORE_TAG = "vn10.2_t954"
    AFTER_TAG = "vn10.2_t212"

### NOT REQUIRED for GA6+ upgrade ### 

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # self.remove_setting(config, ["namelist:run_cosp", "cosp_ncolumns"])
        # self.remove_setting(config, ["namelist:run_cosp", "cosp_npoints_it"])
        return config, self.reports


class vn102_t367(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #367 by Jonathan Wilkinson."""

    BEFORE_TAG = "vn10.2_t212"
    AFTER_TAG = "vn10.2_t367"

### NOT REQUIRED for GA6+ upgrade ### 

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # self.add_setting(config, ["namelist:temp_fixes", "l_fix_mphys_diags_iter"], ".false.")
        return config, self.reports


class vn102_t430(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #430 by paulearnshaw."""

    BEFORE_TAG = "vn10.2_t367"
    AFTER_TAG = "vn10.2_t430"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        self.add_setting(config, ["namelist:clmchfcg", 
                                  "l_cts_fcg_rates"], ".false.")
        self.add_setting(config, ["namelist:temp_fixes", 
                                  "l_rm_hardwire_gas360"], ".false.")
        return config, self.reports


class vn102_t452(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #452 by Carlos Ordonez."""

    BEFORE_TAG = "vn10.2_t430"
    AFTER_TAG = "vn10.2_t452"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        self.add_setting(config,
            ["namelist:run_ukca", "l_ukca_classic_hetchem"], ".false.")
        return config, self.reports


class vn102_t978(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #978 by Richard Hill."""

    BEFORE_TAG = "vn10.2_t452"
    AFTER_TAG = "vn10.2_t978"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # First, get existing values for coupling freqency, if any. 
        freq=self.get_setting_value(config, ["namelist:coupling_control",
	                                     "oasis_couple_freq"])
        if freq is not None:
            # Remove existing oasis_couple_freq
            self.remove_setting(config, ["namelist:coupling_control",
	                                 "oasis_couple_freq"])
            # Add all our new coupling frequencies initialising the 
	    # atmos<->ocean exchanges with our freq value (hours) and 
	    # 0 minutes, and the rest with 0 hours and 0 minutes. 
            newfreq=freq+",0"
            self.add_setting(config, ["namelist:coupling_control",
                                      "oasis_couple_freq_ao"], newfreq)
            self.add_setting(config, ["namelist:coupling_control",
                                      "oasis_couple_freq_oa"], newfreq)
            # The following are brand new so we just set them to zero
            # since no existing models will have controls for chemistry
            # or wave coupling yet. 
            newfreq="0,0"
            self.add_setting(config, ["namelist:coupling_control",
                                      "oasis_couple_freq_ac"], newfreq)
            self.add_setting(config, ["namelist:coupling_control",
                                      "oasis_couple_freq_ca"], newfreq)
            self.add_setting(config, ["namelist:coupling_control",
                                      "oasis_couple_freq_aw"], newfreq)
            self.add_setting(config, ["namelist:coupling_control",
                                      "oasis_couple_freq_wa"], newfreq)
	      
        return config, self.reports

class vn102_t774(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #774 by Colin Johnson."""

    BEFORE_TAG = "vn10.2_t978"
    AFTER_TAG = "vn10.2_t774"

### NOT REQUIRED for GA6+ upgrade ### 

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here

        # # Calculate local chemical timestep
        # interval_local = self.get_setting_value(
        #    config, ["namelist:run_ukca", "i_ukca_interval"])
        # secs_im_local = self.get_setting_value(
        #    config, ["namelist:nlstcgen", "secs_per_periodim"])
        # steps_im_local = self.get_setting_value(
        #    config, ["namelist:nlstcgen", "steps_per_periodim"])
        # chem_ts_local = int(interval_local)*int(secs_im_local)/int(steps_im_local)
        # chem_ts_str = str(chem_ts_local)

        # # Add variable to run_ukca namelist
        # self.add_setting(config, ["namelist:run_ukca", "chem_timestep"], value=chem_ts_str)

        # # Remove variable no longer required in run_ukca namelist
        # self.remove_setting(config, ["namelist:run_ukca", "i_ukca_interval"])
        return config, self.reports

class vn102_t980(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #980 by Adrian Lock."""

    BEFORE_TAG = "vn10.2_t774"
    AFTER_TAG = "vn10.2_t980"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, ["namelist:run_murk","l_murk_vis"],".true.")
        l_murk = self.get_setting_value(config, ["namelist:run_murk", "l_murk"])
        if l_murk == ".false.":
          # change the value of murk_advect and murk_source to true when
          # murk is switched off so that if murk is ever switched on
          # they will default to true too (no Met Office configurations have ever
          # had l_murk true without these other varibles true as well)
          self.change_setting_value(config, ["namelist:run_murk","l_murk_advect"],".true.")
          self.change_setting_value(config, ["namelist:run_murk","l_murk_source"],".true.")
        return config, self.reports

class vn102_t98(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #98 by nicksavage."""

    BEFORE_TAG = "vn10.2_t980"
    AFTER_TAG = "vn10.2_t98"
    
    # This macro deletes all stash 34.151-34.172 from
    # a. Transplants
    # b. Items
    # c. STASH
   
    # Parameters for section and item numbers
    UKCA_SECT = 34
    UKCA_NTP_FIRST = 151
    UKCA_NTP_LAST = 172

    def delete_transp(self, config):
        '''Delete transplant namelists with stash codes
        34.151 to 34.172'''
        
        
        # check all objects in this configuration
        # and add those to deleted to to_del
        # note that we can't delete them inside the loop
        # as it breaks the iteration over config
        to_del = []
        for obj in config.get_value():
        
             # is it a transplant namelist?
             if re.search(r'namelist:trans', obj):
             
               # get the section and item numbers as integers
               item = int(self.get_setting_value(config, [ obj, 'itemc']))
               section = int(self.get_setting_value(config, [ obj, 'sctnc']))

               # check if they are the items we need to remove
               if (section == self.UKCA_SECT and item >= self.UKCA_NTP_FIRST 
                 and item <= self.UKCA_NTP_LAST):
                   # append to the list to be deleted
                   to_del.append(obj)
        
        # now loop over the namelists to be deleted and actually delete them
        for delme in to_del:
           self.remove_setting(config, [delme],info='UKCA NTPs moved to higher ' +
             'item numbers. If transplanting needed, please modify your app')
        
        return config

    def delete_items(self, config):   
        '''Delete items namelists with stash codes
        34.151 to 34.172'''
        
        # check all objects in this configuration
        # and add those to deleted to to_del
        # note that we can't delete them inside the loop
        # as it breaks the iteration over config.get_value()

        # create a list with all the stash to remove in it
        stash_to_delete = range(1000*self.UKCA_SECT + self.UKCA_NTP_FIRST,
            1000*self.UKCA_SECT + self.UKCA_NTP_LAST + 1)


        to_del = []
        to_mod = []
        values = []
        for obj in config.get_value():
        
             # is it a items namelist?
             if re.search(r'namelist:items', obj):
             
               # get the stash code as an integer
               # This is hard because sometimes we have more than one stashcode
               # as a comma separated string
               
               # first turn the comma seperated string into a list of integers
               stsh_cd_list = [int(x) for x in self.get_setting_value(config, [ obj, 'stash_req']).split(',')]

               # test the intersection of this with stash_to_delete
               nmatch = len(set(stash_to_delete) & set(stsh_cd_list))

               # if the intersection is zero length, then nothing to do
               if (nmatch > 0):

                   # if all items in stsh_cd_list are matches, then 
                   # we can delete the whole namelist - append to the list to be deleted
                   if (nmatch == len(stsh_cd_list)):
                       to_del.append(obj)
                   
                   # othewise we need to append to the modify list, with a new value
                   # which is the difference between the sets
                   else:
                       to_mod.append(obj)
                       outlist = list(set(stsh_cd_list) - set(stash_to_delete))
                       csvstr = ','.join(map(str, outlist))
                       # append a csv string of above to values
                       values.append(csvstr)
               
        # now loop over the namelists to be deleted and actually delete them
        for delme in to_del:
           self.remove_setting(config, [delme],info='UKCA NTPs moved to higher ' +
             'item numbers. If initialisation needed, please modify your app')
        
        # finally loop over the namelists to be modified and modify them
        for modme, tovalue in zip(to_mod,values):
           self.change_setting_value(config, [modme,'stash_req'], tovalue,info='UKCA NTPs moved to higher ' +
             'item numbers. If initialisation needed, please modify your app')

        return config
    
    def delete_stash(self, config):
        '''Delete stash namelists with stash codes
        34.151 to 34.172'''
        
        # check all objects in this configuration
        # and add those to deleted to to_del
        # note that we can't delete them inside the loop
        # as it breaks the iteration over config
        to_del = []
        for obj in config.get_value():
        
             # is it a transplant namelist?
             if re.search(r'namelist:streq', obj):
             
               # get the section and item numbers as integers
               item = int(self.get_setting_value(config, [ obj, 'item']))
               section = int(self.get_setting_value(config, [ obj, 'isec']))

               # check if they are the items we need to remove
               if (section == self.UKCA_SECT and item >= self.UKCA_NTP_FIRST 
                 and item <= self.UKCA_NTP_LAST):
                   # append to the list to be deleted
                   to_del.append(obj)
        
        # now loop over the namelists to be deleted and actually delete them
        for delme in to_del:
           self.remove_setting(config, [delme],info='UKCA NTPs moved to higher ' +
             'item numbers. If STASH output needed, please modify your app')
        
        return config

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        
        # delete transplant namelists
        config = self.delete_transp(config)
        # delete items namelists
        config = self.delete_items(config)
        # delete stash namelists
        config = self.delete_stash(config)
        
        return config, self.reports


class vn102_t797(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #797 by Nic Gedney."""

    BEFORE_TAG = "vn10.2_t98"
    AFTER_TAG = "vn10.2_t797"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here

        self.add_setting(config, ["namelist:jules_hydrology", "l_wetland_ch4_npp"], ".false.")
 
        return config, self.reports


class vn102_t952(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #952 by Paul Cresswell.
       Remove duplication of namelists across multiple files."""

    BEFORE_TAG = "vn10.2_t797"
    AFTER_TAG = "vn10.2_t952"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""

        # Determine if this is an SCM app first:
        model_type = self.get_setting_value(config,
                         ["namelist:model_domain", "model_type"])

        # Update the NAMELIST file contents (if present):
        namelist_source = self.get_setting_value(config, 
                              ["file:NAMELIST", "source"])
        if namelist_source:
            # Remove the namelists that are no longer read from NAMELIST,
            # or that are being moved in the source order:
            remove_nl = (['nlcfiles', 'temp_fixes', 'carbon_options',
                          'coupling_control', 'model_domain',
                          'jules_surface_types', 'jules_surface',
                          'jules_radiation', 'jules_hydrology',
                          'jules_sea_seaice', 'jules_soil', 'jules_vegetation',
                          'jules_snow', 'urban_switches', 'planet_constants',
                          'run_dust', 'run_ukca', 'run_gwd', 'run_murk',
                          'run_convection', 'run_bl', 'run_rivers',
                          'run_precip', 'run_radiation', 'run_cloud',
                          'run_aerosol', 'lam_config', 'run_ozone',
                          'run_free_tracers', 'ancilcta', '\(?items\(:\)\)?',
                          'run_eng_corr', 'run_electric', 'nlsizes',
                          'nlstcall', 'gen_phys_inputs', 'run_dyn',
                          'run_dyntest', 'run_track', 'iau_nl'])
            for namelist in remove_nl:
                entry = 'namelist:' + namelist + ' '
                namelist_source = re.sub(entry,'',namelist_source)
            # Insert the moved items in the right place:
            namelist_source = re.sub('namelist:nlst_mpp',
                                     'namelist:nlst_mpp namelist:run_track',
                                     namelist_source)
            namelist_source = re.sub('namelist:urban2t_param',
                                     'namelist:urban2t_param namelist:iau_nl',
                                     namelist_source)

            # Remove excess whitespace:
            namelist_source = re.sub(r' {2,}',' ',namelist_source)
            self.change_setting_value(config, ["file:NAMELIST", "source"],
                                      namelist_source)

            # Rename the NAMELIST file:
            self.rename_setting(config, ["file:NAMELIST"], ["file:ATMOSCNTL"])

        # Update the RECONA file contents (if present):
        recona_source = self.get_setting_value(config, ["file:RECONA","source"])
        if recona_source:
            # Remove items(:):
            recona_source = re.sub(
                            '\(?namelist:items\(:\)\)? ','',recona_source)
            recona_source = re.sub(r' {2,}',' ',recona_source)
            self.change_setting_value(config, ["file:RECONA", "source"],
                                      recona_source)

        # Update the SHARED file contents (every um-atmos app should have this):
        shared_source = self.get_setting_value(config, ["file:SHARED","source"])

        # Swap run_electric/ancilcta and (non-SCM apps) add items(:):
        if model_type == "5":
            shared_end = 'namelist:run_electric namelist:ancilcta'
        else:
            shared_end = (
                'namelist:run_electric namelist:ancilcta (namelist:items(:))')

        shared_source = re.sub('namelist:ancilcta', '', shared_source)
        shared_source = re.sub(
                  'namelist:run_electric ', shared_end, shared_source)

        # Move nlstcall and add a second copy of ancilcta to avoid a rewind:
        shared_source = re.sub('namelist:nlstcall ','',shared_source)
        # Optional parentheses needed for SCM apps.
        shared_source = re.sub(r'(\(?namelist:nlcfiles\)?)',
                        r'\1 namelist:nlstcall namelist:ancilcta',
                        shared_source)

        # Move run_dyntest:
        shared_source = re.sub('namelist:run_dyntest', '', shared_source)
        shared_source = re.sub('namelist:run_dyn ',
                               'namelist:run_dyn namelist:run_dyntest ',
                               shared_source)

        # Move the JULES namelists as a single block:
        matchobj = re.search(
                   r'namelist:jules_surface_types.*namelist:urban_switches ',
                   shared_source)
        shared_source = re.sub(matchobj.group(0),'',shared_source)
        shared_source = re.sub('namelist:run_dyntest ',
                               'namelist:run_dyntest ' + matchobj.group(0),
                               shared_source)


        # SCM only: move another block of namelists to keep the order of files
        # in SHARED consistent with full UM apps.
        if model_type == "5":
            matchobj = re.search(
                       r'namelist:run_aerosol.*namelist:run_free_tracers ',
                       shared_source)
            shared_source = re.sub(matchobj.group(0), '', shared_source)
            shared_source = re.sub('namelist:run_cloud ',
                                   'namelist:run_cloud ' + matchobj.group(0),
                                   shared_source)

        shared_source = re.sub(r' {2,}',' ',shared_source)
        self.change_setting_value(config, ["file:SHARED", "source"],
                                  shared_source)

        return config, self.reports


class vn102_t734(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #734 by David S Amundsen."""

    BEFORE_TAG = "vn10.2_t952"
    AFTER_TAG = "vn10.2_t734"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        
        self.add_setting(config, ["namelist:r2lwclnl","l_extra_top_lw"], ".false.")
        self.add_setting(config, ["namelist:r2lwclnl","l_extra_top_lw2"], ".false.")
        self.add_setting(config, ["namelist:r2swclnl","l_extra_top_sw"], ".false.")
        self.add_setting(config, ["namelist:r2swclnl","l_extra_top_sw2"], ".false.")
        
        self.add_setting(config, ["namelist:r2lwclnl","l_co2_lw"], ".true.")
        self.add_setting(config, ["namelist:r2lwclnl","l_co2_lw2"], ".true.")
        self.add_setting(config, ["namelist:r2swclnl","l_co2_sw"], ".true.")
        self.add_setting(config, ["namelist:r2swclnl","l_co2_sw2"], ".true.")
        
        return config, self.reports


class vn102_t863(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #863 by KalliFurtado."""

    BEFORE_TAG = "vn10.2_t734"
    AFTER_TAG = "vn10.2_t863"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        self.add_setting(config, ["namelist:run_precip", "l_shape_rime"], ".false.")
        self.add_setting(config, ["namelist:run_precip", "a_ratio_fac"], "0.0517")
        self.add_setting(config, ["namelist:run_precip", "a_ratio_exp"], "-0.2707")
        self.add_setting(config, ["namelist:run_precip", "qclrime"], "1e-04")
        self.add_setting(config, ["namelist:run_cloud", "l_subgrid_qv"], ".true.")
        return config, self.reports

class vn102_t1016(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1016 by John Hemmings."""

    BEFORE_TAG = "vn10.2_t863"
    AFTER_TAG = "vn10.2_t1016"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        i_ukca_photol_local = self.get_setting_value(
            config, ["namelist:run_ukca", "i_ukca_photol"])
        if i_ukca_photol_local == "2":
            # Change to use Fast-JX scheme in place of Fast-J
            warn_msg = ('The selected photolysis scheme Fast-J (option 2) ' +
                'has been retired. The Fast-JX scheme will be used instead ' +
                'with a default troposphere only configuration.')
            self.add_report("namelist:run_ukca", "i_ukca_photol",
                            i_ukca_photol_local, warn_msg, is_warning=True)
            self.change_setting_value(
                config, ["namelist:run_ukca", "i_ukca_photol"], "3")
            # Use default Fast-JX cross-section data in place of Fast-J data
            self.change_setting_value(
                config, ["namelist:run_ukca", "jvspec_file"], 
                "'FJX_spec_Nov11.dat'")
            # Set additional namelist variables required for Fast-JX to 
            # sensible default values
            self.change_setting_value(
                config, ["namelist:run_ukca", "jvscat_file"], 
                "'FJX_scat.dat'")
            self.change_setting_value(
                config, ["namelist:run_ukca", "fastjx_numwl"], "8")
            self.change_setting_value(
                config, ["namelist:run_ukca", "fastjx_prescutoff"], "20.000")
            self.change_setting_value(
                config, ["namelist:run_ukca", "fastjx_mode"], "1")
        return config, self.reports
class vn102_t789(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #789 by <mohitdalvi>."""

    BEFORE_TAG = "vn10.2_t1016"
    AFTER_TAG = "vn10.2_t789"

    def upgrade(self, config, meta_config=None):
        """Add Stratospheric factor to Nudging namelist"""
        # Input your macro commands here
        self.add_setting(config,
           ["namelist:run_nudging", "ndg_strat_fac"], "1.0")

        return config, self.reports

class vn102_t1063(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1063 by r.s.smith@reading.ac.uk"""

    BEFORE_TAG = "vn10.2_t789"
    AFTER_TAG = "vn10.2_t1063"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        npft = int(self.get_setting_value(config, ["namelist:jules_surface_types", "npft"]))
        nnvg = int(self.get_setting_value(config, ["namelist:jules_surface_types", "nnvg"]))
        self.add_setting(config, ["namelist:jules_elevate", "l_elev_absolute_height"],','.join(['.false.']*(npft+nnvg)),     info="Add a switch to use absolute elevations levels above sea-level")
        return config, self.reports

class vn102_t153(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #153 by Malcolm Brooks."""

    BEFORE_TAG = "vn10.2_t1063"
    AFTER_TAG = "vn10.2_t153"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, ["namelist:jules_surface", "l_vary_z0m_soil"], ".false.")
        return config, self.reports

class vn102_t823(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #823 by Erica Neininger."""

    BEFORE_TAG = "vn10.2_t153"
    AFTER_TAG = "vn10.2_t823"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        import os
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "ga6_136.18.1", "lib", "python", "macros"))
        import stash_indices

        # Add switch for disabling PP output at TimeStep 0
        for obj in config.get_value():
            if re.search(r"namelist:time", obj):
                iopt = self.get_setting_value(config, [obj, "iopt"])
                istr = self.get_setting_value(config, [obj, "istr"])
                if int(iopt) == 1 and int(istr) == 0:
                    self.add_setting(config, [obj, "lts0"], ".false.")
                else:
                    self.add_setting(config, [obj, "lts0"], ".false.",
                                     state=config.STATE_SYST_IGNORED)

        stash_indices.TidyStashTransform().transform(config)
        config, reports = stash_indices.TidyStashTransform().transform(config)
        self.reports += reports

        return config, self.reports

class vn102_t1023(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1023 by Adrian Lock."""

    BEFORE_TAG = "vn10.2_t823"
    AFTER_TAG = "vn10.2_t1023"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, ["namelist:run_bl","l_use_surf_in_ri"],".false.")
        self.add_setting(config, ["namelist:run_bl","lambda_min_nml"],"40.0")
        self.add_setting(config, ["namelist:run_bl","ritrans"],"0.1")
        return config, self.reports

class vn102_t1096(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1096 by Sarah Shannon."""

    BEFORE_TAG = "vn10.2_t1023"
    AFTER_TAG = "vn10.2_t1096"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, ["namelist:jules_surface", "l_elev_lw_down"], ".false.")
        return config, self.reports

class vn102_t485(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #485 by johnmedwards."""

    BEFORE_TAG = "vn10.2_t1096"
    AFTER_TAG = "vn10.2_t485"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        """New apps will have these included, so only set defaults for old ones."""
        if config.get(["l_force_relayer"]) is None:
            self.add_setting(config, ["namelist:recon", "l_force_relayer"], ".false.")
        if config.get(["l_regularize_landice"]) is None:
            self.add_setting(config, ["namelist:recon", "l_regularize_landice"], ".false.")
        if config.get(["snow_landice_min"]) is None:
            self.add_setting(config, ["namelist:recon", "snow_landice_min"], "5.0e4", state=rose.config.ConfigNode.STATE_SYST_IGNORED)
        if config.get(["snow_icefree_max"]) is None:
            self.add_setting(config, ["namelist:recon", "snow_icefree_max"], "5.0e3", state=rose.config.ConfigNode.STATE_SYST_IGNORED)
        return config, self.reports


class vn103_t1119(rose.upgrade.MacroUpgrade):

    BEFORE_TAG = "vn10.2_t485"
    AFTER_TAG = "ga6_136.18.1_vn10.3"

    def upgrade(self, config, meta_config=None):
        """Upgrade configuration to next major version."""
        if self.get_setting_value(config, ["env", "VN"]):
            self.change_setting_value(config, ["env", "VN"],
                                      "10.3")
        stashmaster_path = self.get_setting_value(config, ["env", "STASHMSTR"])
        if stashmaster_path:
           stashmaster_path = re.sub("vn\d+\.\d+/ctldata",
                                     "vn10.3/ctldata",
                                      stashmaster_path)
           self.change_setting_value(config, ["env", "STASHMSTR"],
                                     stashmaster_path)
        return config, self.reports

