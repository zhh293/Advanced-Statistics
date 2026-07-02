"""集成测试 - 关联规则挖掘 API"""
import pytest
from models import AccidentFeature


def _create_bulk_features(db_session, count=100):
    """创建大量测试用特征数据以满足 Apriori 挖掘需求"""
    import random
    random.seed(42)

    reasons = ['闯红灯', '酒驾', '超速', '其他']
    vehicles = ['电动车', '小轿车', '货车']
    periods = ['早高峰', '晚高峰', '平峰', '夜间']

    for i in range(count):
        if i < count // 3:
            feat = AccidentFeature(
                accident_id=i + 1,
                accident_reason='闯红灯',
                vehicle_type='电动车',
                time_period='早高峰',
                day_of_week=i % 7,
                hour_of_day=8,
            )
        else:
            feat = AccidentFeature(
                accident_id=i + 1,
                accident_reason=random.choice(reasons),
                vehicle_type=random.choice(vehicles),
                time_period=random.choice(periods),
                day_of_week=i % 7,
                hour_of_day=random.randint(0, 23),
            )
        db_session.add(feat)
    db_session.commit()


class TestMiningRunAPI:
    """执行挖掘 API 测试"""

    def test_数据不足(self, client):
        """数据不足时返回空"""
        resp = client.post("/api/mining/run", json={
            "min_support": 0.05,
            "min_confidence": 0.6
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data['count'] == 0
        assert data['rules'] == []

    def test_正常挖掘(self, client, db_session):
        """有足够数据时执行挖掘"""
        _create_bulk_features(db_session, count=100)

        resp = client.post("/api/mining/run", json={
            "min_support": 0.05,
            "min_confidence": 0.3
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data['count'] > 0
        assert len(data['rules']) > 0
        assert '挖掘完成' in data['message']

    def test_默认参数(self, client, db_session):
        """使用默认参数"""
        _create_bulk_features(db_session, count=100)

        resp = client.post("/api/mining/run", json={})
        assert resp.status_code == 200


class TestMiningRulesAPI:
    """查询规则 API 测试"""

    def test_空规则(self, client):
        resp = client.get("/api/mining/rules")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_查询已有规则(self, client, db_session):
        """先执行挖掘，再查询规则"""
        _create_bulk_features(db_session, count=100)

        # 先执行挖掘
        client.post("/api/mining/run", json={
            "min_support": 0.05,
            "min_confidence": 0.3
        })

        # 查询规则
        resp = client.get("/api/mining/rules")
        assert resp.status_code == 200
        rules = resp.json()
        assert len(rules) > 0
        for rule in rules:
            assert 'id' in rule
            assert 'antecedents' in rule
            assert 'consequents' in rule
            assert 'support' in rule
            assert 'confidence' in rule
            assert 'lift' in rule

    def test_关键词筛选(self, client, db_session):
        """按关键词筛选规则"""
        _create_bulk_features(db_session, count=100)
        client.post("/api/mining/run", json={
            "min_support": 0.05,
            "min_confidence": 0.3
        })

        resp = client.get("/api/mining/rules?keyword=闯红灯")
        assert resp.status_code == 200
        rules = resp.json()
        for rule in rules:
            assert '闯红灯' in rule['antecedents'] or '闯红灯' in rule['consequents']

    def test_限制数量(self, client, db_session):
        _create_bulk_features(db_session, count=100)
        client.post("/api/mining/run", json={
            "min_support": 0.05,
            "min_confidence": 0.3
        })

        resp = client.get("/api/mining/rules?limit=3")
        assert resp.status_code == 200
        assert len(resp.json()) <= 3

    def test_排序(self, client, db_session):
        """按不同字段排序"""
        _create_bulk_features(db_session, count=100)
        client.post("/api/mining/run", json={
            "min_support": 0.05,
            "min_confidence": 0.3
        })

        for sort_by in ['lift', 'confidence', 'support']:
            resp = client.get(f"/api/mining/rules?sort_by={sort_by}")
            assert resp.status_code == 200
            rules = resp.json()
            if len(rules) > 1:
                values = [r[sort_by] for r in rules]
                assert values == sorted(values, reverse=True)


class TestLatestParamsAPI:
    """最近参数 API 测试"""

    def test_无历史(self, client):
        resp = client.get("/api/mining/rules/latest-params")
        assert resp.status_code == 200
        data = resp.json()
        assert data['params'] is None

    def test_有历史(self, client, db_session):
        _create_bulk_features(db_session, count=100)
        client.post("/api/mining/run", json={
            "min_support": 0.05,
            "min_confidence": 0.3
        })

        resp = client.get("/api/mining/rules/latest-params")
        assert resp.status_code == 200
        data = resp.json()
        assert data['params'] == "0.05,0.3"
        assert data['calc_time'] is not None
