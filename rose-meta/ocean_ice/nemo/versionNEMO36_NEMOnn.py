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


class go6_gsi8_v2(rose.upgrade.MacroUpgrade):

    """Upgrade macro to move to nemo36_gsi8_v2 (with extra option for freshwater input from ice shelves)"""

    BEFORE_TAG = "nemo36_gsi8"
    AFTER_TAG = "nemo36_gsi8_v2"

    def upgrade(self, config, meta_config=None):
        """Upgrade a GO6 runtime app configuration."""
        # Input your macro commands here

        ln_coupled_iceshelf_fluxes = self.get_setting_value(config, 
                                        ["namelist:namsbc_cpl", "ln_coupled_iceshelf_fluxes"])

        if ln_coupled_iceshelf_fluxes.lower() == ".true.":
            self.add_setting(config,
                               ["namelist:namsbc_cpl", "nn_coupled_iceshelf_fluxes"],"1")
        else:
            self.add_setting(config,
                               ["namelist:namsbc_cpl", "nn_coupled_iceshelf_fluxes"],"0")
 
        self.remove_setting(config, ["namelist:namsbc_cpl", "ln_coupled_iceshelf_fluxes"])

        # Need to add these to the configuration. Only used if nn_coupled_iceshelf_fluxes is changed
        # to 2 in which case we hope the user will think to set these values to something sensible. 
        self.add_setting(config, ["namelist:namsbc_cpl", "rn_greenland_total_fw_flux"],"0.0")
        self.add_setting(config, ["namelist:namsbc_cpl", "rn_antarctica_total_fw_flux"],"0.0")

        self.change_setting_value(config, ["namelist:domain_nml", "nprocs"],
                                  "'set_by_system'")
        return config, self.reports
