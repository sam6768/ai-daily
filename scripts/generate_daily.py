#!/usr/bin/env python3
"""
三木AI 每日一刻钟 - 自动生成脚本
每天自动抓取 AI 资讯并生成 HTML 简报
"""

import os
import json
import requests
import re
from datetime import datetime
import base64

# ============ 配置 ============
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO_NAME = 'sam6768/ai-daily'
TODAY = datetime.now()
TODAY_STR = TODAY.strftime('%Y-%m-%d')
TODAY_DISPLAY = TODAY.strftime('%Y年%m月%d日 %A').replace('Monday', '星期一').replace('Tuesday', '星期二').replace('Wednesday', '星期三').replace('Thursday', '星期四').replace('Friday', '星期五').replace('Saturday', '星期六').replace('Sunday', '星期日')

NEWS_SOURCES = [
    {
        'name': '机器之心',
        'url': 'https://www.jiqizhixin.com/',
        'type': 'html'
    },
    {
        'name': '量子位',
        'url': 'https://www.qbitai.com/',
        'type': 'html'
    },
]

def fetch_web_news():
    """从多个网页源抓取 AI 资讯"""
    all_entries = []
    
    # 尝试抓取机器之心
    try:
        print('正在抓取: 机器之心')
        resp = requests.get('https://www.jiqizhixin.com/', timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            # 提取标题和链接（简单正则）
            titles = re.findall(r'<h2[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?</h2>', resp.text)
            for link, title in titles[:8]:
                title_clean = re.sub(r'<[^>]+>', '', title).strip()
                if title_clean and len(title_clean) > 10:
                    all_entries.append({
                        'title': title_clean,
                        'summary': '',
                        'link': link if link.startswith('http') else f'https://www.jiqizhixin.com{link}',
                        'source': '机器之心'
                    })
            print(f'  抓取到 {len(titles[:8])} 条')
    except Exception as e:
        print(f'  抓取失败: {e}')
    
    # 尝试抓取量子位
    try:
        print('正在抓取: 量子位')
        resp = requests.get('https://www.qbitai.com/', timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            titles = re.findall(r'<h2[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?</h2>', resp.text)
            for link, title in titles[:8]:
                title_clean = re.sub(r'<[^>]+>', '', title).strip()
                if title_clean and len(title_clean) > 10:
                    all_entries.append({
                        'title': title_clean,
                        'summary': '',
                        'link': link if link.startswith('http') else f'https://www.qbitai.com{link}',
                        'source': '量子位'
                    })
            print(f'  抓取到 {len(titles[:8])} 条')
    except Exception as e:
        print(f'  抓取失败: {e}')
    
    # 尝试 Hacker News
    try:
        print('正在抓取: Hacker News')
        resp = requests.get('https://news.ycombinator.com/', timeout=15)
        if resp.status_code == 200:
            # 提取标题
            titles = re.findall(r'<span class="titleline">.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?</span>', resp.text)
            for link, title in titles[:10]:
                title_clean = re.sub(r'<[^>]+>', '', title).strip()
                if title_clean and 'AI' in title_clean or '人工智能' in title_clean or 'GPT' in title_clean or 'LLM' in title_clean:
                    all_entries.append({
                        'title': title_clean,
                        'summary': '',
                        'link': link if link.startswith('http') else f'https://news.ycombinator.com/{link}',
                        'source': 'Hacker News'
                    })
            print(f'  抓取到 AI 相关 {len([e for e in all_entries if e["source"] == "Hacker News"])} 条')
    except Exception as e:
        print(f'  抓取失败: {e}')
    
    return all_entries

def call_gemini(prompt):
    """调用 Gemini API"""
    if not GEMINI_API_KEY:
        print('❌ 未设置 GEMINI_API_KEY')
        return None
    
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}'
    headers = {'Content-Type': 'application/json'}
    data = {
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {'temperature': 0.3, 'maxOutputTokens': 8192}
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=90)
        if resp.status_code == 200:
            result = resp.json()
            if 'candidates' in result and result['candidates']:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f'Gemini 返回空结果: {result}')
                return None
        else:
            print(f'Gemini API 错误: {resp.status_code} {resp.text[:200]}')
            return None
    except Exception as e:
        print(f'调用 Gemini 失败: {e}')
        return None

def generate_html_with_ai(news_items, today_str, today_display):
    """使用 AI 生成 HTML 简报"""
    
    # 准备新闻内容
    if news_items:
        news_text = ''
        for i, item in enumerate(news_items[:20], 1):
            news_text += f"{i}. 【{item['source']}】{item['title']}\n"
    else:
        news_text = '今日未能从RSS源抓取到新闻，请根据当前日期和已知的最新AI动态生成简报内容。'
    
    prompt = f"""你是「三木AI 每日一刻钟」的 AI 资讯编辑。请根据以下新闻标题和当前日期，生成一份精美的 HTML 日报。

## 要求

1. 从新闻中筛选出 10-15 条最有价值的 AI 资讯
2. 按以下4个分类整理：
   - 技术前沿动态（模型/编程/硬件）
   - 国内外AI动态（监管/企业/机器人）
   - 投资与商业（股市/IPO/风险）
   - 政策与行业生态（政策/会议/应用）

3. 提炼 5 条今日要点（放在蓝色速览卡片）

4. 写一段 100-200 字的编辑精选评论

5. 每条资讯的"阅读原文→"链接用 # 占位即可

## 格式要求

生成完整的 HTML 代码，包含以下CSS样式和结构：

```css
:root {{
  --bg: #f5f7fa; --card-bg: #ffffff; --text-primary: #1a1a2e;
  --text-secondary: #5a5a7a; --text-muted: #8a8aa0;
  --accent-blue: #2563eb; --accent-blue-light: #dbeafe;
  --accent-purple: #7c3aed; --accent-purple-light: #ede9fe;
  --accent-teal: #0d9488; --accent-teal-light: #ccfbf1;
  --accent-orange: #ea580c; --accent-orange-light: #ffedd5;
  --accent-green: #16a34a; --accent-green-light: #dcfce7;
  --border: #e2e8f0; --border-light: #f1f5f9;
  --radius: 12px; --radius-sm: 8px;
  --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--text-primary); line-height: 1.7; }}
.container {{ max-width: 720px; margin: 0 auto; padding: 24px 16px 48px; }}
.top-nav {{ background: var(--card-bg); border-radius: var(--radius); padding: 12px 16px; margin-bottom: 20px; box-shadow: var(--shadow); border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }}
.top-nav-title {{ font-size: 16px; font-weight: 700; color: var(--text-primary); }}
.top-nav-sub {{ font-size: 11px; color: var(--text-muted); }}
.header {{ text-align: center; margin-bottom: 28px; }}
.header-title {{ font-size: 22px; font-weight: 700; color: var(--text-primary); letter-spacing: 1px; }}
.header-sub {{ font-size: 13px; color: var(--text-muted); margin-top: 4px; }}
.header-date {{ display: inline-block; margin-top: 12px; padding: 4px 16px; background: var(--accent-blue-light); color: var(--accent-blue); border-radius: 20px; font-size: 13px; font-weight: 500; }}
.intro {{ background: var(--card-bg); border-radius: var(--radius); padding: 20px 24px; margin-bottom: 24px; box-shadow: var(--shadow); border: 1px solid var(--border); }}
.intro-text {{ font-size: 14px; color: var(--text-secondary); line-height: 1.8; }}
.quick-tips {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); border-radius: var(--radius); padding: 20px 24px; margin-bottom: 24px; color: white; box-shadow: var(--shadow); }}
.quick-tips-title {{ font-size: 15px; font-weight: 600; margin-bottom: 12px; }}
.quick-tips-list {{ list-style: none; }}
.quick-tips-list li {{ font-size: 13px; line-height: 1.9; padding-left: 16px; position: relative; opacity: 0.95; }}
.quick-tips-list li::before {{ content: ''; position: absolute; left: 0; top: 10px; width: 6px; height: 6px; background: rgba(255,255,255,0.7); border-radius: 50%; }}
.section {{ margin-bottom: 24px; }}
.section-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 16px; padding-left: 4px; }}
.section-icon {{ width: 28px; height: 28px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 14px; }}
.section-title {{ font-size: 15px; font-weight: 600; color: var(--text-primary); }}
.section-count {{ margin-left: auto; font-size: 12px; color: var(--text-muted); background: var(--border-light); padding: 2px 10px; border-radius: 12px; }}
.card {{ background: var(--card-bg); border-radius: var(--radius); padding: 18px 20px; margin-bottom: 12px; box-shadow: var(--shadow); border: 1px solid var(--border); }}
.card-header {{ display: flex; align-items: flex-start; gap: 10px; margin-bottom: 8px; }}
.card-badge {{ flex-shrink: 0; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 500; }}
.card-title {{ font-size: 14px; font-weight: 600; color: var(--text-primary); line-height: 1.5; flex: 1; }}
.card-summary {{ font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 10px; }}
.card-footer {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
.card-tag {{ font-size: 11px; color: var(--text-muted); background: var(--border-light); padding: 2px 8px; border-radius: 4px; }}
.card-link {{ font-size: 12px; color: var(--accent-blue); text-decoration: none; margin-left: auto; }}
.badge-blue {{ background: var(--accent-blue-light); color: var(--accent-blue); }}
.badge-purple {{ background: var(--accent-purple-light); color: var(--accent-purple); }}
.badge-teal {{ background: var(--accent-teal-light); color: var(--accent-teal); }}
.badge-orange {{ background: var(--accent-orange-light); color: var(--accent-orange); }}
.icon-blue {{ background: var(--accent-blue-light); color: var(--accent-blue); }}
.icon-purple {{ background: var(--accent-purple-light); color: var(--accent-purple); }}
.icon-teal {{ background: var(--accent-teal-light); color: var(--accent-teal); }}
.icon-orange {{ background: var(--accent-orange-light); color: var(--accent-orange); }}
.editor-pick {{ background: var(--card-bg); border-radius: var(--radius); padding: 20px 24px; box-shadow: var(--shadow); border: 1px solid var(--border); border-left: 3px solid var(--accent-orange); }}
.editor-pick-title {{ font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }}
.editor-pick-content {{ font-size: 13px; color: var(--text-secondary); line-height: 1.8; }}
.editor-pick-content p {{ margin-bottom: 8px; }}
.editor-pick-content strong {{ color: var(--text-primary); font-weight: 600; }}
.footer {{ text-align: center; margin-top: 32px; padding-top: 24px; border-top: 1px solid var(--border); }}
.footer-text {{ font-size: 12px; color: var(--text-muted); }}
.footer-brand {{ font-weight: 600; color: var(--text-secondary); }}
@media (max-width: 480px) {{ .container {{ padding: 16px 12px 32px; }} .card {{ padding: 14px 16px; }} }}
```

HTML结构：
1. 顶部导航栏 `.top-nav`：品牌名 + 日期显示
2. Header：标题 + 副标题 + 日期标签
3. 今日概览 `.intro`
4. 蓝色要点速览 `.quick-tips`
5. 四个分类板块 `.section`
6. 编辑精选 `.editor-pick`
7. 页脚 `.footer`

## 今日信息

- 日期: {today_display}
- ISO 日期: {today_str}

## 新闻素材

{news_text}

## 输出

只输出完整的 HTML 代码，从 `<!DOCTYPE html>` 开始到 `</html>` 结束。不要添加任何解释或 markdown 代码块标记。
"""
    
    print('正在调用 Gemini 生成简报...')
    html = call_gemini(prompt)
    
    # 清理可能的 markdown 代码块
    if html:
        html = html.strip()
        if html.startswith('```html'):
            html = html[7:]
        if html.startswith('```'):
            html = html[3:]
        if html.endswith('```'):
            html = html[:-3]
        html = html.strip()
    
    return html

def update_github_files(html_content, today_str):
    """通过 GitHub API 更新文件"""
    if not GITHUB_TOKEN:
        print('❌ 未设置 GITHUB_TOKEN')
        return False
    
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    success_count = 0
    
    # 1. 更新当天的简报文件
    daily_filename = f'ai-daily-{today_str}.html'
    daily_content = base64.b64encode(html_content.encode('utf-8')).decode()
    
    sha = ''
    check_resp = requests.get(f'https://api.github.com/repos/{REPO_NAME}/contents/{daily_filename}', headers=headers, timeout=15)
    if check_resp.status_code == 200:
        sha = check_resp.json().get('sha', '')
    
    daily_data = {
        'message': f'自动更新：{today_str} 每日简报',
        'content': daily_content,
        'branch': 'main'
    }
    if sha:
        daily_data['sha'] = sha
    
    resp = requests.put(f'https://api.github.com/repos/{REPO_NAME}/contents/{daily_filename}', headers=headers, json=daily_data, timeout=30)
    if resp.status_code in [200, 201]:
        print(f'✅ {daily_filename} 上传成功')
        success_count += 1
    else:
        print(f'❌ {daily_filename} 上传失败: {resp.status_code} {resp.text[:200]}')
    
    # 2. 更新 index.html
    index_sha = ''
    check_resp = requests.get(f'https://api.github.com/repos/{REPO_NAME}/contents/index.html', headers=headers, timeout=15)
    if check_resp.status_code == 200:
        index_sha = check_resp.json().get('sha', '')
    
    index_data = {
        'message': f'自动更新：{today_str} 主页',
        'content': daily_content,
        'branch': 'main'
    }
    if index_sha:
        index_data['sha'] = index_sha
    
    resp = requests.put(f'https://api.github.com/repos/{REPO_NAME}/contents/index.html', headers=headers, json=index_data, timeout=30)
    if resp.status_code in [200, 201]:
        print(f'✅ index.html 更新成功')
        success_count += 1
    else:
        print(f'❌ index.html 更新失败: {resp.status_code} {resp.text[:200]}')
    
    # 3. 更新 manifest.json
    manifest_sha = ''
    manifest_content = {'dates': []}
    
    check_resp = requests.get(f'https://api.github.com/repos/{REPO_NAME}/contents/manifest.json', headers=headers, timeout=15)
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
    
    manifest_b64 = base64.b64encode(json.dumps(manifest_content, ensure_ascii=False, indent=2).encode('utf-8')).decode()
    
    manifest_data = {
        'message': f'自动更新：{today_str} manifest',
        'content': manifest_b64,
        'branch': 'main'
    }
    if manifest_sha:
        manifest_data['sha'] = manifest_sha
    
    resp = requests.put(f'https://api.github.com/repos/{REPO_NAME}/contents/manifest.json', headers=headers, json=manifest_data, timeout=30)
    if resp.status_code in [200, 201]:
        print(f'✅ manifest.json 更新成功')
        success_count += 1
    else:
        print(f'❌ manifest.json 更新失败: {resp.status_code} {resp.text[:200]}')
    
    return success_count >= 2  # 至少 index 和 daily 成功

def main():
    print(f'=== 三木AI 每日一刻钟 自动生成 ===')
    print(f'日期: {TODAY_DISPLAY}')
    print(f'API Key: {"已设置" if GEMINI_API_KEY else "未设置"}')
    print(f'GitHub Token: {"已设置" if GITHUB_TOKEN else "未设置"}')
    
    # 1. 抓取新闻
    print('\n📰 第1步：抓取 AI 资讯...')
    news_items = fetch_web_news()
    print(f'共抓取到 {len(news_items)} 条资讯')
    
    # 2. 生成 HTML
    print('\n🤖 第2步：调用 AI 生成简报...')
    html_content = generate_html_with_ai(news_items, TODAY_STR, TODAY_DISPLAY)
    
    if not html_content:
        print('❌ AI 生成失败，退出')
        exit(1)
    
    # 验证 HTML 基本结构
    if '<!DOCTYPE html>' not in html_content or '</html>' not in html_content:
        print('❌ 生成的内容不是完整 HTML，退出')
        exit(1)
    
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
        print('\n❌ 推送到 GitHub 部分失败')
        exit(1)

if __name__ == '__main__':
    main()
