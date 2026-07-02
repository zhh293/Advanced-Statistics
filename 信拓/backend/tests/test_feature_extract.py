"""单元测试 - 特征提取服务"""
import pytest
from datetime import datetime
from services.feature_extract import (
    extract_reason,
    extract_vehicle,
    extract_time_period,
    extract_features,
)


# ==================== extract_reason 测试 ====================

class TestExtractReason:
    """事故原因提取测试"""

    def test_闯红灯(self):
        assert extract_reason("电动车无视红灯闯入路口") == '闯红灯'
        assert extract_reason("行人闯红灯被撞") == '闯红灯'
        assert extract_reason("抢行通过路口") == '闯红灯'

    def test_抢黄灯(self):
        assert extract_reason("轿车抢黄灯通过") == '抢黄灯'
        assert extract_reason("黄灯期间强行通过") == '抢黄灯'

    def test_信号灯故障(self):
        assert extract_reason("信号灯故障导致事故") == '信号灯故障'
        assert extract_reason("信号灯坏了无人修理") == '信号灯故障'
        assert extract_reason("信号灯故了") == '信号灯故障'

    def test_酒驾(self):
        assert extract_reason("酒驾男子撞上护栏") == '酒驾'
        assert extract_reason("醉驾撞人逃逸") == '酒驾'
        assert extract_reason("经检测饮酒后驾车") == '酒驾'
        assert extract_reason("酒精含量超标") == '酒驾'

    def test_超速(self):
        assert extract_reason("货车超速追尾") == '超速'
        assert extract_reason("飙车族深夜飙车") == '超速'

    def test_疲劳驾驶(self):
        assert extract_reason("驾驶员疲劳驾驶") == '疲劳驾驶'
        assert extract_reason("司机犯困打盹") == '疲劳驾驶'

    def test_分心驾驶(self):
        assert extract_reason("分心操作手机导致事故") == '分心驾驶'
        assert extract_reason("玩手机没注意前方") == '分心驾驶'
        assert extract_reason("打电话分心") == '分心驾驶'

    def test_逆向行驶(self):
        assert extract_reason("逆行进入对向车道") == '逆向行驶'
        assert extract_reason("逆向行驶被撞") == '逆向行驶'

    def test_其他(self):
        assert extract_reason("发生一起交通事故") == '其他'
        assert extract_reason("") == '其他'
        assert extract_reason("天气原因导致事故") == '其他'

    def test_优先级_闯红灯优先于其他(self):
        """闯红灯排在最前面，应优先匹配"""
        assert extract_reason("酒后闯红灯") == '闯红灯'


# ==================== extract_vehicle 测试 ====================

class TestExtractVehicle:
    """车辆类型提取测试"""

    def test_电动车(self):
        assert extract_vehicle("电动车闯红灯") == '电动车'
        assert extract_vehicle("电动自行车追尾") == '电动车'
        assert extract_vehicle("非机动车违规") == '电动车'

    def test_摩托车(self):
        assert extract_vehicle("摩托车闯入") == '摩托车/三轮车'
        assert extract_vehicle("三轮车载人") == '摩托车/三轮车'

    def test_货车(self):
        assert extract_vehicle("一辆货车超速") == '货车'
        assert extract_vehicle("卡车追尾") == '货车'
        assert extract_vehicle("半挂车侧翻") == '货车'

    def test_小轿车(self):
        assert extract_vehicle("小车追尾") == '小轿车'
        assert extract_vehicle("一辆轿车撞上") == '小轿车'
        assert extract_vehicle("一辆suv翻入沟渠") == '小轿车'
        assert extract_vehicle("面包车载货") == '小轿车'

    def test_行人(self):
        assert extract_vehicle("行人横穿马路") == '行人'

    def test_其他(self):
        assert extract_vehicle("一起交通事故") == '其他'
        assert extract_vehicle("") == '其他'


# ==================== extract_time_period 测试 ====================

class TestExtractTimePeriod:
    """时段提取测试"""

    def test_早高峰(self):
        assert extract_time_period(datetime(2024, 1, 1, 7, 0)) == '早高峰'
        assert extract_time_period(datetime(2024, 1, 1, 8, 30)) == '早高峰'

    def test_晚高峰(self):
        assert extract_time_period(datetime(2024, 1, 1, 17, 0)) == '晚高峰'
        assert extract_time_period(datetime(2024, 1, 1, 18, 30)) == '晚高峰'

    def test_夜间(self):
        assert extract_time_period(datetime(2024, 1, 1, 22, 0)) == '夜间'
        assert extract_time_period(datetime(2024, 1, 1, 23, 30)) == '夜间'
        assert extract_time_period(datetime(2024, 1, 1, 2, 0)) == '夜间'
        assert extract_time_period(datetime(2024, 1, 1, 4, 59)) == '夜间'

    def test_平峰(self):
        assert extract_time_period(datetime(2024, 1, 1, 9, 0)) == '平峰'
        assert extract_time_period(datetime(2024, 1, 1, 12, 0)) == '平峰'
        assert extract_time_period(datetime(2024, 1, 1, 16, 59)) == '平峰'
        assert extract_time_period(datetime(2024, 1, 1, 5, 0)) == '平峰'

    def test_无时间(self):
        assert extract_time_period(None) == '未知'

    def test_边界值(self):
        """测试时段边界"""
        assert extract_time_period(datetime(2024, 1, 1, 6, 59)) == '平峰'
        assert extract_time_period(datetime(2024, 1, 1, 7, 0)) == '早高峰'
        assert extract_time_period(datetime(2024, 1, 1, 8, 59)) == '早高峰'
        assert extract_time_period(datetime(2024, 1, 1, 9, 0)) == '平峰'
        assert extract_time_period(datetime(2024, 1, 1, 16, 59)) == '平峰'
        assert extract_time_period(datetime(2024, 1, 1, 17, 0)) == '晚高峰'
        assert extract_time_period(datetime(2024, 1, 1, 18, 59)) == '晚高峰'
        assert extract_time_period(datetime(2024, 1, 1, 19, 0)) == '平峰'
        assert extract_time_period(datetime(2024, 1, 1, 21, 59)) == '平峰'
        assert extract_time_period(datetime(2024, 1, 1, 22, 0)) == '夜间'


# ==================== extract_features 综合测试 ====================

class TestExtractFeatures:
    """综合特征提取测试"""

    def test_完整提取(self):
        result = extract_features(
            "酒驾轿车撞上护栏",
            "一辆小轿车酒驾后撞上护栏",
            datetime(2024, 3, 15, 8, 30)
        )
        assert result['accident_reason'] == '酒驾'
        assert result['vehicle_type'] == '小轿车'
        assert result['time_period'] == '早高峰'
        assert result['day_of_week'] == 4  # Friday
        assert result['hour_of_day'] == 8

    def test_无时间(self):
        result = extract_features("事故标题", "事故内容", None)
        assert result['time_period'] == '未知'
        assert result['day_of_week'] is None
        assert result['hour_of_day'] is None

    def test_空内容(self):
        result = extract_features(None, None, None)
        assert result['accident_reason'] == '其他'
        assert result['vehicle_type'] == '其他'
        assert result['time_period'] == '未知'

    def test_标题和正文联合提取(self):
        """标题有车型信息，正文有原因信息"""
        result = extract_features(
            "货车追尾事故",
            "因超速导致追尾",
            datetime(2024, 1, 1, 12, 0)
        )
        assert result['vehicle_type'] == '货车'
        assert result['accident_reason'] == '超速'
