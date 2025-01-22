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


class pp24_t674(MacroUpgrade):

    """Upgrade macro for ticket #674 by Erica Neininger."""
    BEFORE_TAG = "postproc_2.4"
    AFTER_TAG = "postproc_2.5"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc app configuration to postproc_2.5."""
        # Upgrade extract revision keywords
        self.change_setting_value(config, ["env", "config_base"],
                                  "fcm:moci.xm_tr", forced=True)
        self.change_setting_value(config, ["env", "config_rev"],
                                  "@postproc_2.5", forced=True)
        self.change_setting_value(config, ["env", "pp_rev"],
                                  "postproc_2.5", forced=True)
        return config, self.reports
