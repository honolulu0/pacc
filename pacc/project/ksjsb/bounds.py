"""快手极速版工程包的边界值（位于目标矩形的斜对角的两点坐标）模块"""


# pylint: disable=too-few-public-methods
class Bounds:
    """快手极速版边界值类"""
    attendance = '[195,1299][885,1440]'  # 财富页面签到
    cashCoupons = '[-1,351][-1,459]'  # 可用抵用金（张）
    goldCoins = '[-1,351][-1,459]'  # 金币收益
    closeInviteFriendsToMakeMoney = '[483,1563][597,1674]'  # 关闭邀请好友赚更多
    closeCongratulations = '[78,405][174,501]'  # 关闭恭喜获得好友看视频奖励
