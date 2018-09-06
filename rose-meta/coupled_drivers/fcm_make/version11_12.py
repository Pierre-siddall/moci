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


class drivers11_t345(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #345 by Harry Shepherd."""
    BEFORE_TAG = "drivers_1.1"
    AFTER_TAG = "drivers_1.2"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Driver make app configuration."""
        # Input your macro commands here
        self.change_setting_value(config, ["env", "config_rev"],
                                  "@drivers_1.2")
        self.change_setting_value(config, ["env", "driver_rev"],
                                  "drivers_1.2")
        return config, self.reports
