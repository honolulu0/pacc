"""闲鱼全自动刷闲鱼币中央监控系统基类模块"""
# pylint: disable=duplicate-code
from .ld_proj import LDProj
from ..adb import LDConsole, LDADB
from ..base import sleep


class Activity:  # pylint: disable=too-few-public-methods
    """闲鱼全自动刷咸鱼币中央监控系统模块的安卓活动名类"""
    MainActivity = 'com.taobao.idlefish/com.taobao.idlefish.maincontainer.activity.MainActivity'
    UserLoginActivity = 'com.taobao.idlefish/com.ali.user.mobile.login.ui.UserLoginActivity'
    Launcher = 'com.android.launcher3/com.android.launcher3.Launcher'
    ApplicationNotResponding = 'Application Not Responding: com.taobao.idlefish'
    ApplicationError = 'Application Error: com.taobao.idlefish'


class ResourceID:  # pylint: disable=too-few-public-methods
    """闲鱼全自动刷咸鱼币中央监控系统模块的安卓资源ID类"""
    aliuser_login_mobile_et = 'com.taobao.idlefish:id/aliuser_login_mobile_et'
    login_password_btn = 'com.taobao.idlefish:id/login_password_btn'
    confirm = 'com.taobao.idlefish:id/confirm'
    aliuser_login_show_password_btn = 'com.taobao.idlefish:id/aliuser_login_show_password_btn'
    aliuser_login_password_et = 'com.taobao.idlefish:id/aliuser_login_password_et'
    aliuser_login_login_btn = 'com.taobao.idlefish:id/aliuser_login_login_btn'
    aliuser_login_account_et = 'com.taobao.idlefish:id/aliuser_login_account_et'

class IdleFishBase(LDProj):
    """闲鱼基类"""

    def __init__(self, ld_index=1):
        """构造函数

        :param ld_index: 目标雷电模拟器的索引值
        """
        super().__init__()
        self.ld_index = ld_index

    def launch(self):
        """启动雷电模拟器"""
        if LDConsole(self.ld_index).is_exist():
            LDConsole.quit(self.ld_index)
            LDConsole(self.ld_index).launch()
        else:
            print(f'模拟器{self.ld_index}不存在，无法启动')

    def run_app(self, sleep_time=60):
        """启动雷电模拟器并运行咸鱼APP

        :param sleep_time: 等待时间
        """
        if LDConsole(self.ld_index).is_exist():
            LDConsole.quit(self.ld_index)
            LDConsole(self.ld_index).run_app('com.taobao.idlefish', '闲鱼')
        else:
            print(f'设备{self.ld_index}不存在，无法启动')
        sleep(sleep_time)

    def should_restart(self, current_focus=''):
        """判断是否需要重启

        :param current_focus: 当前界面的Activity
        :return: 需要重启True，否则返回False
        """
        if not current_focus:
            current_focus = LDADB(self.ld_index).get_current_focus()
        if Activity.ApplicationNotResponding in current_focus:
            print('检测到咸鱼无响应，正在重启模拟器')
            return True
        if Activity.ApplicationError in current_focus:
            print('检测到咸鱼已停止运行，正在重启模拟器')
            return True
        if Activity.Launcher in current_focus:
            print('检测到咸鱼未正常运行，正在重启模拟器')
            return True
        if 'mCurrentFocus=null' in current_focus:
            print('检测到咸鱼未正常打开，正在重启模拟器')
            return True
        if Activity.UserLoginActivity in current_focus:
            print('检测到已掉线，请登录')
        return False