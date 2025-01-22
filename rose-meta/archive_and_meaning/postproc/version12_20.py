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


class pp12_pp20(MacroUpgrade):

    """Upgrade macro for Version 2.0 Release (#142)"""
    BEFORE_TAG = "postproc_1.2"
    AFTER_TAG = "postproc_2.0"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc make app configuration."""
        # No changes required
        return config, self.reports
