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



class vn103_t1162(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1162 by Ian Boutle."""

    BEFORE_TAG = "GA7-vn10.3_GO6"
    AFTER_TAG = "vn10.3_t1162"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.remove_setting(config,["namelist:run_bl","prandtl"])
        self.remove_setting(config,["namelist:run_bl","l_full_lambdas"])
        self.remove_setting(config,["namelist:run_bl","l_lambdam2"])
        self.remove_setting(config,["namelist:run_bl","subs_couple_fix"])
        return config, self.reports

class vn103_t957(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #957 by Eddy Robertson."""

    BEFORE_TAG = "vn10.3_t1162"
    AFTER_TAG = "vn10.3_t957"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""

        # add the replacement "select_output_fields" entry
        self.add_setting(config, ["namelist:jules_triffid", "dpm_rpm_ratio_io"],
                         "0.25,0.25,0.67,0.67,0.33")

        return config, self.reports


class vn103_t958(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #958 by <mohitdalvi>."""

    BEFORE_TAG = "vn10.3_t957"
    AFTER_TAG = "vn10.3_t958"

    def upgrade(self, config, meta_config=None):
        """Move ukca* RADAER file spec from nlcfiles to run_ukca."""

        # 1. Get value (filename) for each file from nlcfiles namelist
        # 2. Add the item to run_ukca namelist with obtained value
        # 3. Remove existing item in nlcfiles namelist

        ukca_fname = ''
        ukca_fname = self.get_setting_value(config,
                       ['namelist:nlcfiles', 'ukcaaclw'])
        self.add_setting(config,['namelist:run_ukca', 'ukcaaclw'],
                         value = ukca_fname)
        self.remove_setting(config,['namelist:nlcfiles', 'ukcaaclw'])

        ukca_fname = ''
        ukca_fname = self.get_setting_value(config,
                       ['namelist:nlcfiles', 'ukcaacsw'])
        self.add_setting(config,['namelist:run_ukca', 'ukcaacsw'],
                         value = ukca_fname)
        self.remove_setting(config,['namelist:nlcfiles', 'ukcaacsw'])

        ukca_fname = ''
        ukca_fname = self.get_setting_value(config,
                       ['namelist:nlcfiles', 'ukcaanlw'])
        self.add_setting(config,['namelist:run_ukca', 'ukcaanlw'],
                         value = ukca_fname)
        self.remove_setting(config,['namelist:nlcfiles', 'ukcaanlw'])

        ukca_fname = ''
        ukca_fname = self.get_setting_value(config,
                       ['namelist:nlcfiles', 'ukcaansw'])
        self.add_setting(config,['namelist:run_ukca', 'ukcaansw'],
                         value = ukca_fname)
        self.remove_setting(config,['namelist:nlcfiles', 'ukcaansw'])

        ukca_fname = ''
        ukca_fname = self.get_setting_value(config,
                       ['namelist:nlcfiles', 'ukcacrlw'])
        self.add_setting(config,['namelist:run_ukca', 'ukcacrlw'],
                         value = ukca_fname)
        self.remove_setting(config,['namelist:nlcfiles', 'ukcacrlw'])

        ukca_fname = ''
        ukca_fname = self.get_setting_value(config,
                       ['namelist:nlcfiles', 'ukcacrsw'])
        self.add_setting(config,['namelist:run_ukca', 'ukcacrsw'],
                         value = ukca_fname)
        self.remove_setting(config,['namelist:nlcfiles', 'ukcacrsw'])

        ukca_fname = ''
        ukca_fname = self.get_setting_value(config,
                       ['namelist:nlcfiles', 'ukcaprec'])
        self.add_setting(config,['namelist:run_ukca', 'ukcaprec'],
                         value = ukca_fname)
        self.remove_setting(config,['namelist:nlcfiles', 'ukcaprec'])

        return config, self.reports

class vn103_t1151(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1151 by Carlos Ordonez."""

    BEFORE_TAG = "vn10.3_t958"
    AFTER_TAG = "vn10.3_t1151"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        self.add_setting(config, 
            ["namelist:run_aerosol", "l_bmass_hilem_variable"], ".false.")
        self.add_setting(config, 
            ["namelist:run_aerosol", "bmass_high_level_1"], "3")
        self.add_setting(config, 
            ["namelist:run_aerosol", "bmass_high_level_2"], "20")
        return config, self.reports


class vn103_t853(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #853 by Joohyung Son."""

    BEFORE_TAG = "vn10.3_t1151"
    AFTER_TAG = "vn10.3_t853"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        self.add_setting(config, ["namelist:iau_nl", "l_iau_smcchecks"],
                         str(".false."))
        self.add_setting(config, ["namelist:iau_nl", "l_iau_tsoillandicemask"],
                         str(".false."))
        return config, self.reports

class vn103_t1164(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1164 by Ian Boutle."""

    BEFORE_TAG = "vn10.3_t853"
    AFTER_TAG = "vn10.3_t1164"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, ["namelist:run_precip","z_surf"],"0.0")
        return config, self.reports


class vn103_t648(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #648 by Michele Guidolin."""

    BEFORE_TAG = "vn10.3_t1164"
    AFTER_TAG = "vn10.3_t648"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        self.add_setting(config, [ "namelist:nlst_mpp", "l_swap_bounds_ddt" ],
                         ".true.")
        self.add_setting(config, [ "namelist:nlst_mpp", "l_ddt_cornerless" ],
                         ".false.")
        return config, self.reports


class vn103_t1282(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1282 by Nic Gedney."""

    BEFORE_TAG = "vn10.3_t648"
    AFTER_TAG = "vn10.3_t1282"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here

# Not required for GA7 upgrade
        # self.add_setting(config, ["namelist:jules_hydrology", "nfita"], "20")

        return config, self.reports
        
class vn103_t1036(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1036 by <paulselwood>."""

    BEFORE_TAG = "vn10.3_t1282"
    AFTER_TAG = "vn10.3_t1036"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        self.add_setting(config, ["namelist:run_gwd", "gw_seg_size"], "32")
        return config, self.reports
        
class vn103_t1017(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1017 by Ian Boutle."""

    BEFORE_TAG = "vn10.3_t1036"
    AFTER_TAG = "vn10.3_t1017"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, ["namelist:temp_fixes", "l_fix_ctile_orog"], ".false.")
        return config, self.reports
       
class vn103_t1315(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1315 by Chris Smith."""

    BEFORE_TAG = "vn10.3_t1017"
    AFTER_TAG = "vn10.3_t1315"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Delete Frierson control switches
        self.remove_setting(config, ["namelist:idealise","diffuse_dse_ap1"])
        self.remove_setting(config, ["namelist:idealise","diffuse_dse_ap2"])
        self.remove_setting(config, ["namelist:idealise","diffuse_q_ap1"])
        self.remove_setting(config, ["namelist:idealise","diffuse_q_ap2"])
        self.remove_setting(config, ["namelist:idealise","diffuse_u_ap1"])
        self.remove_setting(config, ["namelist:idealise","diffuse_u_ap2"])
        self.remove_setting(config, ["namelist:idealise","diffuse_v_ap1"])
        self.remove_setting(config, ["namelist:idealise","diffuse_v_ap2"])
        self.remove_setting(config, ["namelist:idealise","do_evap_ap1"])
        self.remove_setting(config, ["namelist:idealise","do_evap_ap2"])
        self.remove_setting(config, ["namelist:idealise","do_limit_surf_theta"])
        self.remove_setting(config, ["namelist:idealise","do_precip_ap1"])
        self.remove_setting(config, ["namelist:idealise","do_precip_ap2"])
        self.remove_setting(config, ["namelist:idealise","do_radiation_lw_ap1"])
        self.remove_setting(config, ["namelist:idealise","do_radiation_lw_ap2"])
        self.remove_setting(config, ["namelist:idealise","do_radiation_sw_ap1"])
        self.remove_setting(config, ["namelist:idealise","do_radiation_sw_ap2"])
        self.remove_setting(config, ["namelist:idealise","do_surface_drag_ap1"])
        self.remove_setting(config, ["namelist:idealise","do_surface_drag_ap2"])
        self.remove_setting(config, ["namelist:idealise","do_surface_flux_ap1"])
        self.remove_setting(config, ["namelist:idealise","do_surface_flux_ap2"])
        self.remove_setting(config, ["namelist:idealise","l_frierson"])
        return config, self.reports
 
class vn103_t1421(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1421 by Stephanie Woodward."""

    BEFORE_TAG = "vn10.3_t1315"
    AFTER_TAG = "vn10.3_t1421"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        self.add_setting(config, ["namelist:temp_fixes", "l_fix_ukca_impscav"], ".false.")
        return config, self.reports


class vn103_t1396(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1396 by annemccabe."""

    BEFORE_TAG = "vn10.3_t1421"
    AFTER_TAG = "vn10.3_t1396"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, ["namelist:run_stochastic","i_pert_theta_type"],"0")
        self.add_setting(config, ["namelist:run_stochastic","decorr_ts_pert_theta"],"600.0")
        self.add_setting(config, ["namelist:run_stochastic","l_pert_all_points"],".false.")
        return config, self.reports

class vn103_t698(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #698 by Martin Willett."""

    BEFORE_TAG = "vn10.3_t1396"
    AFTER_TAG = "vn10.3_t698"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, ["namelist:run_convection","l_conv_prog_precip"],".false.")
        self.add_setting(config, ["namelist:run_convection","tau_conv_prog_precip"],"10800.0",state = rose.config.ConfigNode.STATE_SYST_IGNORED)
        self.add_setting(config, ["namelist:run_convection","prog_ent_grad"],"-1.1",state = rose.config.ConfigNode.STATE_SYST_IGNORED)
        self.add_setting(config, ["namelist:run_convection","prog_ent_int"],"-2.9",state = rose.config.ConfigNode.STATE_SYST_IGNORED)
        self.add_setting(config, ["namelist:run_convection","prog_ent_max"],"2.5",state = rose.config.ConfigNode.STATE_SYST_IGNORED)
        self.add_setting(config, ["namelist:run_convection","prog_ent_min"],"0.5",state = rose.config.ConfigNode.STATE_SYST_IGNORED)
        return config, self.reports


class vn103_t299(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #299 by James Manners."""

    BEFORE_TAG = "vn10.3_t698"
    AFTER_TAG = "vn10.3_t299"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        self.add_setting(config, ["namelist:r2swclnl","l_solvar_sw"], ".false.")
        self.add_setting(config, ["namelist:r2swclnl","l_solvar_sw2"], ".false.")
        return config, self.reports
class vn103_t1356(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1356 by Anna Harper."""

    BEFORE_TAG = "vn10.3_t299"
    AFTER_TAG = "vn10.3_t1356"

    def upgrade(self, config, meta_config=None):
        """Upgrade a JULES runtime app configuration."""

        # ADD the trait parameters to pft_params namelist
        self.add_setting(config, ["namelist:jules_pftparm", "nsw_io"],"0.0072,0.0083,0.01604,0.0202,0.0072")
        self.add_setting(config, ["namelist:jules_pftparm", "nr_io"], "0.01726,0.00784,0.0162,0.0084,0.01726")
        self.add_setting(config, ["namelist:jules_pftparm", "hw_sw_io"], "5*0.5")
        self.add_setting(config, ["namelist:jules_triffid", "retran_l_io"], "5*0.5")
        self.add_setting(config, ["namelist:jules_triffid", "retran_r_io"], "5*0.2")

        # IF there are 9 PFTs, need to change these parameters
        npft = int(self.get_setting_value(config, ["namelist:jules_surface_types", "npft"]))
        source = self.get_setting_value(config, ["namelist:jules_surface_types","ncpft"])
        if source:
            ncpft = int(self.get_setting_value(config, ["namelist:jules_surface_types", "ncpft"]))

        if npft==9:
            if ncpft==4:
                #The last 4 are crops
                self.change_setting_value(config, ["namelist:jules_pftparm", "nsw_io"], "0.0072,0.0083,0.01604,0.0202,0.0072,-1,-1,-1,-1")
                self.change_setting_value(config, ["namelist:jules_pftparm", "nr_io"], "0.01726,0.00784,0.0162,0.0084,0.01726,-1,-1,-1,-1")
                self.change_setting_value(config, ["namelist:jules_pftparm", "hw_sw_io"], "9*0.5")
                self.change_setting_value(config, ["namelist:jules_triffid", "retran_l_io"], "9*0.5")
                self.change_setting_value(config, ["namelist:jules_triffid", "retran_r_io"], "9*0.2")
            elif ncpft==0:
                #All natural vegetation PFTs
                self.change_setting_value(config, ["namelist:jules_pftparm", "nsw_io"],"0.0072,0.0072,0.0072,0.0083,0.0083,0.01604,0.0202,0.0072,0.0072")
                self.change_setting_value(config, ["namelist:jules_pftparm", "nr_io"], "0.01726,0.01726,0.01726,0.00784,0.00784,0.0162,0.0084,0.01726,0.01726")
                self.change_setting_value(config, ["namelist:jules_pftparm", "hw_sw_io"], "9*0.5")
                self.change_setting_value(config, ["namelist:jules_triffid", "retran_l_io"], "9*0.5")
                self.change_setting_value(config, ["namelist:jules_triffid", "retran_r_io"], "9*0.2")
        return config, self.reports

class vn103_t1389(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1389 by Paul Cresswell."""

    BEFORE_TAG = "vn10.3_t1356"
    AFTER_TAG = "vn10.3_t1389"

    def upgrade(self, config, meta_config=None):
        """Add essential ioscntl inputs to all UM apps."""
        self.add_setting(config, ["namelist:ioscntl", "ios_spacing"], "0")
        self.add_setting(config, ["namelist:ioscntl", "ios_offset"], "0")
        self.add_setting(config, ["namelist:ioscntl", "ios_tasks_per_server"],
                         "1")

        # Fix invalid values of ios_spacing:
        ios_spacing = self.get_setting_value(config,
                                 ["namelist:ioscntl", "ios_spacing"])
        if int(ios_spacing) < 0:
           self.change_setting_value(config, 
                                 ["namelist:ioscntl", "ios_spacing"], "0")

        return config, self.reports

class vn103_t977(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #977 by <paulselwood>."""

    BEFORE_TAG = "vn10.3_t1389"
    AFTER_TAG = "vn10.3_t977"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Add gather_sync, scatter_sync to namelists
        # and remove MPICH_COLL_SYNC from env
        self.add_setting(config, ["namelist:nlst_mpp", "gather_sync"], ".true.")
        self.add_setting(config, ["namelist:nlst_mpp", "scatter_sync"], ".true.")
        self.remove_setting(config, ["env","MPICH_COLL_SYNC"])
        return config, self.reports


class vn103_t1294(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1294 by Andy Wiltshire."""

    BEFORE_TAG = "vn10.3_t977"
    AFTER_TAG = "vn10.3_t1294"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, ["namelist:jules_vegetation", "l_soil_resp_lev2"], ".false.")
        return config, self.reports


class vn103_t1219(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1219 by James Manners."""

    BEFORE_TAG = "vn10.3_t1294"
    AFTER_TAG = "vn10.3_t1219"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        self.add_setting(config, ["namelist:r2swclnl","l_li_sw"], ".false.")
        self.add_setting(config, ["namelist:r2swclnl","l_li_sw2"], ".false.")
        self.add_setting(config, ["namelist:r2swclnl","l_rb_sw"], ".false.")
        self.add_setting(config, ["namelist:r2swclnl","l_rb_sw2"], ".false.")
        self.add_setting(config, ["namelist:r2swclnl","l_cs_sw"], ".false.")
        self.add_setting(config, ["namelist:r2swclnl","l_cs_sw2"], ".false.")
        self.add_setting(config, ["namelist:r2lwclnl","l_li_lw"], ".false.")
        self.add_setting(config, ["namelist:r2lwclnl","l_li_lw2"], ".false.")
        self.add_setting(config, ["namelist:r2lwclnl","l_rb_lw"], ".false.")
        self.add_setting(config, ["namelist:r2lwclnl","l_rb_lw2"], ".false.")
        self.add_setting(config, ["namelist:r2lwclnl","l_cs_lw"], ".false.")
        self.add_setting(config, ["namelist:r2lwclnl","l_cs_lw2"], ".false.")
        return config, self.reports


class vn103_t1008(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1008 by Dale Roberts."""

    BEFORE_TAG = "vn10.3_t1219"
    AFTER_TAG = "vn10.3_t1008"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        self.add_setting(config, ["namelist:ioscntl", "ios_enable_mpiio"], ".false.")
        return config, self.reports


class vn103_t1314(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1314 by Paul Cresswell."""

    BEFORE_TAG = "vn10.3_t1008"
    AFTER_TAG = "vn10.3_t1314"

    def upgrade(self, config, meta_config=None):
        """Update the value of DR_HOOK."""
        drhook = self.get_setting_value(config, ["env", "DR_HOOK"])
        if drhook == '0':
            self.change_setting_value(config, ["env", "DR_HOOK"], "false")
        else:
            self.change_setting_value(config, ["env", "DR_HOOK"], "true")
        return config, self.reports


class vn103_t1408(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1408 by Eddy Robertson."""

    BEFORE_TAG = "vn10.3_t1314"
    AFTER_TAG = "vn10.3_t1408"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        self.add_setting(config,
            ["namelist:jules_vegetation", "l_trif_crop"],".false.")
        return config, self.reports


class vn103_t1550(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1550 by Adrian Lock."""

    BEFORE_TAG = "vn10.3_t1408"
    AFTER_TAG = "vn10.3_t1550"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Input your macro commands here
        self.add_setting(config, ["namelist:run_stochastic","l_pert_shape"],".false.")
        return config, self.reports


class vn103_t1556(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1556 by Paul Cresswell."""

    BEFORE_TAG = "vn10.3_t1550"
    AFTER_TAG = "vn10.3_t1556"

    def upgrade(self, config, meta_config=None):
        """Update the value of COUPLER."""
        coupler = self.get_setting_value(config, ["env", "COUPLER"])
        if coupler == '':
            self.change_setting_value(config, ["env", "COUPLER"], "none")
        elif coupler == "OASIS3":
            self.change_setting_value(config, ["env", "COUPLER"], "oasis3")
        elif coupler == "OASIS3-MCT":
            self.change_setting_value(config, ["env", "COUPLER"], "oasis3_mct")

        return config, self.reports

class vn103_t1398(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1398 by marcstringer."""

    BEFORE_TAG = "vn10.3_t1556"
    AFTER_TAG = "vn10.3_t1398"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        # Add l_oasis_obgc as false (it will only be true for
        # UKESM specific job, when ocean biogeochemistry is on)
        self.add_setting(config, ["namelist:coupling_control",
                                  "l_oasis_obgc"],".false.")
        return config, self.reports

class vn104_t1450(rose.upgrade.MacroUpgrade):

    BEFORE_TAG = "vn10.3_t1398"
    AFTER_TAG = "GA7-vn10.4_GO6"

    def upgrade(self, config, meta_config=None):
        """Upgrade configuration to next major version."""
        if self.get_setting_value(config, ["env", "VN"]):
            self.change_setting_value(config, ["env", "VN"],
                                      "10.4", forced=True)
        stashmaster_path = self.get_setting_value(config, ["env", "STASHMSTR"])
        if stashmaster_path:
           stashmaster_path = re.sub("vn\d+\.\d+/ctldata",
                                     "vn10.4/ctldata",
                                      stashmaster_path)
           if stashmaster_path == "vn10.4/ctldata":
               self.change_setting_value(config, ["env", "STASHMSTR"],
                                         stashmaster_path, forced=True)
           else:
               self.remove_setting(config, ["env", "STASHMSTR"])
               self.remove_setting(config, ["file:" + stashmaster_path, "source"])
               self.remove_setting(config, ["file:" + stashmaster_path])
                 
        return config, self.reports

