"""咸鱼全自动刷咸鱼币中央监控系统模块"""
from .ld_proj import LDProj
from ..adb.ld_console import LDConsole
from ..base import sleep


# pylint: disable=too-few-public-methods
class Activity:
    """咸鱼全自动刷咸鱼币中央监控系统模块的安卓活动名类"""
    MainActivity = 'com.taobao.idlefish/com.taobao.idlefish.maincontainer.activity.MainActivity'


class IdleFish(LDProj):
    """咸鱼模块"""

    def __init__(self, start_index=1):
        super().__init__()
        self.start_index = start_index

    def run_app(self):
        LDConsole(self.start_index).run_app('com.taobao.idlefish')

    def enter_my_interface(self):
        """进入我的界面"""

    @classmethod
    def mainloop(cls, start_index):
        """主循环"""
        while True:
            cls(start_index).run_app()
            sleep(300)
            LDConsole.quit(start_index)
            print(f'第{start_index}项已执行完毕')
            start_index += 1
            if start_index >= 16:
                print('所有项已执行完毕')
                input()
