"""程序入口模块"""
# pylint: disable=unused-import
from pacc import get_version
from pacc.adb import ADB, UIAutomator
from pacc.base import print_err
from pacc.config import Config
from pacc.project.ksjsb.resource_id import ResourceID

# get_version()

Config.set_debug(True)
DEVICE_SN = '002004003'
adb_ins = ADB(DEVICE_SN)
uia_ins = UIAutomator(DEVICE_SN)
# uia_ins.click('com.jifen.qukan:id/a0m')
try:
    uia_ins.get_current_ui_hierarchy()
except FileNotFoundError as err:
    print_err(err)
