import pandas as pd
import re
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
#1.数据读取与清洗
print("正在读取数据...")
df = pd.read_csv('traffic_accidents_final.csv', encoding='utf-8-sig')
print(f"原始数据量: {len(df)}")
df.dropna(subset=['content'], inplace=True)
df.drop_duplicates(subset=['url', 'content'], keep='first', inplace=True)
print(f"清洗后数据量: {len(df)}")
def parse_pub_time(time_str):
    if pd.isna(time_str):
        return pd.NaT
    match = re.match(r'(\d{4}-\d{2}-\d{2})', str(time_str))
    if match:
        return pd.to_datetime(match.group(1))
    return pd.NaT
df['pub_date'] = df['pub_time'].apply(parse_pub_time)
df.dropna(subset=['pub_date'], inplace=True)
print(f"最终有效数据量: {len(df)}")
#2.特征工程
# 合并标题与正文，提高关键词匹配率
df['text_for_analysis'] = df['title'].fillna('') + ' ' + df['content'].fillna('')
# 2.1 提取事故原因
def extract_reason(text):
    text = str(text).lower()
    if re.search(r'闯红灯|红灯|无视红灯|抢行', text):
        return '闯红灯'
    elif re.search(r'抢黄灯|黄灯', text):
        return '抢黄灯'
    elif re.search(r'信号灯故障|信号灯?[故|坏]', text):
        return '信号灯故障'
    elif re.search(r'酒驾|醉驾|饮酒|酒精', text):
        return '酒驾'
    elif re.search(r'超速|飙车', text):
        return '超速'
    elif re.search(r'疲劳|犯困|打盹', text):
        return '疲劳驾驶'
    elif re.search(r'分心|玩手机|看手机|操作导航|打电话', text):
        return '分心驾驶'
    elif re.search(r'逆行|逆向', text):
        return '逆向行驶'
    else:
        return '其他'
df['accident_reason'] = df['text_for_analysis'].apply(extract_reason)
# 2.2 提取涉事车辆类型
def extract_vehicle(text):
    text = str(text).lower()
    if re.search(r'电动车|电动自行车|非机动车', text):
        return '电动车'
    elif re.search(r'摩托|三轮', text):
        return '摩托车/三轮车'
    elif re.search(r'货车|卡车|厢式|半挂|牵引', text):
        return '货车'
    elif re.search(r'小车|轿车|SUV|私家车|面包车', text):
        return '小轿车'
    elif re.search(r'行人', text):
        return '行人'
    else:
        return '其他'
df['vehicle_type'] = df['text_for_analysis'].apply(extract_vehicle)
# 2.3 提取事故时段
def extract_time_period(hour):
    if pd.isna(hour):
        return '未知'
    if 7 <= hour < 9:
        return '早高峰'
    elif 17 <= hour < 19:
        return '晚高峰'
    elif 22 <= hour or hour < 5:
        return '夜间'
    else:
        return '平峰'
df['hour'] = df['pub_date'].dt.hour
df['time_period'] = df['hour'].apply(extract_time_period)
# 2.4 提取星期几 (周一=0, 周日=6)
df['day_of_week'] = df['pub_date'].dt.dayofweek
print("\n特征提取完成，新增列：accident_reason, vehicle_type, time_period, day_of_week")
# 3.描述性统计分析
print("\n===== 描述性统计 =====")
print("\n事故原因分布:\n", df['accident_reason'].value_counts())
print("\n事故时段分布:\n", df['time_period'].value_counts())
print("\n涉事车辆类型分布:\n", df['vehicle_type'].value_counts())
print("\n高发地点Top5:\n", df['location'].value_counts().head(5))
df.to_csv('traffic_accidents_clean.csv', index=False, encoding='utf-8-sig')
print("\n清洗后数据已保存至 traffic_accidents_clean.csv")
# 4.关联规则挖掘
print("\n===== 关联规则挖掘 =====")
feature_cols = ['accident_reason', 'vehicle_type', 'time_period']
for col in feature_cols:
    df[col] = df[col].astype(str).apply(lambda x: f"{col.split('_')[0]}:{x}")
transactions = df[feature_cols].values.tolist()
transactions = [set(trans) for trans in transactions]
# One-hot编码
te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
# 挖掘频繁项集 (最小支持度5%)
frequent_itemsets = apriori(df_encoded, min_support=0.05, use_colnames=True)
print(f"找到 {len(frequent_itemsets)} 个频繁项集")
# 挖掘关联规则 (最小置信度60%)
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.6)
rules_sorted = rules.sort_values('lift', ascending=False)
print(f"找到 {len(rules_sorted)} 条强关联规则")
print("\n最值得关注的关联规则 (Top 5):")
print(rules_sorted[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head(5))
print("\n分析完成！")