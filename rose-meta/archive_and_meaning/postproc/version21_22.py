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


class pp21_t194(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #194 by EricaNeininger."""
    BEFORE_TAG = "postproc_2.1"
    AFTER_TAG = "pp21_t194"

    def upgrade(self, config, meta_config=None):
        """Upgrade a Postproc app configuration."""
        self.add_setting(config,
                         ["namelist:suitegen", "process_toplevel",],
                         "true")
        self.add_setting(config,
                         ["namelist:suitegen", "archive_toplevel",],
                         "true")

        self.add_setting(config, ["namelist:suitegen", "ncks_path",], "")
        self.add_setting(config,
                         ["namelist:nemopostproc", "extract_region"], "false")
        self.add_setting(config,
                         ["namelist:nemopostproc", "region_dimensions"],
                         'x,1055,1198,y,850,1040')
        self.add_setting(config,
                         ["namelist:nemopostproc", "region_chunking_args"],
                         'time_counter/1,y/191,x/144')

        # Moving diagnostic namelist around
        fields = self.get_setting_value(config,
                                        ["namelist:nemoverify", "fields"])
        self.add_setting(config,
                         ["namelist:nemoverify", "meanfields"], fields)
        self.remove_setting(config,
                            ["namelist:nemoverify", "fields"])

        for model in ['nemo', 'cice']:
              work = self.get_setting_value(config,
                                            ["namelist:%spostproc" % model,
                                             "means_directory"])
              self.add_setting(config,
                               ["namelist:%spostproc" % model, "work_directory"],
                               work)
              self.remove_setting(config, ["namelist:%spostproc" % model,
                                           "means_directory"])

              compress = self.get_setting_value(config,
                                                ["namelist:%spostproc" % model,
                                                 "compress_means"])
              self.add_setting(config,
                               ["namelist:%spostproc" % model, "compress_netcdf"],
                               compress)
              self.remove_setting(config, ["namelist:%spostproc" % model,
                                           "compress_means"])

              # Update verification for concatenated streams due to change in syntax
              streams = self.get_setting_value(config,
                                               ["namelist:%sverify" % model, "meanstreams"])
              self.change_setting_value(config, ["namelist:%sverify" % model, "meanstreams"],
                                        streams.replace('_30','_1m'), forced=True)

        return config, self.reports
