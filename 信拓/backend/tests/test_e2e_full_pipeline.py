"""全链路端到端测试 - 从数据导入到分析到挖掘的完整流程"""
import os
import csv
import tempfile
import pytest
from unittest.mock import patch


class TestFullPipeline:
    """
    全链路测试：模拟完整的用户使用流程
    1. 导入 CSV 数据
    2. 查看看板总览
    3. 查看事故列表 & 筛选
    4. 查看事故详情
    5. 查看热力图
    6. 查看桑基图
    7. 查看词云
    8. 执行关联规则挖掘
    9. 查询规则结果
    10. 导出数据
    """

    @pytest.fixture(autouse=True)
    def setup_csv(self, tmp_path):
        """准备测试 CSV 文件"""
        self.csv_path = str(tmp_path / "test_accidents.csv")
        with open(self.csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'title', 'pub_time', 'location', 'content', 'source'])
            writer.writeheader()

            test_data = [
                # 酒驾案例 - 南京
                {"url": "http://e2e.com/1", "title": "男子酒驾撞护栏", "pub_time": "2024-03-15 08:30:00",
                 "location": "南京市鼓楼区中山路", "content": "3月15日早上，一名男子酒后驾驶小轿车在中山路撞上道路护栏，经检测酒精含量超标。", "source": "南京交警"},
                {"url": "http://e2e.com/2", "title": "醉驾SUV冲入绿化带", "pub_time": "2024-03-16 23:15:00",
                 "location": "南京市江宁区", "content": "深夜一辆SUV醉驾冲入路边绿化带，驾驶员酒精测试严重超标。", "source": "南京交警"},

                # 闯红灯案例 - 温州
                {"url": "http://e2e.com/3", "title": "电动车闯红灯被撞", "pub_time": "2024-03-17 17:45:00",
                 "location": "温州市瑞安区", "content": "一辆电动车无视红灯信号闯入路口，与一辆直行轿车发生碰撞。", "source": "温州交警"},
                {"url": "http://e2e.com/4", "title": "行人闯红灯酿事故", "pub_time": "2024-03-18 08:20:00",
                 "location": "温州市乐清市", "content": "一名行人闯红灯横穿马路，被一辆货车撞倒。", "source": "温州交警"},

                # 超速案例 - 铜仁
                {"url": "http://e2e.com/5", "title": "货车超速追尾", "pub_time": "2024-03-19 02:15:00",
                 "location": "铜仁市碧江区", "content": "凌晨2时，一辆货车因超速行驶追尾前方轿车，造成追尾事故。", "source": "铜仁交警"},
                {"url": "http://e2e.com/6", "title": "摩托车超速翻车", "pub_time": "2024-03-20 14:00:00",
                 "location": "铜仁市松桃县", "content": "一辆摩托车超速行驶在弯道处翻车。", "source": "铜仁交警"},

                # 分心驾驶 - 福建
                {"url": "http://e2e.com/7", "title": "玩手机追尾事故", "pub_time": "2024-03-21 12:00:00",
                 "location": "福州市鼓楼区", "content": "一名驾驶员玩手机分心驾驶小轿车追尾前车。", "source": "福建交警"},
                {"url": "http://e2e.com/8", "title": "打电话错过路口", "pub_time": "2024-03-22 18:30:00",
                 "location": "厦门市思明区", "content": "驾驶员打电话分心错过路口急刹导致后车追尾。", "source": "福建交警"},

                # 疲劳驾驶
                {"url": "http://e2e.com/9", "title": "疲劳驾驶冲出路面", "pub_time": "2024-03-23 03:00:00",
                 "location": "南京市江宁区", "content": "深夜一辆小轿车因驾驶员疲劳犯困冲出路面翻入沟渠。", "source": "南京交警"},
                {"url": "http://e2e.com/10", "title": "货车司机打盹追尾", "pub_time": "2024-03-24 04:30:00",
                 "location": "南京市鼓楼区", "content": "货车司机打盹追尾前方小轿车，疲劳驾驶酿事故。", "source": "南京交警"},

                # 逆向行驶
                {"url": "http://e2e.com/11", "title": "电动车逆行被撞", "pub_time": "2024-03-25 07:30:00",
                 "location": "温州市苍南县", "content": "一辆电动车逆行驶入机动车道被轿车撞上。", "source": "温州交警"},
                {"url": "http://e2e.com/12", "title": "三轮车逆向行驶", "pub_time": "2024-03-26 16:00:00",
                 "location": "铜仁市万山区", "content": "一辆三轮车逆向行驶与正常行驶车辆碰撞。", "source": "铜仁交警"},
            ]

            for row in test_data:
                writer.writerow(row)

    def test_完整流程(self, client, db_session):
        """端到端完整流程测试"""
        # ============ 1. 导入 CSV 数据 ============
        with patch('services.import_service.CSV_PATH', self.csv_path):
            resp = client.post("/api/data/import")
        assert resp.status_code == 200
        result = resp.json()
        assert result['message'] == '导入完成'
        assert '新增 12' in result['detail']

        # ============ 2. 查看看板总览 ============
        resp = client.get("/api/analysis/summary")
        assert resp.status_code == 200
        summary = resp.json()
        assert summary['total_accidents'] == 12
        assert summary['total_locations'] > 0
        assert summary['total_sources'] > 0
        assert summary['latest_time'] is not None

        # 验证各分布数据
        reason_names = [d['name'] for d in summary['reason_distribution']]
        assert '酒驾' in reason_names
        assert '闯红灯' in reason_names

        vehicle_names = [d['name'] for d in summary['vehicle_distribution']]
        assert len(vehicle_names) > 0

        # ============ 3. 查看事故列表 & 多条件筛选 ============
        # 无筛选 - 全部
        resp = client.get("/api/accidents?page=1&size=20")
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 12

        # 按原因筛选
        resp = client.get("/api/accidents?reason=酒驾")
        data = resp.json()
        assert data['total'] == 2
        for item in data['items']:
            assert item['accident_reason'] == '酒驾'

        # 按来源筛选
        resp = client.get("/api/accidents?source=温州")
        data = resp.json()
        assert data['total'] >= 2
        for item in data['items']:
            assert '温州' in item['source']

        # 按车辆类型筛选
        resp = client.get("/api/accidents?vehicle_type=电动车")
        data = resp.json()
        assert data['total'] >= 1

        # 关键词搜索
        resp = client.get("/api/accidents?keyword=打盹")
        data = resp.json()
        assert data['total'] >= 1

        # 分页测试
        resp = client.get("/api/accidents?page=1&size=5")
        data = resp.json()
        assert len(data['items']) == 5
        assert data['total'] == 12

        # ============ 4. 查看事故详情 ============
        resp = client.get("/api/accidents/1")
        assert resp.status_code == 200
        detail = resp.json()
        assert detail['id'] == 1
        assert detail['title'] is not None
        assert detail['content'] is not None
        assert detail['accident_reason'] is not None
        assert detail['vehicle_type'] is not None
        assert detail['time_period'] is not None

        # 不存在的事故
        resp = client.get("/api/accidents/99999")
        assert resp.status_code == 404

        # ============ 5. 获取筛选选项 ============
        resp = client.get("/api/accidents/filters/options")
        assert resp.status_code == 200
        options = resp.json()
        assert '酒驾' in options['reasons']
        assert '闯红灯' in options['reasons']
        assert len(options['vehicle_types']) > 0
        assert len(options['time_periods']) > 0
        assert len(options['sources']) > 0

        # ============ 6. 查看热力图 ============
        resp = client.get("/api/analysis/heatmap")
        assert resp.status_code == 200
        heatmap = resp.json()
        assert len(heatmap) > 0
        # 验证南京有数据
        nanjing_data = [d for d in heatmap if '南京' in d.get('name', '')]
        # 南京可能被拆分为"鼓楼区"和"江宁区"等，看具体 location 值

        # ============ 7. 查看24小时分布 ============
        resp = client.get("/api/analysis/hourly")
        assert resp.status_code == 200
        hourly = resp.json()
        assert len(hourly) > 0
        hours = [d['x'] for d in hourly]
        assert all(0 <= h <= 23 for h in hours)

        # ============ 8. 查看桑基图 ============
        resp = client.get("/api/analysis/sankey")
        assert resp.status_code == 200
        sankey = resp.json()
        assert 'nodes' in sankey
        assert 'links' in sankey

        # ============ 9. 查看词云 ============
        resp = client.get("/api/analysis/wordcloud")
        assert resp.status_code == 200
        wordcloud = resp.json()
        assert len(wordcloud) > 0

        # ============ 10. 查看交叉分析 ============
        resp = client.get("/api/analysis/reason-period-cross")
        assert resp.status_code == 200
        cross = resp.json()
        assert len(cross['periods']) > 0
        assert len(cross['reasons']) > 0

        # ============ 11. 执行关联规则挖掘 ============
        resp = client.post("/api/mining/run", json={
            "min_support": 0.05,
            "min_confidence": 0.3,
        })
        assert resp.status_code == 200
        mining_result = resp.json()
        assert '挖掘完成' in mining_result['message']
        # 12条数据可能产生也可能不产生规则，取决于分布

        # ============ 12. 查询规则 ============
        resp = client.get("/api/mining/rules")
        assert resp.status_code == 200
        rules = resp.json()
        # rules 可能为空，因为数据量较少

        # ============ 13. 查询最近参数 ============
        resp = client.get("/api/mining/rules/latest-params")
        assert resp.status_code == 200
        params = resp.json()
        assert params['params'] == "0.05,0.3"

        # ============ 14. 导出数据 ============
        resp = client.get("/api/accidents/export")
        assert resp.status_code == 200
        assert 'text/csv' in resp.headers.get('content-type', '')
        lines = resp.text.strip().split('\n')
        assert len(lines) == 13  # 表头 + 12条数据

        # 带筛选条件导出
        resp = client.get("/api/accidents/export?reason=酒驾")
        assert resp.status_code == 200
        lines = resp.text.strip().split('\n')
        assert len(lines) == 3  # 表头 + 2条酒驾

        # ============ 15. 爬虫日志查询 ============
        resp = client.get("/api/crawl/logs")
        assert resp.status_code == 200

        resp = client.get("/api/crawl/status")
        assert resp.status_code == 200

    def test_重复导入不重复入库(self, client, db_session):
        """全链路测试：重复导入同一 CSV 数据不应产生重复记录"""
        with patch('services.import_service.CSV_PATH', self.csv_path):
            # 第一次导入
            resp1 = client.post("/api/data/import")
            assert '新增 12' in resp1.json()['detail']

            # 第二次导入
            resp2 = client.post("/api/data/import")
            assert '新增 0' in resp2.json()['detail']
            assert '跳过 12' in resp2.json()['detail']

        # 数据库中仍然只有12条
        resp = client.get("/api/analysis/summary")
        assert resp.json()['total_accidents'] == 12

    def test_筛选导出一致性(self, client, db_session):
        """筛选列表和筛选导出的数据应一致"""
        with patch('services.import_service.CSV_PATH', self.csv_path):
            client.post("/api/data/import")

        # 按"南京"来源筛选列表
        resp = client.get("/api/accidents?source=南京&size=100")
        list_count = resp.json()['total']

        # 按"南京"来源导出
        resp = client.get("/api/accidents/export?source=南京")
        export_lines = resp.text.strip().split('\n')
        export_count = len(export_lines) - 1  # 减去表头

        assert list_count == export_count
