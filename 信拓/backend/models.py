"""ORM 数据模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base


class Accident(Base):
    """交通事故原始数据"""
    __tablename__ = "t_accident"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False, comment="来源URL")
    title = Column(String(500), comment="标题")
    pub_time = Column(DateTime, comment="发布时间")
    location = Column(String(200), comment="事故地点")
    lng = Column(Float, comment="经度")
    lat = Column(Float, comment="纬度")
    content = Column(Text, comment="正文内容")
    source = Column(String(200), comment="来源网站")
    crawl_time = Column(DateTime, default=datetime.now, comment="入库时间")

    __table_args__ = (
        Index("idx_pub_time", "pub_time"),
        Index("idx_location", "location"),
        Index("idx_source", "source"),
    )

    # 一对多关联特征
    features = relationship("AccidentFeature", back_populates="accident", cascade="all, delete-orphan")


class AccidentFeature(Base):
    """特征提取结果"""
    __tablename__ = "t_accident_feature"

    id = Column(Integer, primary_key=True, autoincrement=True)
    accident_id = Column(Integer, ForeignKey("t_accident.id", ondelete="CASCADE"), comment="关联事故ID")
    accident_reason = Column(String(50), comment="事故原因")
    vehicle_type = Column(String(50), comment="车辆类型")
    time_period = Column(String(20), comment="时段")
    day_of_week = Column(Integer, comment="星期几 0-6")
    hour_of_day = Column(Integer, comment="小时 0-23")
    create_time = Column(DateTime, default=datetime.now)

    accident = relationship("Accident", back_populates="features")


class AssociationRule(Base):
    """关联规则挖掘结果"""
    __tablename__ = "t_association_rule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    antecedents = Column(String(500), comment="前件")
    consequents = Column(String(500), comment="后件")
    support = Column(Float, comment="支持度")
    confidence = Column(Float, comment="置信度")
    lift = Column(Float, comment="提升度")
    calc_time = Column(DateTime, default=datetime.now, comment="计算时间")
    params = Column(String(100), comment="参数: min_support,min_confidence")

    __table_args__ = (
        Index("idx_lift", "lift"),
    )


class CrawlLog(Base):
    """爬虫任务日志"""
    __tablename__ = "t_crawl_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), comment="来源网站")
    status = Column(String(20), comment="SUCCESS / FAIL / RUNNING")
    total_count = Column(Integer, default=0, comment="爬取总数")
    new_count = Column(Integer, default=0, comment="新增数量")
    error_msg = Column(Text, comment="错误信息")
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime)
