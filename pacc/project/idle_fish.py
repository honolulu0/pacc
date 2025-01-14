"""闲鱼中控模块"""
from os import listdir, remove
from os.path import join
from random import randint
from xml.parsers.expat import ExpatError
from datetime import date, timedelta, datetime

from .project import Project
from ..base import sleep, print_err
from ..mysql import RetrieveIdleFish, RetrieveIdleFishByConsignee, RetrieveIdleFishByOrderNum, \
    CreateRecordDispatch, UpdateIdleFish
from ..tools import get_now_time
from ..config import Config

ROOT = 'com.taobao.idlefish/com.taobao.idlefish.maincontainer.activity.'


class Activity:  # pylint: disable=too-few-public-methods
    """闲鱼中控模块的安卓活动名类"""
    MainActivity = f'{ROOT}MainActivity'  # 主界面
    BlackBoxMainActivity = 'top.niunaijun.blackboxa64/' \
                           'top.niunaijun.blackboxa.view.main.MainActivity'


class ResourceID:  # pylint: disable=too-few-public-methods
    """闲鱼中控模块的安卓资源ID类"""
    tab_title = 'com.taobao.idlefish:id/tab_title'
    btn_transfer = 'com.taobao.idlefish:id/btn_transfer'
    publish_rate = 'com.taobao.idlefish:id/publish_rate'
    right_btn = 'com.taobao.idlefish:id/right_btn'
    toolbar_layout = 'top.niunaijun.blackboxa64:id/toolbar_layout'


class IdleFish(Project):
    """闲鱼中控类"""

    def __init__(self, serial_num):
        """构造函数

        :param serial_num: 设备编号
        """
        super().__init__(serial_num)
        self.walked_li = []

    def open_black_box(self) -> None:
        """打开BlackBox应用"""
        self.free_memory()
        self.adb_ins.open_app(Activity.BlackBoxMainActivity)
        sleep(5)

    def run_task(self):
        """执行任务"""
        self.open_black_box()
        dic = self.uia_ins.get_dict(ResourceID.toolbar_layout)
        print(dic)
        self.uia_ins.get_current_ui_hierarchy()
        self.uia_ins.get_screen()

    @classmethod
    def get_aps(cls):
        """获取所有支付宝的代付码

        :return: 所有支付宝的代付码
        """
        ap_li = []
        for i in listdir(Config.aps_path)[::-1]:
            spli = i.split('.')
            if spli and spli[-1] == 'png':
                ap_li.append(i)
        return ap_li

    def get_random_ap(self, random_err=0):
        """随机获取一个支付宝的代付码

        :param random_err: 错误的数量
        :return: 当代付码存在时会尽可能地随机返回一个未曾遍历过的代付码，当代付码不存在时返回None
        """
        ap_li = self.__class__.get_aps()
        if ap_li:
            random_ap = ap_li[randint(0, len(ap_li) - 1)]
            if len(ap_li) <= len(self.walked_li):
                self.walked_li = []
            if random_err > 10 or random_ap not in self.walked_li:
                self.walked_li.append(random_ap)
                return random_ap
            return self.get_random_ap(random_err + 1)
        return None

    def get_changed_ap(self):
        """获取一个已改过价的支付宝代付码

        :return: 当已改过价的代付码存在时会返回其中的一个已改过价的代付码，当不存在已改过价的代付码时直接返回None
        """
        ap_li = self.__class__.get_aps()
        if ap_li:
            for ap_code in ap_li:
                job_number = ap_code[4:-4]
                retrieve_ins = RetrieveIdleFish(job_number)
                # print(f'ap={ap}, job_number={job_number}, last_change_price_date='
                #       f'{retrieve_ins.last_change_price_date}, {date.today()}')
                if len(ap_li) <= len(self.walked_li):
                    self.walked_li = []
                if ap_code in self.walked_li:
                    continue
                if retrieve_ins.last_change_price_date == date.today():
                    self.walked_li.append(ap_code)
                    return ap_code
        return None

    def open_app(self):
        """打开闲鱼APP"""
        self.free_memory()
        self.adb_ins.open_app(Activity.MainActivity)
        sleep(6)

    def pay(self):
        """付款"""
        time_cnt = 0
        while True:
            random_ap = self.get_changed_ap()
            if not random_ap:
                print(f'time_cnt={time_cnt}')
                sleep(10)
                time_cnt += 10
                continue
            time_cnt = 0
            alipay_code = join(Config.aps_path, random_ap)
            print(f'alipay_code={alipay_code}, self.walked_li={self.walked_li}')
            self.adb_ins.push_pic(alipay_code)
            self.free_memory()
            if not self.uia_ins.click(text='支付宝', interval=15):
                self.uia_ins.click('android:id/button2')
                continue
            try:
                if not self.uia_ins.click(text='扫一扫'):
                    continue
                self.uia_ins.tap((939, 1399))
                self.uia_ins.click('com.alipay.mobile.beephoto:id/iv_photo')
            except (FileNotFoundError, ExpatError) as err:
                print_err(err)
                continue
            self.uia_ins.click('com.alipay.mobile.beephoto:id/bt_finish', interval=12)
            if self.uia_ins.get_dict(text='照片中未识别到二维码'):
                remove(alipay_code)
                self.free_memory()
                continue
            try:
                if not self.uia_ins.click(
                        text='确认付款', index='8', xml=self.uia_ins.xml, interval=2) and not self. \
                        uia_ins.click(text='确认付款', index='9', xml=self.uia_ins.xml, interval=2):
                    remove(alipay_code)
                    continue
                self.uia_ins.click(text='继续支付', interval=3)
                if not self.uia_ins.click(text='确认交易'):
                    continue
            except FileNotFoundError as err:
                print_err(err)
                continue
            self.uia_ins.click('com.alipay.mobile.antui:id/au_num_1', interval=0.01)
            for i in '39499':
                self.uia_ins.click(f'com.alipay.mobile.antui:id/au_num_{i}',
                                   xml=self.uia_ins.xml, interval=0.01)
            sleep(5)
            if self.uia_ins.get_dict(text='代付成功'):
                try:
                    remove(alipay_code)
                except PermissionError as err:
                    print(err)

    def change_price(self) -> None:  # pylint: disable=too-many-branches, too-many-statements
        """改价"""
        success_cnt = 0
        time_cnt = 0
        while True:
            print(f'success_cnt={success_cnt}, time_cnt={time_cnt}')
            ap_li = self.__class__.get_aps()
            print(f'ap_li={ap_li}')
            if not ap_li:
                time_cnt += 1
                sleep(1)
                continue
            time_cnt = 0
            self.open_app()
            self.adb_ins.get_current_focus()
            try:
                self.uia_ins.click(content_desc='我的，未选中状态', interval=0.01)
            except FileNotFoundError as err:
                print_err(err)
                continue
            self.uia_ins.click(content_desc='我卖出的', interval=0.01)
            self.uia_ins.click(content_desc='待付款', interval=0.01)
            index_list = []
            try:
                dic = self.uia_ins.get_dict(index='0', content_desc='等待买家付款')['node'][1]
            except TypeError as err:
                print_err(f'1 err={err}')
                dic = None
            if dic:
                if '¥0.01' in dic['@content-desc']:
                    print('1 已改')
                else:
                    index_list.append('0')
            try:
                dic = self.uia_ins.get_dict(
                    index='1', content_desc='等待买家付款', xml=self.uia_ins.xml)['node'][1]
            except TypeError as err:
                print_err(f'2 err={err}')
                dic = None
            if dic:
                if '¥0.01' in dic['@content-desc']:
                    print('2 已改')
                else:
                    index_list.append('1')
            try:
                dic = self.uia_ins.get_dict(
                    index='2', content_desc='等待买家付款', xml=self.uia_ins.xml)['node'][1]
            except TypeError as err:
                print_err(f'3 err={err}')
                dic = None
            if dic:
                if '¥0.01' in dic['@content-desc']:
                    print('3 已改')
                else:
                    index_list.append('2')
            try:
                dic = self.uia_ins.get_dict(
                    index='3', content_desc='等待买家付款', xml=self.uia_ins.xml)['node'][1]
            except TypeError as err:
                print_err(f'4 err={err}')
                dic = None
            if dic:
                if '¥0.01' in dic['@content-desc']:
                    print('4 已改')
                else:
                    index_list.append('3')
            print(f'index_list={index_list}')
            if not index_list:
                continue
            self.uia_ins.click(
                index=index_list[-1], content_desc='等待买家付款', xml=self.uia_ins.xml)
            try:
                raw_order_num = self.uia_ins.get_dict(content_desc='订单编号')['@content-desc']
            except TypeError as err:
                print_err(err)
                continue
            order_num = (str(raw_order_num).split('\n'))[1]
            print(f'order_num={order_num}')
            job_number = RetrieveIdleFishByOrderNum(order_num).job_number
            if not job_number:
                continue
            print(job_number)
            update_idle_fish_ins = UpdateIdleFish(job_number=job_number)
            self.uia_ins.click(content_desc='修改价格', xml=self.uia_ins.xml)
            dic = self.uia_ins.get_dict(class_='android.widget.EditText')
            try:
                src_price = float(dic['@text'])
            except TypeError as err:
                print_err(err)
                continue
            if str(src_price)[-1] == '1':
                continue
            price = src_price / 10 + 0.01
            print(f'price={price}')
            self.uia_ins.click(class_='android.widget.EditText', interval=0.01)
            self.adb_ins.input_text(price)
            self.uia_ins.click(content_desc='确定修改', interval=0.01)
            if self.uia_ins.click(content_desc='确定', index='1', interval=0.01):
                update_idle_fish_ins.update_last_change_price_date(date.today())
                success_cnt += 1

    def get_dispatch_address(self, point):  # pylint: disable=too-many-locals
        """获取发货时的地址

        :param point: 点的x和y坐标
        :return: 发货时的地址
        """
        self.uia_ins.tap(point, 2)
        address_dic = self.uia_ins.get_dict('root')['node']['node'][2]['node'][3]['node']
        name_mobile = str(address_dic[0]['@text']).split()
        name, mobile = name_mobile[0], name_mobile[1]
        dispatch_consignee = f'N={name}, M={mobile}'
        print(dispatch_consignee)
        dispatch_date = date.today()
        job_number = RetrieveIdleFishByConsignee(dispatch_consignee).job_number
        dispatch_time = get_now_time()
        retrieve_ins = RetrieveIdleFish(job_number)
        role = retrieve_ins.role
        user_name = retrieve_ins.user_name
        pay_pw = retrieve_ins.pay_pw
        if_mn = retrieve_ins.if_mn
        buy_coins = retrieve_ins.last_buy_coins
        buy_date = retrieve_ins.last_buy_date
        buy_time = retrieve_ins.last_buy_time
        confirm_date = dispatch_date + timedelta(days=10)
        base_payee = retrieve_ins.base_payee
        middle_payee = retrieve_ins.middle_payee
        print(
            f'dispatch_date={dispatch_date}, job_number={job_number}, '
            f'dispatch_time={dispatch_time}, role={role}, '
            f'user_name={user_name}, pay_pw={pay_pw}, '
            f'if_mn={if_mn}, buy_coins={buy_coins}, '
            f'buy_date={buy_date}, buy_time={buy_time}, \n'
            f'dispatch_consignee={dispatch_consignee}, confirm_date={confirm_date}, '
            f'confirm_time={dispatch_time}, \nbase_payee={base_payee}, '
            f'middle_payee={middle_payee}'
        )
        CreateRecordDispatch(
            dispatch_date=dispatch_date, job_number=job_number,
            dispatch_time=dispatch_time, role=role,
            user_name=user_name, pay_pw=pay_pw,
            if_mn=if_mn, buy_coins=buy_coins,
            buy_date=buy_date, buy_time=buy_time,
            dispatch_consignee=dispatch_consignee, confirm_date=confirm_date,
            confirm_time=dispatch_time, base_payee=base_payee,
            middle_payee=middle_payee,
        )
        update_idle_fish_ins = UpdateIdleFish(job_number=job_number)
        update_idle_fish_ins.update_last_dispatch_date(dispatch_date)
        update_idle_fish_ins.update_last_dispatch_time(dispatch_time)
        # input()
        return dispatch_consignee

    def should_pay(self):
        """判断是否需要付款（待付款是否有订单）"""
        self.open_app()
        self.uia_ins.click(content_desc='我的，未选中状态', interval=0.01)
        self.uia_ins.click(content_desc='我卖出的', interval=0.01)
        self.uia_ins.click(content_desc='待付款', interval=0.01)
        if self.uia_ins.get_dict(content_desc='等待买家付款'):
            print('有订单未付款，请先处理')
            input()

    def dispatch(self, err_num=3):  # pylint: disable=too-many-branches, too-many-statements
        """发货

        :param err_num: 结束时的连续错误阈值
        """
        hour = datetime.now().hour
        while hour >= 3:
            print(hour)
            # pylint: disable=duplicate-code
            seconds = (datetime.fromisoformat(
                f'{date.today() + timedelta(days=1)} 00:00:00') - datetime.now()).seconds
            if seconds > 3600:
                sleep(3600)
            else:
                sleep(seconds)
            hour = datetime.now().hour
        self.should_pay()
        err_cnt = success_cnt = 0
        self.open_app()
        while True:
            print(f'success_cnt={success_cnt}, err_cnt={err_cnt}')
            if err_cnt >= err_num:
                break
            if self.uia_ins.click(content_desc='我的，未选中状态', interval=0.01):
                self.uia_ins.xml = ''
            self.uia_ins.click(content_desc='我卖出的', interval=0.01, xml=self.uia_ins.xml)
            self.uia_ins.click(content_desc='待发货', interval=0.01)
            try:
                self.get_dispatch_address((939, 736))
            except (KeyError, TypeError) as err:
                print_err(err)
                err_cnt += 1
                self.open_app()
                continue
            if self.uia_ins.click('com.taobao.idlefish:id/right_text', interval=0.01):
                success_cnt += 1
                err_cnt = 0
                self.uia_ins.click(text='继续')
            else:
                err_cnt += 1
            if not err_cnt:
                try:
                    self.get_dispatch_address((939, 1270))
                except (TypeError, KeyError) as err:
                    print_err(err)
                    err_cnt += 1
                    self.open_app()
                    continue
                if self.uia_ins.click('com.taobao.idlefish:id/right_text', interval=0.01):
                    success_cnt += 1
                    err_cnt = 0
                    self.uia_ins.click(text='继续')
                else:
                    err_cnt += 1
            if not err_cnt:
                try:
                    self.get_dispatch_address((939, 1808))
                except TypeError as err:
                    print_err(err)
                    err_cnt += 1
                    self.open_app()
                    continue
                if self.uia_ins.click('com.taobao.idlefish:id/right_text', interval=0.01):
                    success_cnt += 1
                    err_cnt = 0
                    self.uia_ins.click(text='继续')
                else:
                    err_cnt += 1
            self.adb_ins.press_back_key(0.01)
        self.adb_ins.press_power_key()

    def rate(self):
        """评价"""
        self.open_app()
        success_cnt = 0
        while True:
            self.uia_ins.click(content_desc='我的，未选中状态', interval=0.01)
            self.uia_ins.click(content_desc='我卖出的', interval=0.01)
            self.uia_ins.click(content_desc='待评价', interval=0.01)
            if self.uia_ins.get_dict(content_desc='没有待评价的宝贝'):
                break
            if self.uia_ins.click(content_desc='去评价', interval=0.01):
                success_cnt += 1
                print(f'success_cnt={success_cnt}')
            else:
                self.open_app()
                continue
            self.uia_ins.click(content_desc='赏好评', interval=0.01)
            self.uia_ins.click(text='聊聊本次交易感受，你的评价能帮助到其他人~', interval=0.01)
            self.uia_ins.click(content_desc='沟通体验', interval=0.01)
            self.uia_ins.click(content_desc='发布', xml=self.uia_ins.xml, interval=0.01)
            try:
                self.uia_ins.click(content_desc='确定', interval=0.01)
            except FileNotFoundError as err:
                print_err(err)
                self.open_app()
                continue
            self.adb_ins.press_back_key(0.01)
            self.adb_ins.press_back_key(0.01)
            self.adb_ins.press_back_key(0.01)

    def delete_error_rate_order(self, err_num=3):
        """删除无法评价的订单（超过30天）

        :param err_num: 结束时的连续错误阈值
        """
        err_cnt = 0
        self.open_app()
        self.uia_ins.click(content_desc='我的，未选中状态', interval=0.01)
        self.uia_ins.click(content_desc='我卖出的', interval=0.01)
        self.uia_ins.click(content_desc='待评价', interval=0.01)
        while True:
            print(f'err_cnt={err_cnt}')
            if err_cnt >= err_num:
                self.free_memory()
                self.adb_ins.press_power_key()
                break
            if not self.uia_ins.click(content_desc='更多', interval=0.01):
                err_cnt += 1
                self.adb_ins.press_back_key()
                self.adb_ins.press_back_key()
                self.uia_ins.click(content_desc='我的，未选中状态', interval=0.01)
                self.uia_ins.click(content_desc='我卖出的', interval=0.01)
                self.uia_ins.click(content_desc='待评价', interval=0.01)
                continue
            err_cnt = 0
            self.uia_ins.click(content_desc='删除订单', interval=0.01)
            self.uia_ins.click(ResourceID.right_btn, interval=0.01)
