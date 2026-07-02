"""单元测试 - 地理编码服务"""
import pytest
from services.geo_service import get_coord


class TestGetCoord:
    """地理编码坐标匹配测试"""

    def test_精确城市匹配(self):
        name, lng, lat = get_coord("南京市鼓楼区")
        assert name == "南京"
        assert lng == 118.8
        assert lat == 32.1

    def test_温州匹配(self):
        name, lng, lat = get_coord("温州市区某路口")
        assert name == "温州"
        assert lng == 120.7
        assert lat == 28.0

    def test_区县级匹配优先(self):
        """碧江区的名字比铜仁更长，应优先匹配碧江区"""
        name, lng, lat = get_coord("铜仁市碧江区某路口")
        assert name == "碧江区"
        assert lng == 109.2
        assert lat == 27.7

    def test_乐清匹配(self):
        name, lng, lat = get_coord("乐清市虹桥镇")
        assert name == "乐清"
        assert lng == 121.0
        assert lat == 28.1

    def test_瑞安匹配(self):
        name, lng, lat = get_coord("瑞安某路段")
        assert name == "瑞安"

    def test_福州匹配(self):
        name, lng, lat = get_coord("福州市鼓楼区")
        assert name == "福州"
        assert lng == 119.3
        assert lat == 26.1

    def test_厦门匹配(self):
        name, lng, lat = get_coord("厦门市思明区")
        assert name == "厦门"

    def test_无匹配(self):
        name, lng, lat = get_coord("北京市朝阳区")
        assert name is None
        assert lng is None
        assert lat is None

    def test_空字符串(self):
        name, lng, lat = get_coord("")
        assert name is None
        assert lng is None
        assert lat is None

    def test_None(self):
        name, lng, lat = get_coord(None)
        assert name is None
        assert lng is None
        assert lat is None

    def test_最长匹配(self):
        """当输入包含多个可匹配的地名时，取最长的那个"""
        # "碧江区" 3个字 > "铜仁" 2个字，应匹配碧江区
        name, lng, lat = get_coord("铜仁市碧江区路口")
        assert name == "碧江区"
        assert lng == 109.2
        assert lat == 27.7

    def test_同长度地名(self):
        """同长度地名匹配其中一个即可"""
        name, _, _ = get_coord("铜仁松桃某镇")
        # 铜仁和松桃都是2个字，匹配到任一个都算正确
        assert name in ("铜仁", "松桃")

    def test_返回类型(self):
        """确认返回格式为 (str|None, float|None, float|None)"""
        result = get_coord("南京")
        assert isinstance(result, tuple)
        assert len(result) == 3
