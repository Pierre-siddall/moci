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


class pp25_tXXX(MacroUpgrade):

    """Upgrade macro for ticket #XXX by <author>."""
    BEFORE_TAG = "postproc_2.5"
    AFTER_TAG = "postproc_2.6"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc app configuration to postproc_2.6."""
        
        return config, self.reports
