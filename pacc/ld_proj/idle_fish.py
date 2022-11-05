"""咸鱼全自动刷咸鱼币中央监控系统模块"""
from datetime import date, datetime, timedelta

from .ld_proj import LDProj
from ..adb import LDConsole, LDADB, LDUIA
from ..base import sleep


class Activity:  # pylint: disable=too-few-public-methods
    """咸鱼全自动刷咸鱼币中央监控系统模块的安卓活动名类"""
    MainActivity = 'com.taobao.idlefish/com.taobao.idlefish.maincontainer.activity.MainActivity'
    UserLoginActivity = 'com.taobao.idlefish/com.ali.user.mobile.login.ui.UserLoginActivity'
    Launcher = 'com.android.launcher3/com.android.launcher3.Launcher'
    ApplicationNotResponding = 'Application Not Responding: com.taobao.idlefish'
    ApplicationError = 'Application Error: com.taobao.idlefish'


class IdleFish(LDProj):
    """咸鱼类"""

    def __init__(self, ld_index=1):
        """构造函数

        :param ld_index: 目标雷电模拟器的索引值
        """
        super().__init__()
        self.ld_index = ld_index

    def run_app(self, sleep_time=60):
        """启动雷电模拟器并运行咸鱼APP"""
        LDConsole(self.ld_index).run_app('com.taobao.idlefish')
        sleep(sleep_time)

    def enter_my_interface(self):
        """进入我的界面"""

    @classmethod
    def check(cls, start_index, end_index):
        """检查是否存在问题

        :param start_index: 起始索引值
        :param end_index: 终止索引值
        """
        src_start_index = start_index
        while True:
            if LDConsole.is_running(start_index):
                LDConsole.quit(start_index)
            cls(start_index).run_app(20)
            current_focus = LDADB(start_index).get_current_focus()
            while Activity.Launcher in current_focus:
                LDConsole.quit(start_index)
                cls(start_index).run_app()
                current_focus = LDADB(start_index).get_current_focus()

            if Activity.UserLoginActivity in current_focus:
                print('检测到已掉线，请登录')
            else:
                LDUIA(start_index).tap((50, 70), 10)
            LDUIA(start_index).get_screen()
            LDConsole.quit(start_index)
            print(f'第{start_index}项已检查完毕\n')
            if start_index >= end_index:
                print(f'所有共{end_index - src_start_index + 1}项已检查完毕')
                break
            start_index += 1

    @classmethod
    def should_restart(cls, dn_index):
        """判断是否需要重启

        :return: 需要重启True，否则返回False
        """
        current_focus = LDADB(dn_index).get_current_focus()
        if Activity.ApplicationNotResponding in current_focus:
            print('检测到咸鱼无响应，正在重启模拟器')
            return True
        if Activity.ApplicationError in current_focus:
            print('检测到咸鱼已停止运行，正在重启模拟器')
            return True
        if Activity.Launcher in current_focus:
            print('检测到咸鱼未正常运行，正在重启模拟器')
            return True
        if Activity.UserLoginActivity in current_focus:
            print('检测到已掉线，请登录')
        return False

    @classmethod
    def run_task(cls, start_index):
        """启动任务

        :param start_index: 起始索引值
        """
        if LDConsole.is_running(start_index):
            LDConsole.quit(start_index)
        if LDConsole.is_running(start_index + 1):
            LDConsole.quit(start_index + 1)
        if LDConsole.is_running(start_index + 2):
            LDConsole.quit(start_index + 2)
        cls(start_index).run_app(10)
        cls(start_index + 1).run_app(30)
        cls(start_index + 2).run_app()
        while cls.should_restart(start_index):
            LDConsole.quit(start_index)
            cls(start_index).run_app()
        while cls.should_restart(start_index + 1):
            LDConsole.quit(start_index + 1)
            cls(start_index + 1).run_app()
        while cls.should_restart(start_index + 2):
            LDConsole.quit(start_index + 2)
            cls(start_index + 2).run_app()
        sleep(99)
        LDConsole.quit(start_index)
        print(f'第{start_index}项已执行完毕')
        LDConsole.quit(start_index + 1)
        print(f'第{start_index + 1}项已执行完毕')
        LDConsole.quit(start_index + 2)
        print(f'第{start_index + 2}项已执行完毕\n')

    @classmethod
    def mainloop(cls, start_index, end_index):
        """主循环

        :param start_index: 起始索引值
        :param end_index: 终止索引值
        """
        src_start_index = start_index
        if datetime.now().hour >= 12:
            start_day = date.today() + timedelta(days=1)
        else:
            start_day = date.today()
        while True:
            while start_day != date.today():
                seconds = (datetime.fromisoformat(
                    f'{date.today() + timedelta(days=1)} 00:00:00') - datetime.now()).seconds
                if seconds > 3600:
                    sleep(3600)
                else:
                    sleep(seconds)
            cls.run_task(start_index)
            if start_index+2 >= end_index:
                print(f'所有共{end_index-src_start_index+1}项已执行完毕')
                start_index = src_start_index - 3
                start_day = date.today() + timedelta(days=1)
            start_index += 3
