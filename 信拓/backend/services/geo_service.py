"""地理编码服务 —— 将地名转为经纬度"""
from typing import Optional, Tuple
from config import COORDS


def get_coord(location: str) -> Tuple[Optional[str], Optional[float], Optional[float]]:
    """
    根据地点名匹配坐标
    返回 (匹配到的地名, 经度, 纬度)
    """
    if not location:
        return None, None, None

    s = str(location)
    best, best_len = None, 0
    for name in COORDS:
        if name in s and len(name) > best_len:
            best, best_len = name, len(name)

    if best:
        coord = COORDS[best]
        return best, coord[0], coord[1]
    return None, None, None
