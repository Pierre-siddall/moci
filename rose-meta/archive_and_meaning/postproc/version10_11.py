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


class pp10_t48(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #48 by EricaNeininger."""
    BEFORE_TAG = "postproc_1.0"
    AFTER_TAG = "pp10_t48"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc app configuration."""

        self.add_setting(config,
                         ["namelist:suitegen", "nccopy_path",], "")
        self.add_setting(config,
                         ["namelist:nemopostproc", "compress_means",],
                         "'nccopy'")
        self.add_setting(config,
                         ["namelist:cicepostproc", "compress_means",],
                         "'nccopy'")
        self.add_setting(config,
                         ["namelist:nemopostproc", "compression_level",], "0")
        self.add_setting(config,
                         ["namelist:cicepostproc", "compression_level",], "0")
        self.add_setting(config,
                         ["namelist:nemopostproc", "chunking_arguments",],
                         "time_counter/1,y/205,x/289")
        self.add_setting(config,
                         ["namelist:cicepostproc", "chunking_arguments",],
                         "time/1,nc/1,ni/288,nj/204")

        return config, self.reports
