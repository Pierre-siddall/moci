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



class vn103_t1314(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1314 by Paul Cresswell."""

    BEFORE_TAG = "vn10.3"
    AFTER_TAG = "vn10.3_t1314"

    def upgrade(self, config, meta_config=None):
        """Update the value of OpenMP variables."""
        openmp = self.get_setting_value(config, ["env", "openmp"])
        if openmp == 'openmp_off':
            self.change_setting_value(config, ["env", "openmp"], "false")
        elif openmp == 'openmp_on':
            self.change_setting_value(config, ["env", "openmp"], "true")
        else:
            # Cater for $OPENMP settings:
            warn_openmp = """
        !!! The value of the $openmp variable has changed as follows: !!!
        !!!   openmp_on   ->  true                                    !!!
        !!!   openmp_off  ->  false                                   !!!
        !!! Please update your suite with the new settings.           !!!
            """
            self.add_report(info=warn_openmp, is_warning=True)
        return config, self.reports


class vn103_t1556(rose.upgrade.MacroUpgrade):

    """Upgrade macro for ticket #1556 by Paul Cresswell."""

    BEFORE_TAG = "vn10.3_t1314"
    AFTER_TAG = "vn10.3_t1556"

    def upgrade(self, config, meta_config=None):
        """Add the COUPLER flag based on NEMO FPP keys and rename ocean_exec."""
        keys=self.get_setting_value(config, ["env", "keys_nemo_app"])
        if re.search('key_oasis3mct', keys):
            self.add_setting(config, ["env", "COUPLER"], "oasis3_mct")
        elif re.search('key_oasis3', keys):
            self.add_setting(config, ["env", "COUPLER"], "oasis3")
        else:
            self.add_setting(config, ["env", "COUPLER"], "none")

        self.rename_setting(config, ["env", "ocean_exec"],["env", "OCEAN_EXEC"])

        return config, self.reports

class vn104_t1450(rose.upgrade.MacroUpgrade):

    BEFORE_TAG = "vn10.3_t1556"
    AFTER_TAG = "vn10.4"

    def upgrade(self, config, meta_config=None):
        """Upgrade configuration to next major version."""

        config_revision = self.get_setting_value(config, ['env', 'config_revision'])
        config_root = self.get_setting_value(config, ['env', 'config_root_path'])
        if config_root == '$SOURCE_UM_BASE':
            pass
        else:
            config_root = 'fcm:um.xm_tr'
            config_revision = '@vn10.4'
            self.add_report('env', 'config_root_path', config_root, 
                info='Upgrading fcm_make config version to trunk@vn10.4',
                is_warning=True)
        self.change_setting_value(config, ['env', 'config_revision'], config_revision, forced=True)
        self.change_setting_value(config, ['env', 'config_root_path'], config_root, forced=True)

        prebuild_path = self.get_setting_value(config, ['env', 'prebuild'])
        if prebuild_path == r'$PREBUILD':
            pass
        elif re.search(r'/vn\d+\.\d+_', prebuild_path):
            prebuild_path = re.sub(r'/vn\d+\.\d+_', r'/vn10.4_', prebuild_path)
        elif re.search(r'/r\d+_', prebuild_path):
            prebuild_path = re.sub(r'/r\d+_', r'/vn10.4_', prebuild_path)
        else:
            prebuild_path = ''
        self.change_setting_value(config, ['env', 'prebuild'], prebuild_path, forced=True)

        return config, self.reports

