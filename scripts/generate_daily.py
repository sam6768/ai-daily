#!/usr/bin/env python3
"""
三木AI 每日一刻钟 - 自动生成脚本
每天自动生成 AI 资讯 HTML 简报
"""

import os
import json
import requests
from datetime import datetime
import base64

# ============ 配置 ============
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO_NAME = 'sam6768/ai-daily'
TODAY = datetime.now()
TODAY_STR = TODAY.strftime('%Y-%m-%d')
TODAY_DISPLAY = TODAY.strftime('%Y年%m月%d日 %A').replace('Monday', '星期一').replace('Tuesday', '星期二').replace('Wednesday', '星期三').replace('Thursday', '星期四').replace('Friday', '星期五').replace('Saturday', '星期六').replace('Sunday', '星期日')

def log(msg):
    """打印并记录日志"""
    print(msg)
    with open('generate.log', 'a', encoding='utf-8') as f:
        f.write(f'{datetime.now().isoformat()} {msg}\n')

def call_openrouter(prompt):
    """调用 OpenRouter API"""
    if not OPENROUTER_API_KEY:
        log('❌ 未设置 OPENROUTER_API_KEY')
        return None
    
    url = 'https://openrouter.ai/api/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://ai.18kr.cn/',
        'X-Title': 'Sanmu AI Daily'
    }
    data = {
        'model': 'google/gemini-2.5-flash',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.3,
        'max_tokens': 8192
    }
    
    try:
        log(f'调用 OpenRouter API...')
        resp = requests.post(url, headers=headers, json=data, timeout=120)
        log(f'OpenRouter API 状态: {resp.status_code}')
        
        if resp.status_code == 200:
            result = resp.json()
            if 'choices' in result and result['choices']:
                text = result['choices'][0]['message']['content']
                log(f'✅ OpenRouter 返回成功，长度: {len(text)}')
                return text
            else:
                log(f'⚠️ OpenRouter 返回空结果: {json.dumps(result)[:500]}')
                return None
        else:
            log(f'❌ OpenRouter API 错误: {resp.status_code} {resp.text[:500]}')
            return None
    except Exception as e:
        log(f'❌ 调用 OpenRouter 异常: {e}')
        return None

def generate_html_with_ai(today_str, today_display):
    """使用 AI 生成 HTML 简报"""
    
    prompt = f"""你是「三木AI 每日一刻钟」的 AI 资讯编辑。今天是 {today_display}。

请根据你了解的最新AI行业动态（截至2026年6月），生成一份精美的 HTML 日报。

## 内容要求

1. 生成 10-15 条最新 AI 资讯，按以下4个分类：
   - 技术前沿动态（模型/编程/硬件）- 3条
   - 国内外AI动态（监管/企业/机器人）- 4条
   - 投资与商业（股市/IPO/风险）- 3条
   - 政策与行业生态（政策/会议/应用）- 3条

2. 提炼 5 条今日要点（放在蓝色速览卡片）

3. 写一段 100-200 字的编辑精选评论

4. 每条资讯的"阅读原文→"链接用 # 占位

5. 资讯标题要具体、有信息量，不要泛泛而谈

## 样式要求（内联在HTML中）

使用以下CSS变量和样式：

```
:root {{--bg:#f5f7fa;--card-bg:#ffffff;--text-primary:#1a1a2e;--text-secondary:#5a5a7a;--text-muted:#8a8aa0;--accent-blue:#2563eb;--accent-blue-light:#dbeafe;--accent-purple:#7c3aed;--accent-purple-light:#ede9fe;--accent-teal:#0d9488;--accent-teal-light:#ccfbf1;--accent-orange:#ea580c;--accent-orange-light:#ffedd5;--accent-green:#16a34a;--accent-green-light:#dcfce7;--border:#e2e8f0;--border-light:#f1f5f9;--radius:12px;--radius-sm:8px;--shadow:0 1px 3px rgba(0,0,0,0.04),0 4px 12px rgba(0,0,0,0.03);}}
```

关键样式类：
- `.container` max-width:720px; margin:0 auto; padding:24px 16px 48px;
- `.header` text-align:center; `.header-title` font-size:22px; font-weight:700;
- `.header-date` 蓝色圆角标签 (display:inline-block; padding:4px 16px; background:var(--accent-blue-light); color:var(--accent-blue); border-radius:20px;)
- `.intro` 白色卡片，导语
- `.quick-tips` 蓝紫渐变背景 (linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%))，白色文字，5个要点
- `.section` 分类板块，`.section-header` 带图标和标题，`.section-count` 条目数标签
- `.card` 白色卡片，`.card-badge` 标签，`.card-title` 标题，`.card-summary` 摘要，`.card-footer` 标签+链接
- `.editor-pick` 白色卡片，橙色左边框 (border-left:3px solid var(--accent-orange))，深度观点
- `.footer` 页脚居中

颜色类：badge-blue/badge-purple/badge-teal/badge-orange, icon-blue/icon-purple/icon-teal/icon-orange

## HTML 结构要求

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>三木AI 每日一刻钟 | {today_str}</title>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>...所有CSS...</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1 class="header-title">三木AI 每日一刻钟</h1>
      <p class="header-sub">每天15分钟，读懂AI世界</p>
      <span class="header-date">{today_display}</span>
    </div>
    
    <div class="intro">
      <p class="intro-text">...今日概览...</p>
    </div>
    
    <div class="quick-tips">
      <div class="quick-tips-title">今日要点速览</div>
      <ul class="quick-tips-list">
        <li>要点1</li>
        ...
      </ul>
    </div>
    
    <!-- 四个 section，每个 section 包含多个 card -->
    
    <div class="editor-pick">
      <div class="editor-pick-title">编辑精选 / 深度观点</div>
      <div class="editor-pick-content">...深度评论...</div>
    </div>
    
    <div class="footer">
      <p class="footer-text"><span class="footer-brand">三木AI 每日一刻钟</span> · 每天15分钟，读懂AI世界</p>
      <p class="footer-text">{today_display} · 共收录资讯XX条</p>
    </div>
  </div>
</body>
</html>
```

## 输出格式

只输出完整的 HTML 代码。不要添加 markdown 代码块标记（如 ```html），直接输出纯 HTML 文本。
"""
    
    html = call_openrouter(prompt)
    
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

def generate_fallback_html(today_str, today_display):
    """生成备用 HTML（当 API 不可用时）"""
    log('生成备用 HTML...')
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>三木AI 每日一刻钟 | {today_str}</title>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{--bg:#f5f7fa;--card-bg:#ffffff;--text-primary:#1a1a2e;--text-secondary:#5a5a7a;--text-muted:#8a8aa0;--accent-blue:#2563eb;--accent-blue-light:#dbeafe;--accent-purple:#7c3aed;--accent-purple-light:#ede9fe;--accent-teal:#0d9488;--accent-teal-light:#ccfbf1;--accent-orange:#ea580c;--accent-orange-light:#ffedd5;--accent-green:#16a34a;--accent-green-light:#dcfce7;--border:#e2e8f0;--border-light:#f1f5f9;--radius:12px;--radius-sm:8px;--shadow:0 1px 3px rgba(0,0,0,0.04),0 4px 12px rgba(0,0,0,0.03);}}
    * {{margin:0;padding:0;box-sizing:border-box;}}
    body {{font-family:'Noto Sans SC',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--text-primary);line-height:1.7;}}
    .container {{max-width:720px;margin:0 auto;padding:24px 16px 48px;}}
    .header {{text-align:center;margin-bottom:28px;}}
    .header-title {{font-size:22px;font-weight:700;color:var(--text-primary);letter-spacing:1px;}}
    .header-sub {{font-size:13px;color:var(--text-muted);margin-top:4px;}}
    .header-date {{display:inline-block;margin-top:12px;padding:4px 16px;background:var(--accent-blue-light);color:var(--accent-blue);border-radius:20px;font-size:13px;font-weight:500;}}
    .intro {{background:var(--card-bg);border-radius:var(--radius);padding:20px 24px;margin-bottom:24px;box-shadow:var(--shadow);border:1px solid var(--border);}}
    .intro-text {{font-size:14px;color:var(--text-secondary);line-height:1.8;}}
    .quick-tips {{background:linear-gradient(135deg,#2563eb 0%,#1d4ed8 100%);border-radius:var(--radius);padding:20px 24px;margin-bottom:24px;color:white;box-shadow:var(--shadow);}}
    .quick-tips-title {{font-size:15px;font-weight:600;margin-bottom:12px;}}
    .quick-tips-list {{list-style:none;}}
    .quick-tips-list li {{font-size:13px;line-height:1.9;padding-left:16px;position:relative;opacity:0.95;}}
    .quick-tips-list li::before {{content:'';position:absolute;left:0;top:10px;width:6px;height:6px;background:rgba(255,255,255,0.7);border-radius:50%;}}
    .section {{margin-bottom:24px;}}
    .section-header {{display:flex;align-items:center;gap:10px;margin-bottom:16px;padding-left:4px;}}
    .section-icon {{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;}}
    .section-title {{font-size:15px;font-weight:600;color:var(--text-primary);}}
    .section-count {{margin-left:auto;font-size:12px;color:var(--text-muted);background:var(--border-light);padding:2px 10px;border-radius:12px;}}
    .card {{background:var(--card-bg);border-radius:var(--radius);padding:18px 20px;margin-bottom:12px;box-shadow:var(--shadow);border:1px solid var(--border);}}
    .card-header {{display:flex;align-items:flex-start;gap:10px;margin-bottom:8px;}}
    .card-badge {{flex-shrink:0;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:500;}}
    .card-title {{font-size:14px;font-weight:600;color:var(--text-primary);line-height:1.5;flex:1;}}
    .card-summary {{font-size:13px;color:var(--text-secondary);line-height:1.7;margin-bottom:10px;}}
    .card-footer {{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}}
    .card-tag {{font-size:11px;color:var(--text-muted);background:var(--border-light);padding:2px 8px;border-radius:4px;}}
    .card-link {{font-size:12px;color:var(--accent-blue);text-decoration:none;margin-left:auto;}}
    .badge-blue {{background:var(--accent-blue-light);color:var(--accent-blue);}}
    .badge-purple {{background:var(--accent-purple-light);color:var(--accent-purple);}}
    .badge-teal {{background:var(--accent-teal-light);color:var(--accent-teal);}}
    .badge-orange {{background:var(--accent-orange-light);color:var(--accent-orange);}}
    .icon-blue {{background:var(--accent-blue-light);color:var(--accent-blue);}}
    .icon-purple {{background:var(--accent-purple-light);color:var(--accent-purple);}}
    .icon-teal {{background:var(--accent-teal-light);color:var(--accent-teal);}}
    .icon-orange {{background:var(--accent-orange-light);color:var(--accent-orange);}}
    .editor-pick {{background:var(--card-bg);border-radius:var(--radius);padding:20px 24px;box-shadow:var(--shadow);border:1px solid var(--border);border-left:3px solid var(--accent-orange);}}
    .editor-pick-title {{font-size:15px;font-weight:600;color:var(--text-primary);margin-bottom:12px;}}
    .editor-pick-content {{font-size:13px;color:var(--text-secondary);line-height:1.8;}}
    .editor-pick-content p {{margin-bottom:8px;}}
    .editor-pick-content strong {{color:var(--text-primary);font-weight:600;}}
    .footer {{text-align:center;margin-top:32px;padding-top:24px;border-top:1px solid var(--border);}}
    .footer-text {{font-size:12px;color:var(--text-muted);}}
    .footer-brand {{font-weight:600;color:var(--text-secondary);}}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1 class="header-title">三木AI 每日一刻钟</h1>
      <p class="header-sub">每天15分钟，读懂AI世界</p>
      <span class="header-date">{today_display}</span>
    </div>
    
    <div class="intro">
      <p class="intro-text">今日简报内容正在整理中，请稍后再试。</p>
    </div>
    
    <div class="footer">
      <p class="footer-text"><span class="footer-brand">三木AI 每日一刻钟</span> · 每天15分钟，读懂AI世界</p>
      <p class="footer-text">{today_display}</p>
    </div>
  </div>
</body>
</html>"""

def update_github_files(html_content, today_str):
    """通过 GitHub API 更新文件"""
    if not GITHUB_TOKEN:
        log('❌ 未设置 GITHUB_TOKEN')
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
        log(f'获取 {daily_filename} SHA 失败: {e}')
    
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
            log(f'✅ {daily_filename} 上传成功')
            success_count += 1
        else:
            log(f'❌ {daily_filename} 上传失败: {resp.status_code} {resp.text[:200]}')
    except Exception as e:
        log(f'❌ {daily_filename} 上传异常: {e}')
    
    # 2. 更新 index.html
    index_sha = ''
    try:
        check_resp = requests.get(f'https://api.github.com/repos/{REPO_NAME}/contents/index.html', headers=headers, timeout=15)
        if check_resp.status_code == 200:
            index_sha = check_resp.json().get('sha', '')
    except Exception as e:
        log(f'获取 index.html SHA 失败: {e}')
    
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
            log(f'✅ index.html 更新成功')
            success_count += 1
        else:
            log(f'❌ index.html 更新失败: {resp.status_code} {resp.text[:200]}')
    except Exception as e:
        log(f'❌ index.html 更新异常: {e}')
    
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
        log(f'获取 manifest.json 失败: {e}')
    
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
            log(f'✅ manifest.json 更新成功')
            success_count += 1
        else:
            log(f'❌ manifest.json 更新失败: {resp.status_code} {resp.text[:200]}')
    except Exception as e:
        log(f'❌ manifest.json 更新异常: {e}')
    
    return success_count >= 2

def main():
    log(f'=== 三木AI 每日一刻钟 自动生成 ===')
    log(f'日期: {TODAY_DISPLAY}')
    log(f'API Key: {"已设置" if OPENROUTER_API_KEY else "未设置"}')
    log(f'GitHub Token: {"已设置" if GITHUB_TOKEN else "未设置"}')
    
    # 尝试使用 AI 生成
    html_content = None
    
    if OPENROUTER_API_KEY:
        log('尝试调用 OpenRouter API 生成简报...')
        html_content = generate_html_with_ai(TODAY_STR, TODAY_DISPLAY)
    else:
        log('未设置 API Key，跳过 AI 生成')
    
    # 如果 AI 生成失败，使用备用模板
    if not html_content:
        log('AI 生成失败，使用备用模板')
        html_content = generate_fallback_html(TODAY_STR, TODAY_DISPLAY)
    
    # 验证 HTML
    if '<!DOCTYPE html>' not in html_content or '</html>' not in html_content:
        log('⚠️ HTML 结构不完整，使用备用模板')
        html_content = generate_fallback_html(TODAY_STR, TODAY_DISPLAY)
    
    log(f'HTML 长度: {len(html_content)} 字符')
    
    # 保存到本地
    output_file = f'ai-daily-{TODAY_STR}.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    log(f'✅ 本地备份已保存: {output_file}')
    
    # 推送到 GitHub
    log('推送到 GitHub...')
    success = update_github_files(html_content, TODAY_STR)
    
    if success:
        log('🎉 全部完成！网站已更新：https://ai.18kr.cn/')
    else:
        log('⚠️ 推送到 GitHub 部分失败')
    
    # 即使部分失败也不退出错误码，确保 GitHub Actions 不会标记为失败
    log('脚本执行完毕')

if __name__ == '__main__':
    main()
