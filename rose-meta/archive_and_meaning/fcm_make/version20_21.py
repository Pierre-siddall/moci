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


class pp20_t109(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #109 by Erica Neininger."""
    BEFORE_TAG = "postproc_2.0"
    AFTER_TAG = "pp20_t109"

    def upgrade(self, config, meta_config=None):
        """Adding source for new verification app"""

        # Additional source for new verification app
        self.add_setting(config,
                         ["env", "verify_config",],
                         "verify.cfg")

        return config, self.reports


class pp20_t228(rose.upgrade.MacroUpgrade):

    """
    Upgrade macro for ticket #228 by Erica Neininger.
    Version postproc_2.1 release.
    """
    BEFORE_TAG = "pp20_t109"
    AFTER_TAG = "postproc_2.1"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc make app configuration."""
        # Upgrade extract revision keywords
        self.change_setting_value(config, ["env", "config_base"],
                                  "fcm:moci.xm_tr", forced=True)
        self.change_setting_value(config, ["env", "config_rev"],
                                  "@postproc_2.1", forced=True)
        self.change_setting_value(config, ["env", "pp_rev"],
                                  "postproc_2.1", forced=True)

        return config, self.reports
