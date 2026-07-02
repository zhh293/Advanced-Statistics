"""集成测试 - 事故数据 API"""
import pytest


class TestAccidentListAPI:
    """事故列表 API 测试"""

    def test_空列表(self, client):
        """无数据时返回空列表"""
        resp = client.get("/api/accidents")
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 0
        assert data['items'] == []
        assert data['page'] == 1

    def test_有数据列表(self, client, sample_accidents):
        """有数据时正常返回"""
        resp = client.get("/api/accidents")
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 5
        assert len(data['items']) == 5

    def test_分页(self, client, sample_accidents):
        """分页查询"""
        resp = client.get("/api/accidents?page=1&size=2")
        data = resp.json()
        assert data['total'] == 5
        assert len(data['items']) == 2
        assert data['page'] == 1
        assert data['size'] == 2

    def test_分页第二页(self, client, sample_accidents):
        resp = client.get("/api/accidents?page=2&size=2")
        data = resp.json()
        assert len(data['items']) == 2

    def test_关键词搜索(self, client, sample_accidents):
        """按关键词搜索"""
        resp = client.get("/api/accidents?keyword=酒驾")
        data = resp.json()
        assert data['total'] >= 1
        # 每条结果应包含"酒驾"
        for item in data['items']:
            assert '酒驾' in (item['title'] or '') or '酒驾' in (item['content'] or '') or '酒' in (item['content'] or '')

    def test_按原因筛选(self, client, sample_accidents):
        """按事故原因筛选"""
        resp = client.get("/api/accidents?reason=酒驾")
        data = resp.json()
        assert data['total'] >= 1
        for item in data['items']:
            assert item['accident_reason'] == '酒驾'

    def test_按车辆类型筛选(self, client, sample_accidents):
        resp = client.get("/api/accidents?vehicle_type=电动车")
        data = resp.json()
        assert data['total'] >= 1
        for item in data['items']:
            assert item['vehicle_type'] == '电动车'

    def test_按时段筛选(self, client, sample_accidents):
        resp = client.get("/api/accidents?time_period=早高峰")
        data = resp.json()
        assert data['total'] >= 1
        for item in data['items']:
            assert item['time_period'] == '早高峰'

    def test_按来源筛选(self, client, sample_accidents):
        resp = client.get("/api/accidents?source=南京")
        data = resp.json()
        assert data['total'] >= 1
        for item in data['items']:
            assert '南京' in item['source']


class TestAccidentDetailAPI:
    """事故详情 API 测试"""

    def test_获取详情(self, client, sample_accidents):
        """正常获取事故详情"""
        resp = client.get("/api/accidents/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data['id'] == 1
        assert data['title'] is not None
        assert data['accident_reason'] is not None

    def test_不存在的事故(self, client):
        """查询不存在的事故应返回 404"""
        resp = client.get("/api/accidents/99999")
        assert resp.status_code == 404


class TestFilterOptionsAPI:
    """筛选选项 API 测试"""

    def test_获取选项(self, client, sample_accidents):
        """获取筛选下拉选项"""
        resp = client.get("/api/accidents/filters/options")
        assert resp.status_code == 200
        data = resp.json()
        assert 'reasons' in data
        assert 'vehicle_types' in data
        assert 'time_periods' in data
        assert 'sources' in data
        assert len(data['reasons']) > 0
        assert len(data['vehicle_types']) > 0

    def test_空数据时的选项(self, client):
        """无数据时返回空选项"""
        resp = client.get("/api/accidents/filters/options")
        assert resp.status_code == 200
        data = resp.json()
        assert data['reasons'] == []


class TestExportAPI:
    """数据导出 API 测试"""

    def test_导出csv(self, client, sample_accidents):
        """导出 CSV 文件"""
        resp = client.get("/api/accidents/export")
        assert resp.status_code == 200
        assert 'text/csv' in resp.headers.get('content-type', '')
        content = resp.text
        lines = content.strip().split('\n')
        assert len(lines) >= 2  # 表头 + 至少一行数据
        # 验证表头
        header = lines[0].replace('\ufeff', '')
        assert 'ID' in header
        assert '标题' in header

    def test_带筛选导出(self, client, sample_accidents):
        """带筛选条件导出"""
        resp = client.get("/api/accidents/export?reason=酒驾")
        assert resp.status_code == 200
        content = resp.text
        lines = content.strip().split('\n')
        # 应只包含酒驾相关记录
        assert len(lines) >= 2
