"""淘宝/拼多多全自动远程刷单程序入口模块"""
from pacc.project import SD
from pacc.config import Config

Config.set_debug(True)
SD.mainloop([
    '001001001',
    '001001002',
    '001001003',
    # '001001006', # 易掉线
    '001021001',
    '001021002',
    '001021003',
    '001021005',
    '001021007',
    '001101006',
    '001101011',
    # '001101008',
    '001101009',
    '001024001'
])
