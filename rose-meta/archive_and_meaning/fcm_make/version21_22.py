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


class pp21_tXXX(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #XXX by <Author>."""
    BEFORE_TAG = "postproc_2.1"
    AFTER_TAG = "pp21_tXXX"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc make app configuration."""
        # Add changes here...

        return config, self.reports

