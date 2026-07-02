"""定时爬虫调度"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import sys
import os
from datetime import datetime
from database import SessionLocal
from models import CrawlLog
from services.import_service import import_from_csv

scheduler = BackgroundScheduler()


def crawl_job():
    """定时爬虫任务"""
    db = SessionLocal()
    log = CrawlLog(source="all", status="RUNNING", start_time=datetime.now())
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
    db.close()


def start_scheduler():
    """启动定时任务：每天凌晨2点执行爬虫"""
    scheduler.add_job(
        crawl_job,
        CronTrigger(hour=2, minute=0),
        id='daily_crawl',
        name='每日交通事故数据爬取',
        replace_existing=True,
    )
    scheduler.start()
    print("定时爬虫调度已启动（每日 02:00）")


def stop_scheduler():
    """优雅关闭调度器"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("定时爬虫调度已关闭")
