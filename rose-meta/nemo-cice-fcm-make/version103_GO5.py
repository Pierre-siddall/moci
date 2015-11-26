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



class vn103_GO5(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #34 by Harry Shepherd."""

    BEFORE_TAG = "vn10.3"
    AFTER_TAG = "GO5"

    def upgrade(self, config, meta_config=None):
        """Upgrade a NEMO-CICE fcm-make app configuration."""
        # Input your macro commands here
        self.change_setting_value(config, ['env', 'config_root_path'],
                                  "'fcm:moci.xm_tr'", forced=True)
        self.change_setting_value(config, ['env', 'config_revision'],
                                  "@209", forced=True)
        
        return config, self.reports

