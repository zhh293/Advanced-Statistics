"""爬虫调度 & 数据导入 API"""
import subprocess
import sys
import os
from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from models import CrawlLog
from services.import_service import import_from_csv
from schemas import CrawlTrigger, CrawlLogOut, MessageOut

router = APIRouter(prefix="/api", tags=["爬虫 & 导入"])


@router.post("/data/import", response_model=MessageOut)
def import_data(db: Session = Depends(get_db)):
    """从 CSV 导入数据到数据库"""
    try:
        result = import_from_csv(db)
        return MessageOut(
            message="导入完成",
            detail=f"共 {result['total']} 条，新增 {result['imported']} 条，跳过 {result['skipped']} 条"
        )
    except Exception as e:
        return MessageOut(message="导入失败", detail=str(e))


@router.post("/crawl/trigger", response_model=MessageOut)
def trigger_crawl(
    trigger: CrawlTrigger = None,
    background_tasks: BackgroundTasks = None,
):
    """触发爬虫任务（后台执行）- 使用独立的数据库会话避免线程安全问题"""

    def run_spider():
        # 创建独立的数据库会话，避免跨线程使用
        db = SessionLocal()
        try:
            log = CrawlLog(
                source=",".join(trigger.sources) if trigger and trigger.sources else "all",
                status="RUNNING",
                start_time=datetime.now(),
            )
            db.add(log)
            db.commit()

            try:
                spider_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'spider.py')
                result = subprocess.run(
                    [sys.executable, spider_path],
                    capture_output=True, text=True, timeout=600,
                    cwd=os.path.dirname(spider_path)
                )
                if result.returncode == 0:
                    log.status = "SUCCESS"
                    # 爬虫完成后自动导入
                    import_result = import_from_csv(db)
                    log.total_count = import_result['total']
                    log.new_count = import_result['imported']
                else:
                    log.status = "FAIL"
                    log.error_msg = result.stderr[:1000] if result.stderr else "爬虫执行失败"
            except subprocess.TimeoutExpired:
                log.status = "FAIL"
                log.error_msg = "爬虫执行超时（600秒）"
            except Exception as e:
                log.status = "FAIL"
                log.error_msg = str(e)[:1000]

            log.end_time = datetime.now()
            db.commit()
        finally:
            db.close()

    if trigger is None:
        trigger = CrawlTrigger()

    background_tasks.add_task(run_spider)
    return MessageOut(message="爬虫任务已触发，正在后台执行")


@router.get("/crawl/logs")
def get_crawl_logs(limit: int = 20, db: Session = Depends(get_db)):
    """获取爬虫日志"""
    logs = db.query(CrawlLog).order_by(CrawlLog.start_time.desc()).limit(limit).all()
    return [CrawlLogOut.model_validate(log) for log in logs]


@router.get("/crawl/status")
def get_crawl_status(db: Session = Depends(get_db)):
    """获取最近一次爬虫状态"""
    latest = db.query(CrawlLog).order_by(CrawlLog.start_time.desc()).first()
    if latest:
        return CrawlLogOut.model_validate(latest)
    return {"message": "暂无爬虫记录"}
