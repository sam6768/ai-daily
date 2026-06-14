#!/usr/bin/env python3
"""
三木AI 每日一刻钟 - 自动生成脚本
每天自动生成 AI 资讯 HTML 简报
"""

import os
import json
import requests
import re
import sys
from datetime import datetime
import base64

# ============ 配置 ============
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO_NAME = 'sam6768/ai-daily'
TODAY = datetime.now()
TODAY_STR = TODAY.strftime('%Y-%m-%d')
TODAY_DISPLAY = TODAY.strftime('%Y年%m月%d日 %A').replace('Monday', '星期一').replace('Tuesday', '星期二').replace('Wednesday', '星期三').replace('Thursday', '星期四').replace('Friday', '星期五').replace('Saturday', '星期六').replace('Sunday', '星期日')

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
        print(f'Gemini API 状态: {resp.status_code}')
        if resp.status_code == 200:
            result = resp.json()
            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f'Gemini 返回长度: {len(text)} 字符')
                return text
            else:
                print(f'Gemini 返回空结果')
                return None
        else:
            print(f'Gemini API 错误: {resp.status_code} {resp.text[:500]}')
            return None
    except Exception as e:
        print(f'调用 Gemini 失败: {e}')
        return None

def generate_html_with_ai(today_str, today_display):
    """使用 AI 生成 HTML 简报"""
    
    prompt = f"""你是「三木AI 每日一刻钟」的 AI 资讯编辑。今天是 {today_display}。

请根据你了解的最新AI行业动态，生成一份精美的 HTML 日报。

## 内容要求

1. 生成 10-15 条最新 AI 资讯，按以下4个分类：
   - 技术前沿动态（模型/编程/硬件）
   - 国内外AI动态（监管/企业/机器人）
   - 投资与商业（股市/IPO/风险）
   - 政策与行业生态（政策/会议/应用）

2. 提炼 5 条今日要点（放在蓝色速览卡片）

3. 写一段 100-200 字的编辑精选评论

4. 每条资讯的"阅读原文→"链接用 # 占位

## 样式要求（内联在HTML中）

使用以下CSS变量和样式：

```
:root {{--bg:#f5f7fa;--card-bg:#ffffff;--text-primary:#1a1a2e;--text-secondary:#5a5a7a;--text-muted:#8a8aa0;--accent-blue:#2563eb;--accent-blue-light:#dbeafe;--accent-purple:#7c3aed;--accent-purple-light:#ede9fe;--accent-teal:#0d9488;--accent-teal-light:#ccfbf1;--accent-orange:#ea580c;--accent-orange-light:#ffedd5;--accent-green:#16a34a;--accent-green-light:#dcfce7;--border:#e2e8f0;--border-light:#f1f5f9;--radius:12px;--radius-sm:8px;--shadow:0 1px 3px rgba(0,0,0,0.04),0 4px 12px rgba(0,0,0,0.03);}}
```

关键样式类：
- `.container` max-width:720px; margin:0 auto; padding:24px 16px 48px;
- `.header` text-align:center; `.header-title` font-size:22px; font-weight:700;
- `.header-date` 蓝色圆角标签
- `.intro` 白色卡片，导语
- `.quick-tips` 蓝紫渐变背景，白色文字，5个要点
- `.section` 分类板块，`.section-header` 带图标和标题
- `.card` 白色卡片，`.card-badge` 标签，`.card-title` 标题，`.card-summary` 摘要，`.card-footer` 标签+链接
- `.editor-pick` 白色卡片，橙色左边框，深度观点
- `.footer` 页脚居中

颜色类：badge-blue/badge-purple/badge-teal/badge-orange, icon-blue/icon-purple/icon-teal/icon-orange

## 输出格式

只输出完整的 HTML 代码，从 `<!DOCTYPE html>` 开始到 `</html>` 结束。不要添加任何解释或 markdown 代码块标记。

标题：三木AI 每日一刻钟
副标题：每天15分钟，读懂AI世界
日期：{today_display}
页脚：三木AI 每日一刻钟 · 每天15分钟，读懂AI世界 | {today_display} · 共收录资讯XX条
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
    try:
        check_resp = requests.get(f'https://api.github.com/repos/{REPO_NAME}/contents/{daily_filename}', headers=headers, timeout=15)
        if check_resp.status_code == 200:
            sha = check_resp.json().get('sha', '')
    except Exception as e:
        print(f'获取 {daily_filename} SHA 失败: {e}')
    
    daily_data = {
        'message': f'自动更新：{today_str} 每日简报',
        'content': daily_content,
        'branch': 'main'
    }
    if sha:
        daily_data['sha'] = sha
    
    try:
        resp = requests.put(f'https://api.github.com/repos/{REPO_NAME}/contents/{daily_filename}', headers=headers, json=daily_data, timeout=30)
        if resp.status_code in [200, 201]:
            print(f'✅ {daily_filename} 上传成功')
            success_count += 1
        else:
            print(f'❌ {daily_filename} 上传失败: {resp.status_code} {resp.text[:200]}')
    except Exception as e:
        print(f'❌ {daily_filename} 上传异常: {e}')
    
    # 2. 更新 index.html
    index_sha = ''
    try:
        check_resp = requests.get(f'https://api.github.com/repos/{REPO_NAME}/contents/index.html', headers=headers, timeout=15)
        if check_resp.status_code == 200:
            index_sha = check_resp.json().get('sha', '')
    except Exception as e:
        print(f'获取 index.html SHA 失败: {e}')
    
    index_data = {
        'message': f'自动更新：{today_str} 主页',
        'content': daily_content,
        'branch': 'main'
    }
    if index_sha:
        index_data['sha'] = index_sha
    
    try:
        resp = requests.put(f'https://api.github.com/repos/{REPO_NAME}/contents/index.html', headers=headers, json=index_data, timeout=30)
        if resp.status_code in [200, 201]:
            print(f'✅ index.html 更新成功')
            success_count += 1
        else:
            print(f'❌ index.html 更新失败: {resp.status_code} {resp.text[:200]}')
    except Exception as e:
        print(f'❌ index.html 更新异常: {e}')
    
    # 3. 更新 manifest.json
    manifest_sha = ''
    manifest_content = {'dates': []}
    
    try:
        check_resp = requests.get(f'https://api.github.com/repos/{REPO_NAME}/contents/manifest.json', headers=headers, timeout=15)
        if check_resp.status_code == 200:
            manifest_sha = check_resp.json().get('sha', '')
            manifest_raw = check_resp.json().get('content', '')
            try:
                manifest_content = json.loads(base64.b64decode(manifest_raw).decode())
            except:
                pass
    except Exception as e:
        print(f'获取 manifest.json 失败: {e}')
    
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
    
    try:
        resp = requests.put(f'https://api.github.com/repos/{REPO_NAME}/contents/manifest.json', headers=headers, json=manifest_data, timeout=30)
        if resp.status_code in [200, 201]:
            print(f'✅ manifest.json 更新成功')
            success_count += 1
        else:
            print(f'❌ manifest.json 更新失败: {resp.status_code} {resp.text[:200]}')
    except Exception as e:
        print(f'❌ manifest.json 更新异常: {e}')
    
    return success_count >= 2

def main():
    print(f'=== 三木AI 每日一刻钟 自动生成 ===')
    print(f'日期: {TODAY_DISPLAY}')
    print(f'API Key: {"已设置" if GEMINI_API_KEY else "未设置"}')
    print(f'GitHub Token: {"已设置" if GITHUB_TOKEN else "未设置"}')
    
    if not GEMINI_API_KEY:
        print('❌ 错误：未设置 GEMINI_API_KEY 环境变量')
        sys.exit(1)
    
    # 生成 HTML
    print('\n🤖 调用 Gemini 生成简报...')
    html_content = generate_html_with_ai(TODAY_STR, TODAY_DISPLAY)
    
    if not html_content:
        print('❌ AI 生成失败，退出')
        sys.exit(1)
    
    # 验证 HTML 基本结构
    if '<!DOCTYPE html>' not in html_content or '</html>' not in html_content:
        print('❌ 生成的内容不是完整 HTML，退出')
        sys.exit(1)
    
    print(f'✅ HTML 生成成功，长度: {len(html_content)} 字符')
    
    # 保存到本地（备份）
    output_file = f'ai-daily-{TODAY_STR}.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f'✅ 本地备份已保存: {output_file}')
    
    # 推送到 GitHub
    print('\n🚀 推送到 GitHub...')
    success = update_github_files(html_content, TODAY_STR)
    
    if success:
        print('\n🎉 全部完成！网站已更新：https://ai.18kr.cn/')
    else:
        print('\n❌ 推送到 GitHub 部分失败')
        sys.exit(1)

if __name__ == '__main__':
    main()
