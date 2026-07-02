"""集成测试 - 统计分析 API"""
import pytest


class TestSummaryAPI:
    """看板总览 API 测试"""

    def test_空数据总览(self, client):
        """无数据时返回零值"""
        resp = client.get("/api/analysis/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data['total_accidents'] == 0
        assert data['total_locations'] == 0
        assert data['total_sources'] == 0
        assert data['latest_time'] is None
        assert data['reason_distribution'] == []

    def test_有数据总览(self, client, sample_accidents):
        """有数据时返回统计信息"""
        resp = client.get("/api/analysis/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data['total_accidents'] == 5
        assert data['total_locations'] > 0
        assert data['total_sources'] > 0
        assert data['latest_time'] is not None

        # 事故原因分布
        assert len(data['reason_distribution']) > 0
        for item in data['reason_distribution']:
            assert 'name' in item
            assert 'value' in item
            assert item['value'] > 0

        # 车辆类型分布
        assert len(data['vehicle_distribution']) > 0

        # 时段分布
        assert len(data['period_distribution']) > 0

        # 高发地点
        assert len(data['top_locations']) > 0


class TestHeatmapAPI:
    """热力图 API 测试"""

    def test_空数据热力图(self, client):
        resp = client.get("/api/analysis/heatmap")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_有数据热力图(self, client, sample_accidents):
        resp = client.get("/api/analysis/heatmap")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        for item in data:
            assert 'name' in item
            assert 'value' in item
            assert len(item['value']) == 3  # [lng, lat, count]
            assert item['value'][2] > 0  # count > 0


class TestHourlyAPI:
    """24小时分布 API 测试"""

    def test_空数据(self, client):
        resp = client.get("/api/analysis/hourly")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_有数据(self, client, sample_accidents):
        resp = client.get("/api/analysis/hourly")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        for item in data:
            assert 'x' in item  # hour
            assert 'y' in item  # count
            assert 0 <= item['x'] <= 23


class TestSankeyAPI:
    """桑基图 API 测试"""

    def test_空数据(self, client):
        resp = client.get("/api/analysis/sankey")
        assert resp.status_code == 200
        data = resp.json()
        assert data == {"nodes": [], "links": []}

    def test_有数据(self, client, sample_accidents):
        resp = client.get("/api/analysis/sankey")
        assert resp.status_code == 200
        data = resp.json()
        assert 'nodes' in data
        assert 'links' in data
        # 数据量小于阈值5时可能无 links
        if data['links']:
            for link in data['links']:
                assert 'source' in link
                assert 'target' in link
                assert 'value' in link


class TestWordcloudAPI:
    """词云 API 测试"""

    def test_空数据(self, client):
        resp = client.get("/api/analysis/wordcloud")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_有数据(self, client, sample_accidents):
        resp = client.get("/api/analysis/wordcloud")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        for item in data:
            assert 'name' in item
            assert 'value' in item
            assert len(item['name']) > 1  # 单字词已被过滤


class TestReasonPeriodCrossAPI:
    """交叉分析 API 测试"""

    def test_空数据(self, client):
        resp = client.get("/api/analysis/reason-period-cross")
        assert resp.status_code == 200
        data = resp.json()
        assert data == {"periods": [], "reasons": [], "data": []}

    def test_有数据(self, client, sample_accidents):
        resp = client.get("/api/analysis/reason-period-cross")
        assert resp.status_code == 200
        data = resp.json()
        assert 'periods' in data
        assert 'reasons' in data
        assert 'data' in data
        assert len(data['periods']) > 0
        assert len(data['reasons']) > 0
        # data 的行数 == periods 的数量
        assert len(data['data']) == len(data['periods'])
        # data 的列数 == reasons 的数量
        if data['data']:
            assert len(data['data'][0]) == len(data['reasons'])
