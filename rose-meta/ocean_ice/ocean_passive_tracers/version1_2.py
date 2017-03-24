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


class OPT_v1_tXXXX(rose.upgrade.MacroUpgrade):

    """Upgrade macro for MOCI ticket #XXXX by <Author>."""

    BEFORE_TAG = "OPT-v1"
    AFTER_TAG = "OPT-v1_tXXXX"

    def upgrade(self, config, meta_config=None):
        """Upgrade an Ocean Passive Tracers make app configuration."""
        # Input your macro commands here 
        return config, self.reports




