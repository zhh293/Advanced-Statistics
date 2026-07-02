"""单元测试 - 关联规则挖掘引擎"""
import pytest
from datetime import datetime
from services.mining_engine import run_apriori
from models import AccidentFeature, AssociationRule


class TestRunApriori:
    """Apriori 关联规则挖掘测试"""

    def _create_features(self, db_session, count=50):
        """创建测试用特征数据"""
        import random
        random.seed(42)

        reasons = ['闯红灯', '酒驾', '超速', '其他']
        vehicles = ['电动车', '小轿车', '货车', '摩托车/三轮车']
        periods = ['早高峰', '晚高峰', '平峰', '夜间']

        for i in range(count):
            # 制造一些强关联：早高峰 + 电动车 + 闯红灯
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

    def test_数据不足时返回空(self, db_session):
        """特征数据少于10条时不执行挖掘"""
        for i in range(5):
            db_session.add(AccidentFeature(
                accident_id=i + 1,
                accident_reason='闯红灯',
                vehicle_type='电动车',
                time_period='早高峰',
            ))
        db_session.commit()

        result = run_apriori(db_session, min_support=0.05, min_confidence=0.6)
        assert result == []

    def test_正常挖掘(self, db_session):
        """正常数据量可以挖掘出规则"""
        self._create_features(db_session, count=100)

        result = run_apriori(db_session, min_support=0.05, min_confidence=0.3)
        assert len(result) > 0

        # 检查规则格式
        for rule in result:
            assert 'antecedents' in rule
            assert 'consequents' in rule
            assert 'support' in rule
            assert 'confidence' in rule
            assert 'lift' in rule
            assert 0 <= rule['support'] <= 1
            assert 0 <= rule['confidence'] <= 1
            assert rule['lift'] > 0

    def test_规则保存到数据库(self, db_session):
        """挖掘结果应保存到数据库"""
        self._create_features(db_session, count=100)

        run_apriori(db_session, min_support=0.05, min_confidence=0.3)
        db_rules = db_session.query(AssociationRule).all()
        assert len(db_rules) > 0

        for r in db_rules:
            assert r.params == "0.05,0.3"
            assert r.calc_time is not None

    def test_不同参数不互相覆盖(self, db_session):
        """不同参数的挖掘结果不应互相覆盖"""
        self._create_features(db_session, count=100)

        run_apriori(db_session, min_support=0.05, min_confidence=0.3)
        count1 = db_session.query(AssociationRule).filter(
            AssociationRule.params == "0.05,0.3"
        ).count()

        run_apriori(db_session, min_support=0.1, min_confidence=0.5)
        count1_after = db_session.query(AssociationRule).filter(
            AssociationRule.params == "0.05,0.3"
        ).count()

        assert count1 == count1_after  # 第一次的结果不受影响

    def test_同参数重新挖掘会覆盖(self, db_session):
        """相同参数重新挖掘应覆盖旧结果"""
        self._create_features(db_session, count=100)

        run_apriori(db_session, min_support=0.05, min_confidence=0.3)
        first_count = db_session.query(AssociationRule).filter(
            AssociationRule.params == "0.05,0.3"
        ).count()

        run_apriori(db_session, min_support=0.05, min_confidence=0.3)
        second_count = db_session.query(AssociationRule).filter(
            AssociationRule.params == "0.05,0.3"
        ).count()

        assert first_count == second_count  # 数量应一致（先删后插）

    def test_结果按提升度排序(self, db_session):
        """挖掘结果应按 lift 降序排列"""
        self._create_features(db_session, count=100)

        result = run_apriori(db_session, min_support=0.05, min_confidence=0.3)
        if len(result) > 1:
            lifts = [r['lift'] for r in result]
            assert lifts == sorted(lifts, reverse=True)

    def test_高阈值无结果(self, db_session):
        """阈值过高时可能无结果"""
        self._create_features(db_session, count=20)

        result = run_apriori(db_session, min_support=0.9, min_confidence=0.99)
        assert isinstance(result, list)
