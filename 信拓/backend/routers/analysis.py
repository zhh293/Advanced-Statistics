"""统计分析 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter
import jieba

from database import get_db
from models import Accident, AccidentFeature
from schemas import SummaryOut, HeatmapItem, SankeyData

router = APIRouter(prefix="/api/analysis", tags=["统计分析"])


@router.get("/summary", response_model=SummaryOut)
def get_summary(db: Session = Depends(get_db)):
    """看板总览数据"""
    total = db.query(Accident).count()
    locations = db.query(Accident.location).filter(Accident.location != '').distinct().count()
    sources = db.query(Accident.source).filter(Accident.source != '').distinct().count()
    latest = db.query(func.max(Accident.pub_time)).scalar()

    # 事故原因分布
    reasons = db.query(
        AccidentFeature.accident_reason, func.count(AccidentFeature.id)
    ).group_by(AccidentFeature.accident_reason).all()
    reason_dist = [{"name": r[0], "value": r[1]} for r in reasons if r[0]]

    # 车辆类型分布
    vehicles = db.query(
        AccidentFeature.vehicle_type, func.count(AccidentFeature.id)
    ).group_by(AccidentFeature.vehicle_type).all()
    vehicle_dist = [{"name": v[0], "value": v[1]} for v in vehicles if v[0]]

    # 时段分布
    periods = db.query(
        AccidentFeature.time_period, func.count(AccidentFeature.id)
    ).group_by(AccidentFeature.time_period).all()
    period_dist = [{"name": p[0], "value": p[1]} for p in periods if p[0]]

    # 高发地点 TOP10
    top_locs = db.query(
        Accident.location, func.count(Accident.id)
    ).filter(Accident.location != '').group_by(Accident.location).order_by(
        func.count(Accident.id).desc()
    ).limit(10).all()
    top_locations = [{"name": loc[0], "value": loc[1]} for loc in top_locs]

    return SummaryOut(
        total_accidents=total,
        total_locations=locations,
        total_sources=sources,
        latest_time=latest,
        reason_distribution=reason_dist,
        vehicle_distribution=vehicle_dist,
        period_distribution=period_dist,
        top_locations=top_locations,
    )


@router.get("/heatmap")
def get_heatmap(db: Session = Depends(get_db)):
    """热力图数据 - 使用 AVG 聚合经纬度"""
    results = db.query(
        func.avg(Accident.lng).label('lng'),
        func.avg(Accident.lat).label('lat'),
        Accident.location,
        func.count(Accident.id).label('cnt'),
    ).filter(
        Accident.lng.isnot(None), Accident.lat.isnot(None)
    ).group_by(Accident.location).all()

    data = []
    for row in results:
        data.append(HeatmapItem(
            name=row.location or "未知",
            value=[round(row.lng, 2), round(row.lat, 2), row.cnt]
        ))
    return [d.model_dump() for d in data]


@router.get("/hourly")
def get_hourly(db: Session = Depends(get_db)):
    """24小时分布"""
    results = db.query(
        AccidentFeature.hour_of_day, func.count(AccidentFeature.id)
    ).filter(AccidentFeature.hour_of_day.isnot(None)).group_by(
        AccidentFeature.hour_of_day
    ).order_by(AccidentFeature.hour_of_day).all()

    return [{"x": r[0], "y": r[1]} for r in results]


@router.get("/sankey")
def get_sankey(db: Session = Depends(get_db)):
    """桑基图数据：时段→原因→车型"""
    features = db.query(AccidentFeature).all()
    if not features:
        return {"nodes": [], "links": []}

    # 统计 (period, reason, vehicle) 组合
    triples = Counter()
    for f in features:
        key = (f.time_period, f.accident_reason, f.vehicle_type)
        triples[key] += 1

    # 过滤低频组合
    triples = {k: v for k, v in triples.items() if v > 5}

    nodes_set = set()
    links = []

    for (period, reason, vehicle), count in triples.items():
        links.append({"source": f"period_{period}", "target": f"reason_{reason}", "value": count})
        links.append({"source": f"reason_{reason}", "target": f"vehicle_{vehicle}", "value": count})
        nodes_set.add(f"period_{period}")
        nodes_set.add(f"reason_{reason}")
        nodes_set.add(f"vehicle_{vehicle}")

    nodes = [{"name": n} for n in sorted(nodes_set)]
    name2idx = {n["name"]: i for i, n in enumerate(nodes)}

    for link in links:
        link["source"] = name2idx[link["source"]]
        link["target"] = name2idx[link["target"]]

    return {"nodes": nodes, "links": links}


@router.get("/wordcloud")
def get_wordcloud(db: Session = Depends(get_db)):
    """词云数据 - 分批处理避免内存溢出"""
    stop_words = {
        '的', '了', '在', '是', '和', '民警', '交警', '驾驶', '车辆', '行驶',
        '事故', '进行', '开展', '一个', '等', '与', '及', '发生', '该', '被',
        '因', '已', '涉嫌', '依法', '，', '。', '、', '；', '：', '！', '？',
        '"', '"', '（', '）', '\n', '\r', ' ', '…', '中', '对', '到',
        '为', '后', '时', '上', '不', '有', '从', '其', '经', '将', '由',
        '也', '向', '并', '所', '就', '把', '而', '又', '但', '或', '如',
    }

    word_counter = Counter()
    batch_size = 200
    offset = 0

    while True:
        contents = db.query(Accident.content).offset(offset).limit(batch_size).all()
        if not contents:
            break
        text = ' '.join([c[0] or '' for c in contents])
        words = jieba.cut(text)
        for w in words:
            if len(w) > 1 and w not in stop_words:
                word_counter[w] += 1
        offset += batch_size

    return [{"name": w, "value": c} for w, c in word_counter.most_common(200)]


@router.get("/reason-period-cross")
def get_reason_period_cross(db: Session = Depends(get_db)):
    """时段×原因交叉表（堆叠柱状图）"""
    import pandas as pd
    features = db.query(AccidentFeature).all()

    if not features:
        return {"periods": [], "reasons": [], "data": []}

    df = pd.DataFrame([{
        'period': f.time_period,
        'reason': f.accident_reason,
    } for f in features])

    if df.empty:
        return {"periods": [], "reasons": [], "data": []}

    period_order = ['夜间', '平峰', '早高峰', '晚高峰', '未知']
    cross = df.groupby(['period', 'reason']).size().unstack(fill_value=0)
    cross = cross.reindex([p for p in period_order if p in cross.index], fill_value=0)

    return {
        "periods": list(cross.index),
        "reasons": list(cross.columns),
        "data": cross.values.tolist()
    }
