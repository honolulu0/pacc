"""雷电9_咸鱼程序入口模块"""
from pacc.config import Config
from pacc.ld_proj.idle_fish import IdleFish

Config.set_ld_work_path()
start_index, end_index = 198, 258
# IdleFish.check(start_index, end_index)
IdleFish.mainloop(start_index, end_index)
