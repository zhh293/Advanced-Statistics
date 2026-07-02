"""测试共享 fixtures"""
import sys
import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

# 确保 backend 目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Base, get_db
from models import Accident, AccidentFeature, AssociationRule, CrawlLog


@pytest.fixture(scope="function")
def test_engine():
    """每个测试使用独立的内存数据库"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """提供测试用的数据库会话，与 API 共享同一连接"""
    # 创建一个共享连接，确保内存数据库数据可跨 session 访问
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def app(test_engine, db_session):
    """创建测试用 FastAPI 应用（跳过 lifespan 避免启动调度器）"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from routers import accidents, analysis, mining, crawl

    # 创建独立的测试 app，不使用 lifespan（避免启动 scheduler）
    test_app = FastAPI(title="test")
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    test_app.include_router(accidents.router)
    test_app.include_router(analysis.router)
    test_app.include_router(mining.router)
    test_app.include_router(crawl.router)

    # 让 API 端点使用同一个 db_session
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # 不关闭，由 fixture 管理

    test_app.dependency_overrides[get_db] = override_get_db
    yield test_app


@pytest.fixture(scope="function")
def client(app):
    """提供测试用的 HTTP 客户端"""
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def sample_accidents(db_session):
    """创建测试用的事故数据"""
    from datetime import datetime

    accidents = []
    data = [
        {
            "url": "http://test.com/1",
            "title": "男子酒后驾车撞上护栏",
            "pub_time": datetime(2024, 3, 15, 8, 30),
            "location": "南京市鼓楼区",
            "lng": 118.8, "lat": 32.1,
            "content": "3月15日早上8点，一名男子酒驾撞上护栏，经酒精检测血液酒精含量超标。",
            "source": "南京交警",
        },
        {
            "url": "http://test.com/2",
            "title": "电动车闯红灯被撞",
            "pub_time": datetime(2024, 3, 16, 17, 45),
            "location": "温州市瑞安区",
            "lng": 120.6, "lat": 27.8,
            "content": "一辆电动车无视红灯信号闯红灯，与一辆轿车碰撞。",
            "source": "温州交警",
        },
        {
            "url": "http://test.com/3",
            "title": "货车超速追尾事故",
            "pub_time": datetime(2024, 3, 17, 2, 15),
            "location": "铜仁市碧江区",
            "lng": 109.2, "lat": 27.7,
            "content": "凌晨2时，一辆货车因超速行驶追尾前方轿车，造成追尾事故。",
            "source": "铜仁交警",
        },
        {
            "url": "http://test.com/4",
            "title": "行人横穿马路被摩托车撞伤",
            "pub_time": datetime(2024, 3, 18, 12, 0),
            "location": "福州市鼓楼区",
            "lng": 119.3, "lat": 26.1,
            "content": "一行人横穿马路时被摩托车撞伤，行人受轻伤，摩托车驾驶员分心玩手机。",
            "source": "福建交警",
        },
        {
            "url": "http://test.com/5",
            "title": "疲劳驾驶轿车冲出路面",
            "pub_time": datetime(2024, 3, 19, 23, 30),
            "location": "南京市江宁区",
            "lng": 118.8, "lat": 32.1,
            "content": "深夜一辆小轿车因驾驶员疲劳犯困冲出路面翻入沟渠。",
            "source": "南京交警",
        },
    ]

    for item in data:
        acc = Accident(**item)
        db_session.add(acc)
        db_session.flush()

        # 提取特征
        from services.feature_extract import extract_features
        features = extract_features(item["title"], item["content"], item["pub_time"])
        feat = AccidentFeature(
            accident_id=acc.id,
            accident_reason=features['accident_reason'],
            vehicle_type=features['vehicle_type'],
            time_period=features['time_period'],
            day_of_week=features['day_of_week'],
            hour_of_day=features['hour_of_day'],
        )
        db_session.add(feat)
        accidents.append(acc)

    db_session.flush()
    return accidents
