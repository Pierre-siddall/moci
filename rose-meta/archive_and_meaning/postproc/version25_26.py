import re
import sys
if sys.version_info[0] == 2:
    from rose.upgrade import MacroUpgrade
else:
    from metomi.rose.upgrade import MacroUpgrade

class UpgradeError(Exception):

      """Exception created when an upgrade fails."""

      def __init__(self, msg):
          self.msg = msg

      def __repr__(self):
          sys.tracebacklimit = 0
          return self.msg

      __str__ = __repr__


class pp25_t678(MacroUpgrade):

    """Upgrade macro for ticket #678 by pierresiddall."""
    BEFORE_TAG = "postproc_2.5"
    AFTER_TAG = "pp25_t678"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc app configuration to postproc_2.6."""
        try:
            cice_age = self.get_setting_value(config, ["namelist:ciceverify", "cice_age"])
            self.remove_setting(config, ["namelist:ciceverify", "cice_age"])
        except AttributeError:
            cice_age = "false"
        
        self.add_setting(config,["namelist:ciceverify","cice_age_rst"],cice_age)
        base = self.get_setting_value(config, ["namelist:nemo_processing", "base_component"])
        self.add_setting(config,["namelist:nemoverify","base_mean"],base)
        self.add_setting(config,["namelist:nemoverify","nemo_version"],"4.2+")
        self.add_setting(config,["namelist:nemoverify","nemo_ice_rst"],"false")
        self.add_setting(config,["namelist:nemoverify","nemo_icb_rst"],"false")
        
        return config, self.reports
