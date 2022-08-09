"""程序入口模块"""
from pacc.adb import ADB, UIAutomator
# pylint: disable=unused-import
from pacc.base import print_err
from pacc.config import Config
from pacc.project.ksjsb.resource_id import ResourceID

Config.set_debug(True)
DEVICE_SN = '003001001'
# DEVICE_SN = '003001002'
adb_ins = ADB(DEVICE_SN)
uia_ins = UIAutomator(DEVICE_SN)
# uia_ins.get_texts_from_screen(True)
# try:
#     uia_ins.get_current_ui_hierarchy()
# except FileNotFoundError as err:
#     print_err(err)