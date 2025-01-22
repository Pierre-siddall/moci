import re
import sys
import os
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


class pp11_t75(MacroUpgrade):

    """Upgrade macro for ticket #75 by EricaNeininger."""
    BEFORE_TAG = "postproc_1.1"
    AFTER_TAG = "pp11_t75"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc app configuration."""
        self.add_setting(config,
                         ["namelist:cicepostproc", "means_to_archive",], None)
        self.add_setting(config,
                         ["namelist:cicepostproc", "base_component",], '10d')
        self.add_setting(config,
                         ["namelist:nemopostproc", "means_to_archive",], None)
        self.add_setting(config,
                         ["namelist:nemopostproc", "base_component",], '10d')
        return config, self.reports


class pp11_t76(MacroUpgrade):

    """Upgrade macro for ticket #76 by EricaNeininger."""
    BEFORE_TAG = "pp11_t75"
    AFTER_TAG = "pp11_t76"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc app configuration."""
        self.add_setting(config,
                         ["namelist:nemopostproc",
                          "archive_iceberg_trajectory",], 'false')
        return config, self.reports


class pp11_t37(MacroUpgrade):

    """Upgrade macro for ticket #37 by EricaNeininger."""
    BEFORE_TAG = "pp11_t76"
    AFTER_TAG = "pp11_t37"

    def upgrade(self, config, meta_config=None):
        """
        New options to allow individual fieldsfiles to be converted
        to pp format at the user's discretion.
        """
        self.add_setting(config, ["namelist:archiving",
                                  "convert_all_streams",], "true")
        self.add_setting(config, ["namelist:archiving",
                                  "archive_as_fieldsfiles",], None)
        return config, self.reports


class pp11_t80(MacroUpgrade):

    """Upgrade macro for ticket #80 by harryshepherd."""
    BEFORE_TAG = "pp11_t37"
    AFTER_TAG = "pp11_t80"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc app configuration."""
        # Input your macro commands here
        self.add_setting(config,
                         ["file:monitorpp.nl", "source"],
                         "namelist:monitoring")
        self.add_setting(config,
                         ["namelist:monitoring", "ltimer"],
                         "false")
        
        return config, self.reports


class pp11_t98(MacroUpgrade):

    """Upgrade macro for ticket #98 by EricaNeininger."""
    BEFORE_TAG = "pp11_t80"
    AFTER_TAG = "pp11_t98"

    def upgrade(self, config, meta_config=None):
        """New options to allow processing of selected streams."""
        self.add_setting(config, ["namelist:archiving",
                                  "process_all_streams",], "true")
        self.add_setting(config, ["namelist:archiving",
                                  "process_streams",], 'a-z1-9')
        self.add_setting(config, ["namelist:archiving",
                                  "process_means",], 'msy')
        
        self.add_setting(config, ["namelist:nemopostproc",
                                  "process_all_fieldsfiles",], "true")
        self.add_setting(config, ["namelist:nemopostproc",
                                  "means_fieldsfiles",],
                         "grid_U,grid_V,grid_W,grid_T")
        return config, self.reports


class pp11_t112(MacroUpgrade):

    """Upgrade macro for ticket #112 by <Erica Neininger>."""
    BEFORE_TAG = "pp11_t98"
    AFTER_TAG = "pp11_t112"

    def upgrade(self, config, meta_config=None):
        """New options for calling ncrcat from CICE."""
        self.add_setting(config,
                         ["namelist:suitegen", "ncrcat_path",], "")
        self.add_setting(config,
                         ["namelist:cicepostproc", "cat_daily_means",], "false")        
        return config, self.reports


class pp11_t18(MacroUpgrade):
    """Upgrade macro for ticket #18 by EricaNeininger."""
    BEFORE_TAG = "pp11_t112"
    AFTER_TAG = "pp11_t18"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc app configuration."""
        self.remove_setting(config, ["namelist:suitegen", "tasks_per_cycle"])
        return config, self.reports


class pp11_pp12(MacroUpgrade):

    """Upgrade macro for Version 1.2 Release."""
    BEFORE_TAG = "pp11_t18"
    AFTER_TAG = "postproc_1.2"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc make app configuration."""
        # No changes required
        return config, self.reports
