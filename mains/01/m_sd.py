"""淘宝/拼多多全自动远程刷单程序入口"""
from pacc.project import SD
from pacc.config import Config

Config.set_debug(True)
# SD.mainloop(['001021003'])
SD.mainloop([
    # '001001001',
    '001001002',
    '001001003',
    '001001004',
    '001001005',
    '001011001',
    '001021001',
    '001021002',
    '001021003',
    '001021004',
    '001021005',
    '001021006',
])