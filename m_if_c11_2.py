"""闲鱼程序入口C11_2模块"""
# pylint: disable=duplicate-code
from pacc.adb import LDConsole
from pacc.config import Config
from pacc.ld_proj.idle_fish import IdleFish

Config.debug = True
Config.set_ld_work_path()
start_index, end_index = 1, LDConsole.get_last_device_num()
print(f'start_index={start_index}, end_index={end_index}')
# IdleFish.create(end_index)
IdleFish.check_after_run(start_index, end_index)
# IdleFish.login(71, 71)
# IdleFish.confirm(start_index, end_index)
