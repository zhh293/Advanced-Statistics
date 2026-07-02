"""Apriori 关联规则挖掘引擎"""
import pandas as pd
from typing import List, Dict
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from sqlalchemy.orm import Session
from models import AccidentFeature, AssociationRule
from datetime import datetime


def run_apriori(db: Session, min_support: float = 0.05, min_confidence: float = 0.6) -> List[Dict]:
    """
    从 t_accident_feature 表读取特征数据，执行 Apriori 挖掘
    返回规则列表
    """
    # 1. 读取特征数据
    features = db.query(AccidentFeature).all()
    if len(features) < 10:
        return []

    rows = []
    for f in features:
        rows.append({
            'accident_reason': f'accident:{f.accident_reason}',
            'vehicle_type': f'vehicle:{f.vehicle_type}',
            'time_period': f'period:{f.time_period}',
        })

    df = pd.DataFrame(rows)
    transactions = [set(row) for row in df.values.tolist()]

    # 2. One-hot 编码
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

    # 3. 频繁项集
    frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
    if frequent_itemsets.empty:
        return []

    # 4. 关联规则
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    if rules.empty:
        return []

    rules_sorted = rules.sort_values('lift', ascending=False)

    # 5. 保存到数据库
    params_key = f"{min_support},{min_confidence}"
    # 清除旧的同参数结果
    db.query(AssociationRule).filter(AssociationRule.params == params_key).delete()

    result = []
    for _, row in rules_sorted.iterrows():
        ant = ', '.join(sorted(row['antecedents']))
        con = ', '.join(sorted(row['consequents']))
        rule = AssociationRule(
            antecedents=ant,
            consequents=con,
            support=round(float(row['support']), 4),
            confidence=round(float(row['confidence']), 4),
            lift=round(float(row['lift']), 4),
            calc_time=datetime.now(),
            params=params_key,
        )
        db.add(rule)
        result.append({
            'antecedents': ant,
            'consequents': con,
            'support': round(float(row['support']), 4),
            'confidence': round(float(row['confidence']), 4),
            'lift': round(float(row['lift']), 4),
        })

    db.commit()
    return result
