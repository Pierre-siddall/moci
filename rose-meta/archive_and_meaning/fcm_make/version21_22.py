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


class pp21_t280(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #280 by Erica Neininger."""
    BEFORE_TAG = "postproc_2.1"
    AFTER_TAG = "postproc_2.2"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc make app configuration."""
       # Upgrade extract revision keywords
        self.change_setting_value(config, ["env", "config_base"],
                                  "fcm:moci.xm_tr", forced=True)
        self.change_setting_value(config, ["env", "config_rev"],
                                  "@postproc_2.2", forced=True)
        self.change_setting_value(config, ["env", "pp_rev"],
                                  "postproc_2.2", forced=True)

        return config, self.reports

