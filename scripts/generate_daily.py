#!/usr/bin/env python3
"""
三木AI 每日一刻钟 - 自动生成脚本
每天自动抓取 AI 资讯并生成 HTML 简报
"""

import os
import json
import glob
import requests
from datetime import datetime, timedelta
import feedparser
import base64

# ============ 配置 ============
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
REPO_NAME = 'sam6768/ai-daily'
TODAY = datetime.now()
TODAY_STR = TODAY.strftime('%Y-%m-%d')
TODAY_DISPLAY = TODAY.strftime('%Y年%m月%d日 %A').replace('Monday', '星期一').replace('Tuesday', '星期二').replace('Wednesday', '星期三').replace('Thursday', '星期四').replace('Friday', '星期五').replace('Saturday', '星期六').replace('Sunday', '星期日')

RSS_FEEDS = [
    'https://rsshub.app/36kr/news/ai',
    'https://rsshub.app/jiqizhixin/article',
    'https://news.ycombinator.com/rss',
    'https://rsshub.app/techcrunch/tag/artificial-intelligence',
]

def fetch_rss_news():
    """从 RSS 源抓取 AI 资讯"""
    all_entries = []
    
    for feed_url in RSS_FEEDS:
        try:
            print(f'正在抓取: {feed_url}')
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:  # 每个源取前10条
                all_entries.append({
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', '')[:300],
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': feed.feed.get('title', feed_url)
                })
        except Exception as e:
            print(f'抓取失败 {feed_url}: {e}')
            continue
    
    return all_entries

def call_gemini(prompt):
    """调用 Gemini API"""
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}'
    headers = {'Content-Type': 'application/json'}
    data = {
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {'temperature': 0.3, 'maxOutputTokens': 8192}
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        if resp.status_code == 200:
            return resp.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f'Gemini API 错误: {resp.status_code} {resp.text}')
            return None
    except Exception as e:
        print(f'调用 Gemini 失败: {e}')
        return None

def generate_html_with_ai(news_items, today_str, today_display):
    """使用 AI 生成 HTML 简报"""
    
    # 准备新闻内容
    news_text = ''
    for i, item in enumerate(news_items[:20], 1):
        news_text += f"{i}. 【{item['source']}】{item['title']}\n   摘要: {item['summary']}\n   链接: {item['link']}\n\n"
    
    prompt = f"""你是「三木AI 每日一刻钟」的 AI 资讯编辑。请根据以下今日抓取的新闻，生成一份精美的 HTML 日报。

## 要求

1. 从新闻中筛选出 10-15 条最有价值的 AI 资讯
2. 按以下4个分类整理：
   - 技术前沿动态（模型/编程/硬件）
   - 国内外AI动态（监管/企业/机器人）
   - 投资与商业（股市/IPO/风险）
   - 政策与行业生态（政策/会议/应用）

3. 提炼 5 条今日要点（放在蓝色速览卡片）

4. 写一段 100-200 字的编辑精选评论

## 格式要求

生成完整的 HTML 代码，包含：
- 顶部导航栏（带日历功能，参考现有 index.html 的 .top-nav 样式）
- 今日概览（intro 区域）
- 蓝色要点速览卡片（quick-tips）
- 四个分类板块（section + card）
- 编辑精选（editor-pick，橙色左边框）
- 页脚（footer）

## 样式规范

- 使用现有的 CSS 变量（--bg, --card-bg, --accent-blue 等）
- 保持蓝紫色系、卡片式布局
- 响应式设计

## 今日信息

- 日期: {today_display}
- ISO 日期: {today_str}

## 新闻素材

{news_text}

## 输出

只输出完整的 HTML 代码，从 <!DOCTYPE html> 开始到 </html> 结束。不要添加任何解释。
"""
    
    print('正在调用 Gemini 生成简报...')
    html = call_gemini(prompt)
    return html

def update_github_files(html_content, today_str):
    """通过 GitHub API 更新文件"""
    token = os.environ.get('GITHUB_TOKEN', '')
    if not token:
        print('缺少 GITHUB_TOKEN 环境变量')
        return False
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # 1. 更新当天的简报文件
    daily_filename = f'ai-daily-{today_str}.html'
    daily_content = base64.b64encode(html_content.encode()).decode()
    
    # 获取文件 SHA（如果已存在）
    sha = ''
    check_resp = requests.get(f'https://api.github.com/repos/{REPO_NAME}/contents/{daily_filename}', headers=headers)
    if check_resp.status_code == 200:
        sha = check_resp.json().get('sha', '')
    
    # 上传当天简报
    daily_data = {
        'message': f'自动更新：{today_str} 每日简报',
        'content': daily_content,
        'branch': 'main'
    }
    if sha:
        daily_data['sha'] = sha
    
    resp = requests.put(f'https://api.github.com/repos/{REPO_NAME}/contents/{daily_filename}', headers=headers, json=daily_data)
    if resp.status_code in [200, 201]:
        print(f'✅ {daily_filename} 上传成功')
    else:
        print(f'❌ {daily_filename} 上传失败: {resp.status_code} {resp.text}')
        return False
    
    # 2. 更新 index.html（主页显示今天的内容）
    index_filename = 'index.html'
    index_sha = ''
    check_resp = requests.get(f'https://api.github.com/repos/{REPO_NAME}/contents/{index_filename}', headers=headers)
    if check_resp.status_code == 200:
        index_sha = check_resp.json().get('sha', '')
    
    index_data = {
        'message': f'自动更新：{today_str} 主页',
        'content': daily_content,  # 主页内容和当天简报一样
        'branch': 'main'
    }
    if index_sha:
        index_data['sha'] = index_sha
    
    resp = requests.put(f'https://api.github.com/repos/{REPO_NAME}/contents/{index_filename}', headers=headers, json=index_data)
    if resp.status_code in [200, 201]:
        print(f'✅ {index_filename} 更新成功')
    else:
        print(f'❌ {index_filename} 更新失败: {resp.status_code} {resp.text}')
        return False
    
    # 3. 更新 manifest.json
    manifest_filename = 'manifest.json'
    manifest_sha = ''
    manifest_content = {'dates': []}
    
    check_resp = requests.get(f'https://api.github.com/repos/{REPO_NAME}/contents/{manifest_filename}', headers=headers)
    if check_resp.status_code == 200:
        manifest_sha = check_resp.json().get('sha', '')
        manifest_raw = check_resp.json().get('content', '')
        try:
            manifest_content = json.loads(base64.b64decode(manifest_raw).decode())
        except:
            pass
    
    if today_str not in manifest_content.get('dates', []):
        manifest_content.setdefault('dates', []).append(today_str)
        manifest_content['dates'].sort(reverse=True)
    
    manifest_b64 = base64.b64encode(json.dumps(manifest_content, ensure_ascii=False, indent=2).encode()).decode()
    
    manifest_data = {
        'message': f'自动更新：{today_str} manifest.json',
        'content': manifest_b64,
        'branch': 'main'
    }
    if manifest_sha:
        manifest_data['sha'] = manifest_sha
    
    resp = requests.put(f'https://api.github.com/repos/{REPO_NAME}/contents/{manifest_filename}', headers=headers, json=manifest_data)
    if resp.status_code in [200, 201]:
        print(f'✅ {manifest_filename} 更新成功')
    else:
        print(f'❌ {manifest_filename} 更新失败: {resp.status_code} {resp.text}')
        return False
    
    return True

def main():
    print(f'=== 三木AI 每日一刻钟 自动生成 ===')
    print(f'日期: {TODAY_DISPLAY}')
    
    # 1. 抓取新闻
    print('\n📰 第1步：抓取 AI 资讯...')
    news_items = fetch_rss_news()
    print(f'共抓取到 {len(news_items)} 条资讯')
    
    if not news_items:
        print('❌ 没有抓取到任何资讯，退出')
        return
    
    # 2. 生成 HTML
    print('\n🤖 第2步：调用 AI 生成简报...')
    html_content = generate_html_with_ai(news_items, TODAY_STR, TODAY_DISPLAY)
    
    if not html_content:
        print('❌ AI 生成失败，退出')
        return
    
    # 3. 保存到本地（备份）
    output_file = f'ai-daily-{TODAY_STR}.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f'✅ 本地备份已保存: {output_file}')
    
    # 4. 推送到 GitHub
    print('\n🚀 第3步：推送到 GitHub...')
    success = update_github_files(html_content, TODAY_STR)
    
    if success:
        print('\n🎉 全部完成！网站已更新：https://ai.18kr.cn/')
    else:
        print('\n❌ 推送到 GitHub 失败，请检查配置')

if __name__ == '__main__':
    main()
