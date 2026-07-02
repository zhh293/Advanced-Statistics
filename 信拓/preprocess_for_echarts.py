import pandas as pd
import jieba
from collections import Counter
import json
import re
import os
import math
os.makedirs('./echarts_data', exist_ok=True)
#读取数据
df = pd.read_csv('traffic_accidents_final.csv', encoding='utf-8-sig')
df = df.dropna(subset=['content', 'pub_time', 'location']).copy()
df['pub_time'] = pd.to_datetime(df['pub_time'], errors='coerce')
df = df.dropna(subset=['pub_time'])
#地理坐标字典
COORDS = {
    '南京': [118.8, 32.1], '温州': [120.7, 28.0], '铜仁': [109.2, 27.7],
    '福建': [117.9, 26.5], '福州': [119.3, 26.1], '厦门': [118.1, 24.5],
    '泉州': [118.6, 24.9], '漳州': [117.7, 24.5], '龙岩': [117.0, 25.1],
    '三明': [117.6, 26.3], '莆田': [119.0, 25.4], '南平': [118.2, 26.6],
    '宁德': [119.5, 26.7],
    '碧江区': [109.2, 27.7], '万山区': [109.2, 27.5], '松桃': [109.2, 28.2],
    '玉屏': [109.0, 27.2], '江口': [108.9, 27.7], '印江': [108.4, 28.0],
    '石阡': [108.2, 27.5], '思南': [108.2, 27.9], '德江': [108.1, 28.3],
    '沿河': [108.5, 28.6],
    '苍南': [120.4, 27.5], '乐清': [121.0, 28.1], '永嘉': [120.7, 28.2],
    '瑞安': [120.6, 27.8], '龙港': [120.5, 27.6],
}
def is_number(x):
    """检查是否为有效数值（不是NaN/Inf）"""
    return not (math.isnan(x) or math.isinf(x))
# 1. 热力图数据
def get_coord(loc):
    """返回匹配到的城市名"""
    s = str(loc)
    best, best_len = None, 0
    for name in COORDS:
        if name in s and len(name) > best_len:
            best, best_len = name, len(name)
    return best
df['city_name'] = df['location'].apply(get_coord)
city_count = df.groupby('city_name').size().reset_index(name='count')
city_count = city_count[city_count['city_name'].notna()]
heatmap_data = []
for _, row in city_count.iterrows():
    name = row['city_name']
    cnt = row['count']
    coord = COORDS.get(name)
    if not coord:
        continue
    if not is_number(coord[0]) or not is_number(coord[1]) or not is_number(cnt):
        continue
    heatmap_data.append({
        "name": name,
        "value": [coord[0], coord[1], int(cnt)]
    })
with open('./echarts_data/heatmap_data.json', 'w', encoding='utf-8') as f:
    json.dump(heatmap_data, f, ensure_ascii=False)

# 2. 特征提取（桑基图用）
def extract_reason(text):
    text = str(text).lower()
    if re.search(r'闯红灯|红灯|无视红灯|抢行', text): return 'reason_闯红灯'
    if re.search(r'酒驾|醉驾|饮酒|酒精', text): return 'reason_酒驾'
    if re.search(r'超速|飙车', text): return 'reason_超速'
    if re.search(r'疲劳|犯困|打盹', text): return 'reason_疲劳驾驶'
    if re.search(r'分心|玩手机|看手机|操作导航|打电话', text): return 'reason_分心驾驶'
    if re.search(r'逆行|逆向', text): return 'reason_逆向行驶'
    return 'reason_其他'
def extract_vehicle(text):
    text = str(text).lower()
    if re.search(r'电动车|电动自行车|非机动车', text): return 'vehicle_电动车'
    if re.search(r'摩托|三轮', text): return 'vehicle_摩托车/三轮车'
    if re.search(r'货车|卡车|厢式|半挂|牵引', text): return 'vehicle_货车'
    if re.search(r'小车|轿车|SUV|私家车|面包车', text): return 'vehicle_小轿车'
    if re.search(r'行人', text): return 'vehicle_行人'
    return 'vehicle_其他'
def extract_period(dt):
    try:
        h = dt.hour
        if 7 <= h < 9: return 'period_早高峰'
        if 17 <= h < 19: return 'period_晚高峰'
        if 22 <= h or h < 5: return 'period_夜间'
        return 'period_平峰'
    except:
        return 'period_未知'
df['reason'] = (df['title'].fillna('') + ' ' + df['content'].fillna('')).apply(extract_reason)
df['vehicle'] = (df['title'].fillna('') + ' ' + df['content'].fillna('')).apply(extract_vehicle)
df['period'] = df['pub_time'].apply(extract_period)
# 3. 桑基图数据
sankey_df = df.groupby(['period', 'reason', 'vehicle']).size().reset_index(name='count')
sankey_df = sankey_df[sankey_df['count'] > 5]
nodes_set = set()
links = []
for _, row in sankey_df.iterrows():
    src, tar = row['period'], row['reason']
    val = int(row['count'])
    links.append({"source": src, "target": tar, "value": val})
    nodes_set.add(src); nodes_set.add(tar)
for _, row in sankey_df.iterrows():
    src, tar = row['reason'], row['vehicle']
    val = int(row['count'])
    links.append({"source": src, "target": tar, "value": val})
    nodes_set.add(src); nodes_set.add(tar)
nodes = [{"name": n} for n in nodes_set]
name2idx = {n["name"]: i for i, n in enumerate(nodes)}
for link in links:
    link["source"] = name2idx[link["source"]]
    link["target"] = name2idx[link["target"]]
with open('./echarts_data/sankey_data.json', 'w', encoding='utf-8') as f:
    json.dump({"nodes": nodes, "links": links}, f, ensure_ascii=False)
#4. 词云数据
texts = df['content'].apply(str)
words = list(jieba.cut(' '.join(texts)))
stop_words = {'的','了','在','是','和','民警','交警','驾驶','车辆','行驶','事故','进行','开展','一个','等','与','及','发生','该','被','因','已','涉嫌','依法'}
words = [w for w in words if len(w) > 1 and w not in stop_words]
wf = Counter(words).most_common(200)
with open('./echarts_data/wordcloud_data.json', 'w', encoding='utf-8') as f:
    json.dump([{"name": w, "value": c} for w, c in wf], f, ensure_ascii=False)
# 5. 其他统计图数据 
# 违法类型 TOP8
reason_cnt = df['reason'].value_counts().head(8).reset_index()
reason_cnt.columns = ['name', 'value']
with open('./echarts_data/reason_data.json', 'w', encoding='utf-8') as f:
    json.dump(reason_cnt.to_dict('records'), f, ensure_ascii=False)
# 24小时分布
df['hour'] = df['pub_time'].dt.hour
hour_cnt = df['hour'].value_counts().sort_index()
with open('./echarts_data/hour_data.json', 'w', encoding='utf-8') as f:
    json.dump([{"x": int(h), "y": int(c)} for h, c in hour_cnt.items()], f, ensure_ascii=False)
# 车辆类型
vehicle_cnt = df['vehicle'].value_counts().head(6).reset_index()
vehicle_cnt.columns = ['name', 'value']
with open('./echarts_data/vehicle_data.json', 'w', encoding='utf-8') as f:
    json.dump(vehicle_cnt.to_dict('records'), f, ensure_ascii=False)
# 时段 × 违法类型 交叉表（堆叠柱状图用）
period_order = ['period_夜间', 'period_平峰', 'period_早高峰', 'period_晚高峰', 'period_未知']
cross = df.groupby(['period', 'reason']).size().unstack(fill_value=0)
cross = cross.reindex(period_order, fill_value=0)
reason_hour = {
    "periods": list(cross.index),
    "reasons": list(cross.columns),
    "data": cross.values.tolist()
}
with open('./echarts_data/reason_hour_data.json', 'w', encoding='utf-8') as f:
    json.dump(reason_hour, f, ensure_ascii=False)
print("所有 JSON 生成完毕，无 NaN！")