"""单元测试 - CSV 导入服务"""
import os
import pytest
import tempfile
import csv
from datetime import datetime
from services.import_service import import_from_csv
from models import Accident, AccidentFeature


class TestImportFromCsv:
    """CSV 数据导入测试"""

    def _create_csv(self, rows):
        """创建临时 CSV 文件"""
        fd, path = tempfile.mkstemp(suffix='.csv')
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'title', 'pub_time', 'location', 'content', 'source'])
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return path

    def test_基本导入(self, db_session):
        """测试基本的 CSV 导入"""
        csv_path = self._create_csv([
            {
                'url': 'http://test.com/1',
                'title': '酒驾事故',
                'pub_time': '2024-03-15 08:30:00',
                'location': '南京',
                'content': '男子酒驾撞上护栏',
                'source': '南京交警',
            },
        ])
        try:
            result = import_from_csv(db_session, csv_path)
            assert result['total'] == 1
            assert result['imported'] == 1
            assert result['skipped'] == 0

            # 验证数据库记录
            acc = db_session.query(Accident).first()
            assert acc.title == '酒驾事故'
            assert acc.location == '南京'
            assert acc.lng == 118.8  # 南京坐标

            # 验证特征
            feat = db_session.query(AccidentFeature).first()
            assert feat.accident_reason == '酒驾'
            assert feat.time_period == '早高峰'
        finally:
            os.unlink(csv_path)

    def test_去重导入(self, db_session):
        """重复导入相同数据应跳过"""
        csv_path = self._create_csv([
            {
                'url': 'http://test.com/1',
                'title': '事故1',
                'pub_time': '2024-03-15',
                'location': '南京',
                'content': '事故内容',
                'source': '测试',
            },
        ])
        try:
            # 第一次导入
            result1 = import_from_csv(db_session, csv_path)
            assert result1['imported'] == 1

            # 第二次导入 - 应全部跳过
            result2 = import_from_csv(db_session, csv_path)
            assert result2['imported'] == 0
            assert result2['skipped'] == 1
        finally:
            os.unlink(csv_path)

    def test_空内容行被跳过(self, db_session):
        """content 为空的行应被跳过"""
        csv_path = self._create_csv([
            {
                'url': 'http://test.com/1',
                'title': '事故1',
                'pub_time': '2024-03-15',
                'location': '南京',
                'content': '',
                'source': '测试',
            },
            {
                'url': 'http://test.com/2',
                'title': '事故2',
                'pub_time': '2024-03-15',
                'location': '温州',
                'content': '有内容的记录',
                'source': '测试',
            },
        ])
        try:
            result = import_from_csv(db_session, csv_path)
            # pandas dropna 会丢掉空 content 行
            assert result['total'] == 1
            assert result['imported'] == 1
        finally:
            os.unlink(csv_path)

    def test_多条导入(self, db_session):
        """多条记录导入"""
        csv_path = self._create_csv([
            {
                'url': f'http://test.com/{i}',
                'title': f'事故{i}',
                'pub_time': f'2024-03-{15+i}',
                'location': '南京',
                'content': f'这是第{i}条事故记录',
                'source': '测试',
            }
            for i in range(5)
        ])
        try:
            result = import_from_csv(db_session, csv_path)
            assert result['total'] == 5
            assert result['imported'] == 5

            count = db_session.query(Accident).count()
            assert count == 5
        finally:
            os.unlink(csv_path)

    def test_地理编码(self, db_session):
        """导入时应自动进行地理编码"""
        csv_path = self._create_csv([
            {
                'url': 'http://test.com/1',
                'title': '事故',
                'pub_time': '2024-03-15',
                'location': '温州市瑞安区',
                'content': '温州瑞安事故',
                'source': '测试',
            },
        ])
        try:
            import_from_csv(db_session, csv_path)
            acc = db_session.query(Accident).first()
            assert acc.lng is not None
            assert acc.lat is not None
        finally:
            os.unlink(csv_path)

    def test_特征自动提取(self, db_session):
        """导入时应自动提取事故特征"""
        csv_path = self._create_csv([
            {
                'url': 'http://test.com/feat',
                'title': '电动车闯红灯',
                'pub_time': '2024-03-15 17:30:00',
                'location': '南京',
                'content': '一辆电动车闯红灯被轿车撞上',
                'source': '测试',
            },
        ])
        try:
            import_from_csv(db_session, csv_path)
            feat = db_session.query(AccidentFeature).first()
            assert feat is not None
            assert feat.accident_reason == '闯红灯'
            assert feat.vehicle_type == '电动车'
            assert feat.time_period == '晚高峰'
        finally:
            os.unlink(csv_path)
