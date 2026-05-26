#!/usr/bin/env python3
"""
Text-to-SQL: 基于大模型自动生成SQL语句
作者: 张鸿昊 (20242081353)
说明: 使用DeepSeek V4大模型（兼容Anthropic API）对codebase_community数据库进行Text-to-SQL
"""
import json
import sqlite3
import os
import time
import httpx

# ==================== 配置 ====================
API_KEY = "sk-d0588f9b67444710968afb1ec4b3d298"  # 替换为你的DeepSeek API Key
API_BASE = "https://api.deepseek.com"  # DeepSeek API地址
MODEL = "deepseek-chat"  # DeepSeek V4模型

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "codebase_community.sqlite")
DEV_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dev_data.json")
TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data.json")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "张鸿昊_20242081353_test_result.json")

# 数据库Schema（硬编码以减少token消耗）
DATABASE_SCHEMA = """
-- 数据库: codebase_community (SQLite)
-- 共8张表: badges, comments, postHistory, postLinks, posts, tags, users, votes

CREATE TABLE badges (
    Id INTEGER PRIMARY KEY,
    UserId INTEGER,
    Name TEXT,
    Date DATETIME,
    FOREIGN KEY (UserId) REFERENCES users(Id)
);

CREATE TABLE comments (
    Id INTEGER PRIMARY KEY,
    PostId INTEGER,
    Score INTEGER,
    Text TEXT,
    CreationDate DATETIME,
    UserId INTEGER,
    UserDisplayName TEXT,
    FOREIGN KEY (PostId) REFERENCES posts(Id),
    FOREIGN KEY (UserId) REFERENCES users(Id)
);

CREATE TABLE postHistory (
    Id INTEGER PRIMARY KEY,
    PostHistoryTypeId INTEGER,
    PostId INTEGER,
    RevisionGUID TEXT,
    CreationDate DATETIME,
    UserId INTEGER,
    Text TEXT,
    Comment TEXT,
    UserDisplayName TEXT,
    FOREIGN KEY (PostId) REFERENCES posts(Id),
    FOREIGN KEY (UserId) REFERENCES users(Id)
);

CREATE TABLE postLinks (
    Id INTEGER PRIMARY KEY,
    CreationDate DATETIME,
    PostId INTEGER,
    RelatedPostId INTEGER,
    LinkTypeId INTEGER,
    FOREIGN KEY (PostId) REFERENCES posts(Id),
    FOREIGN KEY (RelatedPostId) REFERENCES posts(Id)
);

CREATE TABLE posts (
    Id INTEGER PRIMARY KEY,
    PostTypeId INTEGER,
    AcceptedAnswerId INTEGER,
    CreaionDate DATETIME,  -- 注意: 原表拼写为CreaionDate而非CreationDate
    Score INTEGER,
    ViewCount INTEGER,
    Body TEXT,
    OwnerUserId INTEGER,
    LasActivityDate DATETIME,  -- 注意: 原表拼写为LasActivityDate
    Title TEXT,
    Tags TEXT,
    AnswerCount INTEGER,
    CommentCount INTEGER,
    FavoriteCount INTEGER,
    LastEditorUserId INTEGER,
    LastEditDate DATETIME,
    CommunityOwnedDate DATETIME,
    ParentId INTEGER,
    ClosedDate DATETIME,
    OwnerDisplayName TEXT,
    LastEditorDisplayName TEXT,
    FOREIGN KEY (OwnerUserId) REFERENCES users(Id),
    FOREIGN KEY (ParentId) REFERENCES posts(Id)
);

CREATE TABLE tags (
    Id INTEGER PRIMARY KEY,
    TagName TEXT,
    Count INTEGER,
    ExcerptPostId INTEGER,
    WikiPostId INTEGER,
    FOREIGN KEY (ExcerptPostId) REFERENCES posts(Id)
);

CREATE TABLE users (
    Id INTEGER PRIMARY KEY,
    Reputation INTEGER,
    CreationDate DATETIME,
    DisplayName TEXT,
    LastAccessDate DATETIME,
    WebsiteUrl TEXT,
    Location TEXT,
    AboutMe TEXT,
    Views INTEGER,
    UpVotes INTEGER,
    DownVotes INTEGER,
    AccountId INTEGER,
    Age INTEGER,
    ProfileImageUrl TEXT
);

CREATE TABLE votes (
    Id INTEGER PRIMARY KEY,
    PostId INTEGER,
    VoteTypeId INTEGER,
    CreationDate DATE,
    UserId INTEGER,
    BountyAmount INTEGER,
    FOREIGN KEY (PostId) REFERENCES posts(Id),
    FOREIGN KEY (UserId) REFERENCES users(Id)
);
"""


def call_llm(messages, max_retries=3):
    """调用DeepSeek大模型API（OpenAI兼容格式）"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.0
    }

    for attempt in range(max_retries):
        try:
            response = httpx.post(
                f"{API_BASE}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  API调用失败 (尝试 {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None


def build_prompt(question, evidence=""):
    """构建Text-to-SQL的Prompt"""
    system_prompt = """你是一个专业的SQL生成专家。你的任务是根据用户的自然语言查询需求，针对codebase_community数据库生成对应的SQLite SQL语句。

重要规则：
1. 只输出一条SQL语句，不要输出任何解释、注释或代码块标记
2. SQL语句必须是有效的SQLite语法
3. SQLite不支持YEAR()等函数，使用STRFTIME('%Y', column)提取年份
4. posts表中的创建日期列名是 CreaionDate（不是CreationDate，注意拼写）
5. posts表中的最后活动日期列名是 LasActivityDate（不是LastActivityDate）
6. 使用IIF(condition, true_val, false_val)进行条件判断
7. 百分比计算时使用CAST(... AS REAL)避免整数除法
8. 字符串匹配使用LIKE时注意大小写
9. 日期格式通常为 'YYYY-MM-DD HH:MM:SS.0'"""

    user_prompt = f"""数据库Schema:
{DATABASE_SCHEMA}

查询需求: {question}"""

    if evidence and evidence.strip():
        user_prompt += f"\n\n参考提示(evidence): {evidence}"

    user_prompt += "\n\nSQL:"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


def clean_sql(sql_text):
    """清理模型输出的SQL"""
    if not sql_text:
        return ""
    sql_text = sql_text.strip()
    # 去除代码块标记
    if sql_text.startswith("```sql"):
        sql_text = sql_text[6:]
    elif sql_text.startswith("```"):
        sql_text = sql_text[3:]
    if sql_text.endswith("```"):
        sql_text = sql_text[:-3]
    sql_text = sql_text.strip()
    # 保留分号
    if not sql_text.endswith(";"):
        sql_text += ";"
    return sql_text


def validate_sql(db_path, sql):
    """验证SQL是否可以执行"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        return True, len(results)
    except Exception as e:
        return False, str(e)


def evaluate_dev_data(dev_data, db_path):
    """在dev_data上评估准确率"""
    print("\n" + "=" * 60)
    print("在 dev_data.json 上进行评估")
    print("=" * 60)

    correct = 0
    total = len(dev_data)

    for i, item in enumerate(dev_data):
        question = item["question"]
        evidence = item.get("evidence", "")
        gold_sql = item["SQL"]

        print(f"\n[{i+1}/{total}] {question[:70]}...")

        # 调用大模型生成SQL
        messages = build_prompt(question, evidence)
        generated_sql = call_llm(messages)
        generated_sql = clean_sql(generated_sql)

        if not generated_sql:
            print(f"  生成失败!")
            continue

        print(f"  生成: {generated_sql[:100]}")

        # 比较查询结果
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(gold_sql)
            gold_results = set(map(str, cursor.fetchall()))

            cursor.execute(generated_sql)
            gen_results = set(map(str, cursor.fetchall()))

            conn.close()

            if gold_results == gen_results:
                correct += 1
                print(f"  ✓ 正确!")
            else:
                print(f"  ✗ 结果不匹配")
                print(f"    期望({len(gold_results)}行): {list(gold_results)[:2]}")
                print(f"    实际({len(gen_results)}行): {list(gen_results)[:2]}")
        except Exception as e:
            print(f"  ✗ 执行错误: {e}")

        # 避免限流
        time.sleep(1)

    accuracy = correct / total * 100 if total > 0 else 0
    print(f"\n{'=' * 60}")
    print(f"dev_data 准确率: {correct}/{total} = {accuracy:.1f}%")
    print(f"{'=' * 60}")
    return accuracy


def process_test_data(test_data, db_path):
    """处理test_data并生成结果"""
    print("\n" + "=" * 60)
    print("处理 test_data.json")
    print("=" * 60)

    results = []

    for i, item in enumerate(test_data):
        question_id = item["question_id"]
        question = item["question"]
        evidence = item.get("evidence", "")

        print(f"\n[{i+1}/{len(test_data)}] Q{question_id}: {question[:70]}...")

        # 调用大模型生成SQL
        messages = build_prompt(question, evidence)
        generated_sql = call_llm(messages)
        generated_sql = clean_sql(generated_sql)

        if not generated_sql or generated_sql == ";":
            generated_sql = "SELECT 1;"
            print(f"  生成失败，使用fallback")
        else:
            print(f"  生成: {generated_sql[:100]}")

            # 验证SQL
            valid, info = validate_sql(db_path, generated_sql)
            if valid:
                print(f"  ✓ 有效 (返回{info}行)")
            else:
                print(f"  ⚠ 执行错误: {info}")

        result_item = {
            "question_id": question_id,
            "question": question,
            "evidence": evidence,
            "SQL": generated_sql
        }
        results.append(result_item)

        # 避免API限流
        time.sleep(1)

    return results


def main():
    print("=" * 60)
    print("Text-to-SQL 自动生成系统")
    print("作者: 张鸿昊 (20242081353)")
    print("数据库: codebase_community")
    print("模型: DeepSeek V4")
    print("=" * 60)

    # 检查数据库文件
    if not os.path.exists(DB_PATH):
        print(f"\n错误: 数据库文件不存在: {DB_PATH}")
        print("请确保 codebase_community.sqlite 已解压到当前目录")
        return

    # 检查API Key
    if API_KEY == "YOUR_API_KEY_HERE":
        print("\n⚠ 请先设置 API_KEY!")
        print("编辑 text2sql.py，将第15行的 API_KEY 替换为你的DeepSeek API Key")
        return

    # 加载数据
    print("\n[步骤1] 加载数据文件...")
    with open(DEV_DATA_PATH, 'r', encoding='utf-8') as f:
        dev_data = json.load(f)
    print(f"  dev_data: {len(dev_data)} 条")

    with open(TEST_DATA_PATH, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    print(f"  test_data: {len(test_data)} 条")

    # 在dev_data上评估
    print("\n[步骤2] 在dev_data上评估Prompt效果...")
    accuracy = evaluate_dev_data(dev_data, DB_PATH)

    # 处理test_data
    print("\n[步骤3] 在test_data上生成SQL...")
    results = process_test_data(test_data, DB_PATH)

    # 保存结果
    print("\n[步骤4] 保存结果...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  结果已保存到: {OUTPUT_PATH}")

    print("\n" + "=" * 60)
    print("完成! 提交内容:")
    print(f"  1. 代码压缩包: 张鸿昊_20242081353_Text2sql.zip")
    print(f"  2. 测试结果:   张鸿昊_20242081353_test_result.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
