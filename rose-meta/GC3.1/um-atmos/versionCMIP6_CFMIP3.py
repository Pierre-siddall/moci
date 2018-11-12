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



class CMIP6_CFMIP3_branches(rose.upgrade.MacroUpgrade):

    """Upgrade macro for CFMIP3 "Version" release."""

    BEFORE_TAG = "vn10.7_CMIP6_production_mods"
    AFTER_TAG = "vn10.7_CMIP6_CFMIP3_branches"

    def upgrade(self, config, meta_config=None):
        """Upgrade a UM runtime app configuration."""
        
        stashmaster_path = self.get_setting_value(config, ["env", "STASHMASTER"])
        stash_source = "fcm:um.xm_br/pkg/alejandrobodas/vn10.7_CMIP6_CFMIP3_branches/" + \
            "rose-meta/um-atmos/HEAD/etc/stash/STASHmaster@58955"
        if stashmaster_path:
            self.change_setting_value(config, ["env", "STASHMASTER"], "STASHmaster")
        else:
            self.add_setting(config, ["env", "STASHMASTER"], "STASHmaster")

        stash_file = self.get_setting_value(config, ["file:STASHmaster", "source"])
        if stash_file:
            self.change_setting_value(config, ["file:STASHmaster", "source"], stash_source)
        else:
           self.add_setting(config, ["file:STASHmaster", "source"], stash_source) 
        

        return config, self.reports

