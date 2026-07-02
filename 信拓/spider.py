import requests
from bs4 import BeautifulSoup
import time
import random
import re
import os
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
# 温州交警网
def get_wenzhou_list_urls(max_pages=50):
    urls = []
    for page in range(max_pages):
        if page == 0:
            page_url = 'https://wzjj.wenzhou.gov.cn/col/col1475904/index.html'
        else:
            page_url = f'https://wzjj.wenzhou.gov.cn/col/col1475904/index_{page}.html'
        print(f"温州交警网 - 列表页: {page_url}")
        try:
            resp = requests.get(page_url, headers=HEADERS, timeout=10)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            container = soup.find('div', class_='page-content')
            if not container:
                break
            for li in container.find_all('li'):
                a = li.find('a', href=True)
                if a:
                    href = a['href']
                    full = urljoin('https://wzjj.wenzhou.gov.cn', href)
                    urls.append(full)
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"温州列表页出错: {e}")
            continue
    return list(set(urls))
def parse_wenzhou_detail(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        title_tag = soup.find('div', class_='titt')
        if not title_tag:
            return []
        title = title_tag.get_text().strip()
        pub_time = ''
        time_span = soup.find('span', string=re.compile(r'日期：'))
        if time_span:
            time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', time_span.get_text())
            if time_match:
                pub_time = time_match.group(1)
        source_span = soup.find('span', string=re.compile(r'来源：'))
        source = source_span.get_text().replace('来源：', '').strip() if source_span else '温州交警'
        content_parts = []
        for p in soup.find_all('p', style=re.compile(r'text-indent:\s*2em')):
            content_parts.append(p.get_text().strip())
        content = ' '.join(content_parts)
        if not content:
            content_div = soup.find('div', class_='content') or soup.find('div', class_='article')
            if content_div:
                content = content_div.get_text().strip()
        location = ''
        loc_match = re.search(r'([\u4e00-\u9fa5]{2,}?(?:市|县|区|路|街道))', title + content[:100])
        if loc_match:
            location = loc_match.group(1)
        return [{
            'url': url, 'title': title, 'pub_time': pub_time,
            'location': location, 'content': content, 'source': source
        }]
    except Exception as e:
        print(f"温州详情页出错: {e}, {url}")
        return []
#福建交警网
def get_fujian_list_urls(max_pages=15):
    urls = []
    for page in range(1, max_pages + 1):
        if page == 1:
            page_url = 'http://fjjj.fjsen.com/node_305211.htm'
        else:
            page_url = f'http://fjjj.fjsen.com/node_305211_{page}.htm'
        print(f"福建交警网 - 列表页: {page_url}")
        try:
            resp = requests.get(page_url, headers=HEADERS, timeout=10)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            ul = soup.find('ul', class_='list_page')
            if not ul:
                break
            for li in ul.find_all('li'):
                a = li.find('a', href=True)
                if a:
                    full = urljoin('http://fjjj.fjsen.com', a['href'])
                    urls.append(full)
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"福建列表页出错: {e}")
            continue
    return list(set(urls))
def parse_fujian_detail(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        title_tag = soup.find('div', class_='zs_h1')
        if not title_tag:
            return []
        title = title_tag.get_text().strip()
        pub_time = ''
        time_span = soup.find('span', style=re.compile(r'padding-left:\s*400px'))
        if time_span:
            time_match = re.search(r'\d{4}-\d{2}-\d{2}', time_span.get_text())
            if time_match:
                pub_time = time_match.group()
        source_span = soup.find('span', string=re.compile(r'来源：'))
        source = source_span.get_text().replace('来源：', '').strip() if source_span else '福建交警网'
        content_parts = [p.get_text().strip() for p in soup.find_all('p', style=re.compile(r'text-indent:\s*2em'))]
        content = ' '.join(content_parts)
        if not content:
            content_div = soup.find('div', class_=re.compile(r'content'))
            if content_div:
                content = content_div.get_text().strip()
        location = ''
        loc_match = re.search(r'([\u4e00-\u9fa5]{2,}?(?:市|县|区))', title)
        if loc_match:
            location = loc_match.group(1)
        return [{
            'url': url, 'title': title, 'pub_time': pub_time,
            'location': location, 'content': content, 'source': source
        }]
    except Exception as e:
        print(f"福建详情页出错: {e}, {url}")
        return []
# 铜仁市公安交管局（聚合页拆分）
def get_tongren_list_urls(max_pages=10):
    urls = []
    base = 'http://jjzd.trs.gov.cn/xxgk_500457/pgt/'
    for page in range(max_pages):
        if page == 0:
            page_url = base
        else:
            page_url = f'{base}index_{page}.html'
        print(f"铜仁交警 - 列表页: {page_url}")
        try:
            resp = requests.get(page_url, headers=HEADERS, timeout=10)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            ul = soup.find('ul', class_='list lh24 f14')
            if not ul:
                break
            for li in ul.find_all('li'):
                a = li.find('a', href=True)
                if a:
                    full = urljoin('http://jjzd.trs.gov.cn', a['href'])
                    urls.append(full)
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"铜仁列表页出错: {e}")
            continue
    return list(set(urls))
def parse_tongren_detail(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        title_tag = soup.find('h1')
        if not title_tag:
            return []
        title = title_tag.get_text().strip()
        pub_time = ''
        time_script = soup.find('script', string=re.compile(r'pubdata'))
        if time_script:
            match = re.search(r"pubdata\s*=\s*'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})'", time_script.string)
            if match:
                pub_time = match.group(1)
        source_script = soup.find('script', string=re.compile(r'wzly'))
        source = '铜仁市公安交管局'
        if source_script:
            match = re.search(r"wzly\s*=\s*'([^']+)'", source_script.string)
            if match:
                source = match.group(1)
        content_div = soup.find('div', class_='content') or soup.find('div', class_='article')
        if not content_div:
            content_parts = []
            for sibling in title_tag.find_next_siblings():
                if sibling.name in ['p', 'div', 'span'] and 'fwtj' not in sibling.get('class', []):
                    content_parts.append(sibling.get_text().strip())
            content = ' '.join(content_parts)
        else:
            content = content_div.get_text().strip()
        if not content:
            return []
        # 拆分聚合案例
        cases = []
        if '案例' in content:
            parts = re.split(r'(?=案例\s*[一二三四五六七八九十\d]+)', content)
        elif re.search(r'\d+\.', content):
            parts = re.split(r'(?=\d+\.)', content)
        else:
            parts = [content]
        for part in parts:
            if len(part.strip()) < 20:
                continue
            # 提取地点
            loc_match = re.search(r'([\u4e00-\u9fa5]{2,}?(?:市|县|区|路|街道))', part[:100])
            location = loc_match.group(1) if loc_match else ''
            cases.append({
                'url': url,
                'title': title,
                'pub_time': pub_time,
                'location': location,
                'content': part.strip(),
                'source': source
            })
        return cases if cases else [{
            'url': url, 'title': title, 'pub_time': pub_time,
            'location': '', 'content': content, 'source': source
        }]
    except Exception as e:
        print(f"铜仁详情页出错: {e}, {url}")
        return []

#南京交警 
def get_nanjing_list_urls(max_pages=31):
    """
    获取南京交警网交通管理栏目列表页中的详情页URL。
    :param max_pages: 最大爬取页数（网站共31页）
    """
    urls = []
    base_list_url = 'https://gaj.nanjing.gov.cn/jtgl/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    for page in range(max_pages):
        if page == 0:
            page_url = base_list_url + 'index.html'
        else:
            page_url = f'{base_list_url}index_{page}.html'
        print(f"南京交警 - 列表页: {page_url}")
        try:
            resp = requests.get(page_url, headers=headers, timeout=10)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            # 列表容器：div.list-right-con > ul > li
            container = soup.find('div', class_='list-right-con')
            if not container:
                print(f"  未找到列表容器，可能已到末尾")
                break
            
            li_tags = container.find_all('li')
            if not li_tags:
                print(f"  本页无新闻项")
                break
            
            for li in li_tags:
                a = li.find('a', href=True)
                if a:
                    href = a['href']
                    # 处理相对路径（如 ./202604/t20260413_5822214.html）
                    if href.startswith('./'):
                        href = href[2:]
                    full_url = urljoin(base_list_url, href)
                    urls.append(full_url)
            
            print(f"  提取到 {len(li_tags)} 条链接")
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"南京列表页出错: {e}")
            continue
    unique_urls = list(set(urls))
    print(f"南京交警共提取到 {len(unique_urls)} 个详情页链接")
    return unique_urls

def parse_nanjing_detail(url):
    """
    解析南京交警新闻详情页，提取标题、发布时间、事故地点、新闻正文、来源等信息。
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        # 1. 标题：class="doctitle"
        title_tag = soup.find('div', class_='doctitle')
        if not title_tag:
            print(f"未找到标题, URL: {url}")
            return []
        title = title_tag.get_text().strip()
        # 2. 发布时间：在 class="field_con1" 的文本中，格式："发布时间：2026-03-02 11:01"
        pub_time = ''
        info_div = soup.find('div', class_='field_con1')
        if info_div:
            info_text = info_div.get_text()
            time_match = re.search(r'发布时间：(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', info_text)
            if time_match:
                pub_time = time_match.group(1)
        # 3. 来源：从 field_con1 中提取 "责任编辑：南京市公安局"
        source = '南京交警'
        if info_div:
            source_match = re.search(r'责任编辑：([^\s]+)', info_div.get_text())
            if source_match:
                source = source_match.group(1)
        # 4. 正文：class="view TRS_UEDITOR trs_paper_default trs_web" 或类似容器
        content_div = soup.find('div', class_='view') or soup.find('div', class_='TRS_UEDITOR')
        content = ''
        if content_div:
            p_tags = content_div.find_all('p')
            if p_tags:
                content = ' '.join([p.get_text().strip() for p in p_tags])
            else:
                content = content_div.get_text().strip()
            content = re.sub(r'\s+', ' ', content)
        if not content:
            print(f"未找到正文内容, URL: {url}")
            return []
        # 5. 事故地点：从标题或正文前部提取地名
        location = ''
        loc_match = re.search(r'([\u4e00-\u9fa5]{2,}?(?:市|区|县|路|街道|高速))', title + content[:100])
        if loc_match:
            location = loc_match.group(1)
        if not location:
            location = '南京市'  
        
        return [{
            'url': url,
            'title': title,
            'pub_time': pub_time,
            'location': location,
            'content': content,
            'source': source
        }]
    except Exception as e:
        print(f"南京详情页出错: {e}, {url}")
        return []
# 主程序
def main():
    all_data = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 1. 温州交警网
    print("\n===== 温州交警网 =====")
    wz_urls = get_wenzhou_list_urls(max_pages=50)
    print(f"获取到 {len(wz_urls)} 个详情页链接")
    for i, url in enumerate(wz_urls, 1):
        print(f"温州 [{i}/{len(wz_urls)}]")
        all_data.extend(parse_wenzhou_detail(url))
        time.sleep(random.uniform(1, 2))
    # 2. 福建交警网
    print("\n===== 福建交警网 =====")
    fj_urls = get_fujian_list_urls(max_pages=15)
    print(f"获取到 {len(fj_urls)} 个详情页链接")
    for i, url in enumerate(fj_urls, 1):
        print(f"福建 [{i}/{len(fj_urls)}]")
        all_data.extend(parse_fujian_detail(url))
        time.sleep(random.uniform(1, 2))
    # 3. 铜仁市公安交管局
    print("\n===== 铜仁市公安交管局 =====")
    tr_urls = get_tongren_list_urls(max_pages=10)
    print(f"获取到 {len(tr_urls)} 个详情页链接")
    for i, url in enumerate(tr_urls, 1):
        print(f"铜仁 [{i}/{len(tr_urls)}]")
        cases = parse_tongren_detail(url)
        all_data.extend(cases)
        print(f"  该页拆分出 {len(cases)} 条案例")
        time.sleep(random.uniform(1, 2))
    # 4. 南京交警
    print("\n===== 南京交警 =====")
    nj_urls = get_nanjing_list_urls(max_pages=31)  # 共31页
    print(f"获取到 {len(nj_urls)} 个详情页链接")
    for i, url in enumerate(nj_urls, 1):
        print(f"南京 [{i}/{len(nj_urls)}]")
        cases = parse_nanjing_detail(url)
        all_data.extend(cases)
        if i % 10 == 0:
            print(f"  已处理 {i} 个页面")
        time.sleep(random.uniform(1, 2))
    # 保存最终结果
    if all_data:
        df = pd.DataFrame(all_data)
        df = df.drop_duplicates(subset=['url', 'content'])
        final_path = os.path.join(script_dir, 'traffic_accidents_final.csv')
        df.to_csv(final_path, index=False, encoding='utf-8-sig')
        print(f"\n全部完成！总计 {len(df)} 条数据，保存至 {final_path}")
    else:
        print("\n未获取到任何数据。")
if __name__ == '__main__':
    main()