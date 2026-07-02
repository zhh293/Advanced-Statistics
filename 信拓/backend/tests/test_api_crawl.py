"""集成测试 - 爬虫 & 数据导入 API"""
import os
import csv
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from models import CrawlLog


class TestImportAPI:
    """数据导入 API 测试"""

    def test_导入成功(self, client):
        """正常导入 CSV"""
        with patch('routers.crawl.import_from_csv') as mock_import:
            mock_import.return_value = {'total': 1, 'imported': 1, 'skipped': 0}
            resp = client.post("/api/data/import")
            assert resp.status_code == 200
            data = resp.json()
            assert data['message'] == '导入完成'
            assert '新增 1' in data['detail']

    def test_导入异常(self, client):
        """导入失败时返回错误信息"""
        with patch('routers.crawl.import_from_csv', side_effect=Exception("文件不存在")):
            resp = client.post("/api/data/import")
            assert resp.status_code == 200
            data = resp.json()
            assert data['message'] == '导入失败'
            assert '文件不存在' in data['detail']


class TestCrawlTriggerAPI:
    """爬虫触发 API 测试"""

    def test_触发爬虫(self, client):
        """触发爬虫应返回成功消息（mock BackgroundTasks 避免实际执行）"""
        with patch('routers.crawl.SessionLocal'), \
             patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr='')
            resp = client.post("/api/crawl/trigger")
        assert resp.status_code == 200
        data = resp.json()
        assert '已触发' in data['message']


class TestCrawlLogsAPI:
    """爬虫日志 API 测试"""

    def test_空日志(self, client):
        resp = client.get("/api/crawl/logs")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_有日志(self, client, db_session):
        """添加日志后查询"""
        from datetime import datetime
        log = CrawlLog(
            source="all",
            status="SUCCESS",
            total_count=100,
            new_count=10,
            start_time=datetime(2024, 3, 15, 2, 0),
            end_time=datetime(2024, 3, 15, 2, 30),
        )
        db_session.add(log)
        db_session.flush()

        resp = client.get("/api/crawl/logs")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]['source'] == 'all'
        assert data[0]['status'] == 'SUCCESS'
        assert data[0]['total_count'] == 100
        assert data[0]['new_count'] == 10

    def test_限制数量(self, client, db_session):
        from datetime import datetime
        for i in range(10):
            db_session.add(CrawlLog(
                source="all", status="SUCCESS",
                start_time=datetime(2024, 3, i + 1),
            ))
        db_session.flush()

        resp = client.get("/api/crawl/logs?limit=3")
        assert resp.status_code == 200
        assert len(resp.json()) == 3


class TestCrawlStatusAPI:
    """爬虫状态 API 测试"""

    def test_无记录(self, client):
        resp = client.get("/api/crawl/status")
        assert resp.status_code == 200
        data = resp.json()
        assert 'message' in data

    def test_有记录(self, client, db_session):
        from datetime import datetime
        db_session.add(CrawlLog(
            source="all", status="SUCCESS",
            total_count=50, new_count=5,
            start_time=datetime(2024, 3, 15),
        ))
        db_session.flush()

        resp = client.get("/api/crawl/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'SUCCESS'
        assert data['total_count'] == 50
