#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Send daily AI briefing email with full HTML content matching webpage style
"""

import smtplib
import ssl
import re
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# QQ Mail SMTP config
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SENDER_EMAIL = "xinmu8@qq.com"
SMTP_PASSWORD = "kdqpkbunsnfhbgfj"
RECEIVER_EMAIL = "908863436@qq.com"

def extract_content_from_html(html_content):
    """Extract body content from index.html for email use"""
    # Extract just the container content (from <div class="container"> to closing </div> before </body>)
    match = re.search(r'(<div class="container">.*?</div>)\s*</body>', html_content, re.DOTALL)
    if match:
        return match.group(1)
    return html_content

def build_email_html(body_content, date_str):
    """Build a full HTML email that matches the webpage style"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>三木AI 每日一刻钟 | {date_str}</title>
  <style>
    body {{ font-family: 'PingFang SC','Microsoft YaHei',-apple-system,BlinkMacSystemFont,sans-serif; background:#f5f7fa; color:#1a1a2e; line-height:1.7; margin:0; padding:0; }}
    .email-wrapper {{ max-width:680px; margin:0 auto; background:#f5f7fa; padding:24px 16px 48px; }}
    .header {{ text-align:center; margin-bottom:28px; }}
    .header-title {{ font-size:22px; font-weight:700; color:#1a1a2e; letter-spacing:1px; margin:0; }}
    .header-sub {{ font-size:13px; color:#8a8aa0; margin-top:4px; }}
    .header-date {{ display:inline-block; margin-top:12px; padding:4px 16px; background:#dbeafe; color:#2563eb; border-radius:20px; font-size:13px; font-weight:500; }}

    .intro {{ background:#ffffff; border-radius:12px; padding:20px 24px; margin-bottom:24px; border:1px solid #e2e8f0; }}
    .intro-text {{ font-size:14px; color:#5a5a7a; line-height:1.8; margin:0; }}

    .quick-tips {{ background:linear-gradient(135deg,#2563eb 0%,#1d4ed8 100%); border-radius:12px; padding:20px 24px; margin-bottom:24px; color:white; }}
    .quick-tips-title {{ font-size:15px; font-weight:600; margin-bottom:12px; }}
    .quick-tips-list {{ list-style:none; margin:0; padding:0; }}
    .quick-tips-list li {{ font-size:13px; line-height:1.9; padding-left:16px; position:relative; opacity:0.95; }}
    .quick-tips-list li::before {{ content:'•'; position:absolute; left:0; top:0; color:rgba(255,255,255,0.7); font-size:16px; }}

    .section {{ margin-bottom:24px; }}
    .section-header {{ display:flex; align-items:center; gap:10px; margin-bottom:16px; padding-left:4px; }}
    .section-icon {{ width:28px; height:28px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:14px; }}
    .section-title {{ font-size:15px; font-weight:600; color:#1a1a2e; }}
    .section-count {{ margin-left:auto; font-size:12px; color:#8a8aa0; background:#f1f5f9; padding:2px 10px; border-radius:12px; }}

    .card {{ background:#ffffff; border-radius:12px; padding:18px 20px; margin-bottom:12px; border:1px solid #e2e8f0; }}
    .card-header {{ display:flex; align-items:flex-start; gap:10px; margin-bottom:8px; }}
    .card-badge {{ flex-shrink:0; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:500; }}
    .card-title {{ font-size:14px; font-weight:600; color:#1a1a2e; line-height:1.5; flex:1; margin:0; }}
    .card-summary {{ font-size:13px; color:#5a5a7a; line-height:1.7; margin-bottom:10px; }}
    .card-footer {{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; }}
    .card-tag {{ font-size:11px; color:#8a8aa0; background:#f1f5f9; padding:2px 8px; border-radius:4px; }}
    .card-link {{ font-size:12px; color:#2563eb; text-decoration:none; margin-left:auto; }}

    .badge-blue {{ background:#dbeafe; color:#2563eb; }}
    .badge-purple {{ background:#ede9fe; color:#7c3aed; }}
    .badge-teal {{ background:#ccfbf1; color:#0d9488; }}
    .badge-orange {{ background:#ffedd5; color:#ea580c; }}
    .badge-green {{ background:#dcfce7; color:#16a34a; }}
    .icon-blue {{ background:#dbeafe; color:#2563eb; }}
    .icon-purple {{ background:#ede9fe; color:#7c3aed; }}
    .icon-teal {{ background:#ccfbf1; color:#0d9488; }}
    .icon-orange {{ background:#ffedd5; color:#ea580c; }}
    .icon-green {{ background:#dcfce7; color:#16a34a; }}

    .editor-pick {{ background:#ffffff; border-radius:12px; padding:20px 24px; border:1px solid #e2e8f0; border-left:3px solid #ea580c; }}
    .editor-pick-title {{ font-size:15px; font-weight:600; color:#1a1a2e; margin-bottom:12px; }}
    .editor-pick-content {{ font-size:13px; color:#5a5a7a; line-height:1.8; }}
    .editor-pick-content p {{ margin-bottom:8px; margin-top:0; }}

    .footer {{ text-align:center; margin-top:32px; padding-top:24px; border-top:1px solid #e2e8f0; }}
    .footer-text {{ font-size:12px; color:#8a8aa0; }}
    .footer-brand {{ font-weight:600; color:#5a5a7a; }}

    .view-online {{ text-align:center; margin-top:20px; padding:14px; background:#ffffff; border-radius:12px; border:1px solid #e2e8f0; }}
    .view-online a {{ color:#2563eb; text-decoration:none; font-size:13px; font-weight:500; }}
  </style>
</head>
<body>
  <div class="email-wrapper">
    {body_content}
    <div class="view-online">
      <a href="https://ai.18kr.cn/">查看网页版（含完整排版和链接）→</a>
    </div>
    <div class="footer">
      <p class="footer-text"><span class="footer-brand">三木AI 每日一刻钟</span> · 每天15分钟，读懂AI世界</p>
      <p class="footer-text">— 三木AI 自动推送</p>
    </div>
  </div>
</body>
</html>'''

def send_email():
    print("Reading webpage content...")

    # Read the HTML file
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("Extracting body content...")
    body_content = extract_content_from_html(html_content)

    # Get date from HTML
    date_match = re.search(r'>(\d{4}年\d{2}月\d{2}日)', html_content)
    if not date_match:
        date_match = re.search(r'(\d{4}年\d{2}月\d{2}日)', html_content)
    date_str = date_match.group(1) if date_match else "今日"
    iso_date = re.search(r'(\d{4}-\d{2}-\d{2})', html_content)
    iso_date_str = iso_date.group(1) if iso_date else ""

    # Build email subject
    subject = f"「三木AI 每日一刻钟」{date_str} 完整简报"

    # Build full HTML email
    email_html = build_email_html(body_content, iso_date_str)

    print("Sending HTML email...")
    print("From: %s" % SENDER_EMAIL)
    print("To: %s" % RECEIVER_EMAIL)
    print("Subject: %s" % subject)

    # Create multipart message (HTML + plain text fallback)
    msg = MIMEMultipart('alternative')
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = Header(subject, 'utf-8')

    # Attach HTML part
    html_part = MIMEText(email_html, 'html', 'utf-8')
    msg.attach(html_part)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            print("Connecting to SMTP server...")
            server.login(SENDER_EMAIL, SMTP_PASSWORD)
            print("Login success, sending...")
            server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
            print("Email sent successfully!")
            return True
    except Exception as e:
        print("Email send failed: %s" % str(e))
        return False

if __name__ == "__main__":
    send_email()
