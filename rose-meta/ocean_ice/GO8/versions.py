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


class nemo4_0_si3(rose.upgrade.MacroUpgrade):

    """Upgrade macro for NEMO 4 beta to NEMO 4.0"""

    BEFORE_TAG = "nemo40beta_si3"
    AFTER_TAG = "nemo4.0_si3"

    def upgrade(self, config, meta_config=None):
        """Upgrade a GO8 runtime app configuration."""
        # Input your macro commands here

        self.remove_setting(config, ["namelist:namdyn", "ln_dynadv"])
        self.remove_setting(config, ["namelist:namdyn", "ln_dynfull"])

        self.add_setting(config,["namelist:namdyn", "ln_dynadv2d"],".false.")
        self.add_setting(config,["namelist:namdyn", "ln_dynadv1d"],".false.")
        self.add_setting(config,["namelist:namdyn", "ln_dynall"],".true.")

        self.remove_setting(config, ["namelist:namdyn", "ln_landfast"])
        self.remove_setting(config, ["namelist:namdyn", "rn_gamma"])

        self.add_setting(config,["namelist:namdyn", "ln_landfast_home"],".false.")
        self.add_setting(config,["namelist:namdyn", "ln_landfast_l16"],".false.")
        self.add_setting(config,["namelist:namdyn", "rn_depfra"],"0.125")
        self.add_setting(config,["namelist:namdyn", "rn_tensile"],"0.2")

        self.remove_setting(config, ["namelist:nammpp", "jpnij"])

        self.remove_setting(config, ["namelist:nampar", "nn_virtual_itd"])
        self.add_setting(config,["namelist:nampar", "ln_virtual_itd"],".false.")
 
        self.remove_setting(config, ["namelist:namthd_pnd", "ln_pnd_fwb"])

        # rn_ahm_0 is a hangover from NEMO 3.6 which exists as an ignored parameter
        # in the standard NEMO 4 beta suites and if we don't remove it the upgrade
        # macro will "unignore" it because there is no trigger to say it should be 
        # ignored. So just get rid of it where it exists.
        try:
            self.remove_setting(config, ["namelist:namdyn_ldf", "rn_ahm_0"])
        except:
	   print("Don't need to remove rn_ahm_0.")	   

        # Add in ln_shlat2d if not already in the configuration. 
        try:
            ln_shlat2d = self.get_setting_value(config,["namelist:namlbc", "ln_shlat2d"])
        except:
            self.add_setting(config,["namelist:namlbc", "ln_shlat2d"],".false.")

        return config, self.reports
