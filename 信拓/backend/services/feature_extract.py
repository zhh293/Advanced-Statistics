"""特征提取服务 —— 从标题+正文中提取事故原因、车辆类型、时段等"""
import re
from datetime import datetime


def extract_reason(text: str) -> str:
    """提取事故原因"""
    text = str(text).lower()
    if re.search(r'闯红灯|红灯|无视红灯|抢行', text):
        return '闯红灯'
    if re.search(r'抢黄灯|黄灯', text):
        return '抢黄灯'
    if re.search(r'信号灯故障|信号灯[故坏]', text):
        return '信号灯故障'
    if re.search(r'酒驾|醉驾|饮酒|酒精', text):
        return '酒驾'
    if re.search(r'超速|飙车', text):
        return '超速'
    if re.search(r'疲劳|犯困|打盹', text):
        return '疲劳驾驶'
    if re.search(r'分心|玩手机|看手机|操作导航|打电话', text):
        return '分心驾驶'
    if re.search(r'逆行|逆向', text):
        return '逆向行驶'
    return '其他'


def extract_vehicle(text: str) -> str:
    """提取涉事车辆类型"""
    text = str(text).lower()
    if re.search(r'电动车|电动自行车|非机动车', text):
        return '电动车'
    if re.search(r'摩托|三轮', text):
        return '摩托车/三轮车'
    if re.search(r'货车|卡车|厢式|半挂|牵引', text):
        return '货车'
    if re.search(r'小车|轿车|suv|私家车|面包车', text):
        return '小轿车'
    if re.search(r'行人', text):
        return '行人'
    return '其他'


def extract_time_period(dt: datetime) -> str:
    """根据时间提取时段"""
    if dt is None:
        return '未知'
    h = dt.hour
    if 7 <= h < 9:
        return '早高峰'
    if 17 <= h < 19:
        return '晚高峰'
    if 22 <= h or h < 5:
        return '夜间'
    return '平峰'


def extract_features(title: str, content: str, pub_time: datetime) -> dict:
    """一次提取所有特征"""
    text = (title or '') + ' ' + (content or '')
    return {
        'accident_reason': extract_reason(text),
        'vehicle_type': extract_vehicle(text),
        'time_period': extract_time_period(pub_time),
        'day_of_week': pub_time.weekday() if pub_time else None,
        'hour_of_day': pub_time.hour if pub_time else None,
    }
