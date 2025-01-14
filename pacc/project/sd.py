"""淘宝/拼多多全自动远程刷单APP中央监控系统模块"""
from datetime import datetime
from xml.parsers.expat import ExpatError

from .project import Project
from ..base import show_datetime, sleep, print_err

ROOT = 'com.dd.rclient/com.dd.rclient.ui.activity.'
PDD_ROOT = 'com.xunmeng.pinduoduo'
TB_ROOT = 'com.taobao.taobao'


# pylint: disable=too-few-public-methods
class Activity:
    """淘宝/拼多多全自动远程刷单APP中央控制系统模块的安卓活动名类"""
    MainActivity = f'{ROOT}MainActivity'  # 主界面
    LoginActivity = f'{ROOT}LoginActivity'  # 登录


# pylint: disable=too-few-public-methods
class ResourceID:
    """淘宝/拼多多全自动远程刷单APP中央控制系统模块的安卓资源ID类"""
    # 确定（联机业务异常，请重新联机）、立即连接（连接异常，正在重新连接......）
    # （切换账号将会结束您当前的挂机，是否继续？）
    button2 = 'android:id/button2'  # 确定或等待（滴滴助手无响应。要将其关闭吗？）
    button1 = 'android:id/button1'  # 取消或【确定（淘宝无响应。要将其关闭吗？）】
    auto_wait_btn = 'com.dd.rclient:id/auto_wait_btn'
    # 连接状态信息：【正在连接服务器...】、【已连接到服务器,等待控制端连接】
    mec_connect_state = 'com.dd.rclient:id/mec_connect_state'
    btn_exit_app = 'com.dd.rclient:id/btn_exit_app'  # 退出程序
    icon_title = 'com.miui.home:id/icon_title'  # 桌面图标
    message = 'android:id/message'  # 切换账号将会结束您当前的挂机,是否继续?
    # 【小米手机】
    miui_message = 'miui:id/message'  # 淘宝无响应。要将其关闭吗？
    # 【华为手机】
    alertTitle = 'android:id/alertTitle'  # 【滴滴助手 无响应。是否将其关闭？】
    aerr_wait = 'android:id/aerr_wait'  # 华为手机等待按钮（滴滴助手 无响应。是否将其关闭？）


class SD(Project):
    """刷单类"""

    offline_devices = []
    home_devices = []

    # pylint: disable=too-many-return-statements, too-many-branches, too-many-statements
    def check(self):
        """检查

        :return: 状态正常返回True，否则返回False
        """
        show_datetime(f'检查设备{self.serial_num}', start_br=True)
        if datetime.now().hour == 3:
            print('当前正值自动开关机时段，无需额外检查\n')
            return True
        if not self.adb_ins.is_online():
            print('当前设备不在线，无法检查')
            self.__class__.offline_devices.append(self.serial_num)
        current_focus = self.adb_ins.get_current_focus()
        if TB_ROOT in current_focus:
            print('淘宝正在运行，无需额外检查\n')
            return True
        if PDD_ROOT in current_focus:
            print('拼多多正在运行，无需额外检查\n')
            return True
        if 'com.miui.home/com.miui.home.launcher.Launcher' in current_focus or \
                'com.huawei.android.launcher/com.huawei.android.launcher.unihome.' \
                'UniHomeLauncher' in current_focus:
            if self.serial_num in self.__class__.home_devices:
                self.reopen_app()
                self.__class__.home_devices.remove(self.serial_num)
                return self.check()
            print(f'第一次检测到设备{self.serial_num}桌面正在运行，无需额外检查\n')
            self.__class__.home_devices.append(self.serial_num)
            return True
        if self.serial_num in self.__class__.home_devices:
            self.__class__.home_devices.remove(self.serial_num)
        if 'mCurrentFocus=null' in current_focus:
            print('无法正常获取当前正在运行的程序信息，无法进行检查\n')
            return False
        try:
            dic = self.uia_ins.get_dict(ResourceID.message)
        except (FileNotFoundError, ExpatError):
            print('无法正常获取当前用户界面上元素的层次布局信息，无法进行检查')
            return False
        if 'Application Not Responding' in current_focus and self.uia_ins.get_dict(
                ResourceID.miui_message, xml=self.uia_ins.xml) and '淘宝无响应。要将其关闭吗？' in self.\
                uia_ins.get_dict(ResourceID.miui_message, xml=self.uia_ins.xml)['@text']:
            print('淘宝无响应，正在将其关闭。')
            self.uia_ins.click(ResourceID.button1, xml=self.uia_ins.xml)
            return False
        if dic and dic['@text'] == '切换账号将会结束您当前的挂机,是否继续?':
            self.uia_ins.click(ResourceID.button1, xml=self.uia_ins.xml)
            self.uia_ins.xml = ''
        click_cnt = 0
        try:
            while self.uia_ins.click(ResourceID.button2, '等待', xml=self.uia_ins.xml) or self.\
                    uia_ins.click(ResourceID.aerr_wait, '等待', xml=self.uia_ins.xml):
                click_cnt += 1
                print(f'click_cnt={click_cnt}')
                self.uia_ins.xml = ''
        except FileNotFoundError as err:
            print_err(err)
        if click_cnt:
            sleep(60)
            if 'Application Not Responding: com.dd.rclient' in self.adb_ins.get_current_focus():
                print('滴滴助手无响应，正在将其关闭。')
                self.uia_ins.click(ResourceID.button1, xml=self.uia_ins.xml)
                self.reopen_app()
            return self.check()
        dic = self.uia_ins.get_dict(ResourceID.mec_connect_state, xml=self.uia_ins.xml)
        if dic and dic['@text'] == '正在连接服务器...':
            self.reopen_app()
        elif not dic and Activity.MainActivity in current_focus:
            try:
                self.reopen_app()
            except FileNotFoundError as err:
                print_err(err)
            return self.check()
        if Activity.LoginActivity in current_focus:
            self.adb_ins.reboot()
            sleep(600)
            self.open_app()
            # if Activity.LoginActivity in self.adb_ins.get_current_focus():
            #     EMail(self.serial_num).send_offline_error()
        print('检查结束，未发现不可处理异常\n')
        return True

    def reopen_app(self):
        """重新打开APP"""
        self.exit_app()
        self.open_app()

    def open_app(self):
        """打开淘宝/拼多多全自动远程刷单APP"""
        self.free_memory()
        if not self.uia_ins.click(text='滴滴助手'):
            self.uia_ins.tap((82, 1862))
            self.uia_ins.click(text='滴滴助手')
        sleep(12)
        self.uia_ins.click(ResourceID.auto_wait_btn)
        self.uia_ins.click(ResourceID.button1)

    def exit_app(self):
        """退出APP"""
        self.uia_ins.click(ResourceID.btn_exit_app, xml=self.uia_ins.xml)
        self.uia_ins.click(ResourceID.button2)

    @classmethod
    def mainloop(cls, devices_sn):
        """主循环函数

        :param devices_sn: 多个设备的编号
        """
        instances = [cls(device_sn) for device_sn in devices_sn]
        while True:
            cls.offline_devices.clear()
            for ins in instances:
                ins.check()
            if cls.offline_devices:
                print(f'离线设备：{cls.offline_devices}')
            if cls.home_devices:
                print(f'桌面设备：{cls.home_devices}')
            sleep(600)
