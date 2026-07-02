"""Pydantic 请求/响应模型"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ========== 事故相关 ==========
class AccidentOut(BaseModel):
    id: int
    url: str
    title: Optional[str] = None
    pub_time: Optional[datetime] = None
    location: Optional[str] = None
    lng: Optional[float] = None
    lat: Optional[float] = None
    content: Optional[str] = None
    source: Optional[str] = None
    accident_reason: Optional[str] = None
    vehicle_type: Optional[str] = None
    time_period: Optional[str] = None
    day_of_week: Optional[int] = None
    hour_of_day: Optional[int] = None

    class Config:
        from_attributes = True


class AccidentPage(BaseModel):
    total: int
    page: int
    size: int
    items: List[AccidentOut]


class AccidentFilter(BaseModel):
    keyword: Optional[str] = None
    reason: Optional[str] = None
    vehicle_type: Optional[str] = None
    time_period: Optional[str] = None
    source: Optional[str] = None
    location: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


# ========== 统计分析 ==========
class SummaryOut(BaseModel):
    total_accidents: int
    total_locations: int
    total_sources: int
    latest_time: Optional[datetime] = None
    reason_distribution: List[dict]
    vehicle_distribution: List[dict]
    period_distribution: List[dict]
    top_locations: List[dict]


class ChartItem(BaseModel):
    name: str
    value: int


class HeatmapItem(BaseModel):
    name: str
    value: List[float]  # [lng, lat, count]


class HourItem(BaseModel):
    x: int
    y: int


class SankeyData(BaseModel):
    nodes: List[dict]
    links: List[dict]


class WordCloudItem(BaseModel):
    name: str
    value: int


# ========== 关联规则 ==========
class MiningParams(BaseModel):
    min_support: float = 0.05
    min_confidence: float = 0.6


class RuleOut(BaseModel):
    id: int
    antecedents: str
    consequents: str
    support: float
    confidence: float
    lift: float
    calc_time: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 爬虫 ==========
class CrawlTrigger(BaseModel):
    sources: Optional[List[str]] = None  # 指定来源，不传则全部


class CrawlLogOut(BaseModel):
    id: int
    source: str
    status: str
    total_count: int
    new_count: int
    error_msg: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 通用 ==========
class MessageOut(BaseModel):
    message: str
    detail: Optional[str] = None
