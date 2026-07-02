"""事故数据 API"""
import io
import csv
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Accident, AccidentFeature
from schemas import AccidentOut, AccidentPage

router = APIRouter(prefix="/api/accidents", tags=["事故数据"])


@router.get("/filters/options")
def get_filter_options(db: Session = Depends(get_db)):
    """获取所有可用的筛选选项"""
    reasons = [r[0] for r in db.query(AccidentFeature.accident_reason).distinct().all()]
    vehicles = [r[0] for r in db.query(AccidentFeature.vehicle_type).distinct().all()]
    periods = [r[0] for r in db.query(AccidentFeature.time_period).distinct().all()]
    sources = [r[0] for r in db.query(Accident.source).distinct().all()]
    return {
        "reasons": [r for r in reasons if r],
        "vehicle_types": [v for v in vehicles if v],
        "time_periods": [p for p in periods if p],
        "sources": [s for s in sources if s],
    }


@router.get("/export")
def export_accidents(
    keyword: str = Query(None),
    reason: str = Query(None),
    vehicle_type: str = Query(None),
    time_period: str = Query(None),
    source: str = Query(None),
    location: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    format: str = Query("csv", description="导出格式: csv"),
    db: Session = Depends(get_db),
):
    """导出筛选结果为 CSV 文件"""
    q = db.query(Accident).outerjoin(AccidentFeature)

    if keyword:
        q = q.filter(
            (Accident.title.contains(keyword)) |
            (Accident.content.contains(keyword))
        )
    if reason:
        q = q.filter(AccidentFeature.accident_reason == reason)
    if vehicle_type:
        q = q.filter(AccidentFeature.vehicle_type == vehicle_type)
    if time_period:
        q = q.filter(AccidentFeature.time_period == time_period)
    if source:
        q = q.filter(Accident.source.contains(source))
    if location:
        q = q.filter(Accident.location.contains(location))
    if date_from:
        q = q.filter(func.date(Accident.pub_time) >= date_from)
    if date_to:
        q = q.filter(func.date(Accident.pub_time) <= date_to)

    accidents = q.group_by(Accident.id).order_by(Accident.pub_time.desc()).all()

    output = io.StringIO()
    output.write('\ufeff')  # BOM for Excel compatibility
    writer = csv.writer(output)
    writer.writerow(['ID', '标题', '事故原因', '车辆类型', '时段', '地点', '来源', '发布时间', 'URL'])

    for acc in accidents:
        feat = acc.features[0] if acc.features else None
        writer.writerow([
            acc.id,
            acc.title or '',
            feat.accident_reason if feat else '',
            feat.vehicle_type if feat else '',
            feat.time_period if feat else '',
            acc.location or '',
            acc.source or '',
            str(acc.pub_time or ''),
            acc.url or '',
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=accidents_export.csv"},
    )


@router.get("", response_model=AccidentPage)
def list_accidents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None, description="搜索关键词"),
    reason: str = Query(None, description="事故原因"),
    vehicle_type: str = Query(None, description="车辆类型"),
    time_period: str = Query(None, description="时段"),
    source: str = Query(None, description="来源"),
    location: str = Query(None, description="地点"),
    date_from: str = Query(None, description="开始日期 YYYY-MM-DD"),
    date_to: str = Query(None, description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """分页查询事故列表，支持多条件筛选"""
    q = db.query(Accident).outerjoin(AccidentFeature)

    # 条件筛选
    if keyword:
        q = q.filter(
            (Accident.title.contains(keyword)) |
            (Accident.content.contains(keyword))
        )
    if reason:
        q = q.filter(AccidentFeature.accident_reason == reason)
    if vehicle_type:
        q = q.filter(AccidentFeature.vehicle_type == vehicle_type)
    if time_period:
        q = q.filter(AccidentFeature.time_period == time_period)
    if source:
        q = q.filter(Accident.source.contains(source))
    if location:
        q = q.filter(Accident.location.contains(location))
    if date_from:
        q = q.filter(func.date(Accident.pub_time) >= date_from)
    if date_to:
        q = q.filter(func.date(Accident.pub_time) <= date_to)

    # 使用 group_by 避免 join 导致的重复行
    total = q.group_by(Accident.id).count()
    accidents = (
        q.group_by(Accident.id)
        .order_by(Accident.pub_time.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    items = []
    for acc in accidents:
        feat = acc.features[0] if acc.features else None
        items.append(AccidentOut(
            id=acc.id,
            url=acc.url,
            title=acc.title,
            pub_time=acc.pub_time,
            location=acc.location,
            lng=acc.lng,
            lat=acc.lat,
            content=acc.content,
            source=acc.source,
            accident_reason=feat.accident_reason if feat else None,
            vehicle_type=feat.vehicle_type if feat else None,
            time_period=feat.time_period if feat else None,
            day_of_week=feat.day_of_week if feat else None,
            hour_of_day=feat.hour_of_day if feat else None,
        ))

    return AccidentPage(total=total, page=page, size=size, items=items)


@router.get("/{accident_id}", response_model=AccidentOut)
def get_accident(accident_id: int, db: Session = Depends(get_db)):
    """获取事故详情"""
    acc = db.query(Accident).filter(Accident.id == accident_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="事故记录不存在")
    feat = acc.features[0] if acc.features else None
    return AccidentOut(
        id=acc.id,
        url=acc.url,
        title=acc.title,
        pub_time=acc.pub_time,
        location=acc.location,
        lng=acc.lng,
        lat=acc.lat,
        content=acc.content,
        source=acc.source,
        accident_reason=feat.accident_reason if feat else None,
        vehicle_type=feat.vehicle_type if feat else None,
        time_period=feat.time_period if feat else None,
        day_of_week=feat.day_of_week if feat else None,
        hour_of_day=feat.hour_of_day if feat else None,
    )
