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



class vnX_Y(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #<insert MOCI ticket number> by <author>."""

    BEFORE_TAG = "X"
    AFTER_TAG = "Y"

    def upgrade(self, config, meta_config=None):
        """Upgrade a NEMO-CICE fcm-make app configuration."""
        # Input your macro commands here
        
        return config, self.reports

