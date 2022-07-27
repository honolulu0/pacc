"""程序入口模块"""
from pacc.adb import ADB, UIAutomator
from pacc.config import Config
from pacc.tools import EMail

Config.set_debug(True)
DEVICE_SN = '003001002'
adb_ins = ADB(DEVICE_SN)
uia_ins = UIAutomator(DEVICE_SN)
uia_ins.get_current_ui_hierarchy()
# EMail(DEVICE_SN).send_login_alarm()
