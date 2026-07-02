"""CSV 数据导入服务"""
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from models import Accident, AccidentFeature
from services.feature_extract import extract_features
from services.geo_service import get_coord
from config import CSV_PATH


def import_from_csv(db: Session, csv_path: str = None) -> dict:
    """
    从 CSV 导入事故数据到数据库
    返回 {'total': N, 'imported': N, 'skipped': N}
    """
    path = csv_path or CSV_PATH
    df = pd.read_csv(path, encoding='utf-8-sig')

    # 清洗
    df = df.dropna(subset=['content'])
    df = df.drop_duplicates(subset=['url', 'content'], keep='first')

    total = len(df)
    imported = 0
    skipped = 0

    for _, row in df.iterrows():
        url = str(row.get('url', ''))
        content = str(row.get('content', ''))

        # 检查是否已存在
        existing = db.query(Accident).filter(
            Accident.url == url,
            Accident.content == content
        ).first()
        if existing:
            skipped += 1
            continue

        # 解析时间
        pub_time = None
        time_str = str(row.get('pub_time', ''))
        if time_str and time_str != 'nan':
            try:
                pub_time = pd.to_datetime(time_str).to_pydatetime()
            except Exception:
                pass

        location = str(row.get('location', '')) if str(row.get('location', '')) != 'nan' else ''

        # 地理编码
        city_name, lng, lat = get_coord(location)

        # 创建事故记录
        accident = Accident(
            url=url,
            title=str(row.get('title', '')) if str(row.get('title', '')) != 'nan' else '',
            pub_time=pub_time,
            location=location,
            lng=lng,
            lat=lat,
            content=content,
            source=str(row.get('source', '')) if str(row.get('source', '')) != 'nan' else '',
            crawl_time=datetime.now(),
        )
        db.add(accident)
        db.flush()  # 获取 accident.id

        # 提取特征
        features = extract_features(
            str(row.get('title', '')),
            content,
            pub_time
        )
        feat = AccidentFeature(
            accident_id=accident.id,
            accident_reason=features['accident_reason'],
            vehicle_type=features['vehicle_type'],
            time_period=features['time_period'],
            day_of_week=features['day_of_week'],
            hour_of_day=features['hour_of_day'],
        )
        db.add(feat)
        imported += 1

    db.commit()
    return {'total': total, 'imported': imported, 'skipped': skipped}
