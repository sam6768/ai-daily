#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Send daily AI briefing email - 2026-08-30"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.header import Header

# QQ Mail SMTP config
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SENDER_EMAIL = "xinmu8@qq.com"
SMTP_PASSWORD = "kdqpkbunsnfhbgfj"
RECEIVER_EMAIL = "908863436@qq.com"

SUBJECT = "「三木AI 每日一刻钟」2026年08月30日 完整简报"

BODY = """你好！

「三木AI 每日一刻钟」2026年08月30日 简报已自动生成并发布。

今日核心要点（13条真实资讯）：

1. DeepSeek推进74亿美元新一轮融资：投前估值740亿美元，拟2027年IPO，前七月营收已破4.75亿元
2. 谷歌DeepMind Co-Scientist接入真实CVD设备：83页论文展示Gemini自主设计实验并成功生长MoS₂等二维半导体
3. 中国首部《人工智能训练数据合规使用指引》正式发布：国家网信办等五部门明确标注、授权、溯源三大底线
4. 美团训练大型AI模型完全使用国产芯片：自主可控里程碑，标志中美AI算力生态走向二元分叉
5. 长鑫存储LPDDR6内存正式量产：小米玄戒O3首发支持，中国高端存储标准从0到1突破
6. 黄仁勋宣布英伟达"已实现AGI"：Vera Rubin平台首测对DeepSeek吞吐量提升30倍
7. OpenAI官宣终止向Cursor提供模型：AI编程工具迎生态变局，11月12日过渡期结束
8. 全球首例AI实时辅助脑外科手术在伦敦完成：UCL团队让AI从"术前参谋"迈向"术中帮手"
9. 月之暗面Kimi冲刺港股IPO：估值冲击500亿美元，开源旗舰首次在主流基准超越闭源
10. 沐曦股份曦云C系列GPU完成腾讯混元Hy4 preview Day 0适配：国产算力生态重大突破
11. 大晓机器人联合港大发布StreamPI：为VLA模型加入时间维度，推动具身智能进入连续物理智能
12. 上海"十五五"规划构建"芯-模-云"生态：北京亦庄首发全国首个AI4Chip专项政策
13. 合肥"词元世界"平台正式上线：一站式聚合200余款主流大模型，工信部已研制近200项AI关键标准

分类统计：技术前沿 3条 / 国内外AI动态 4条 / 投资与商业 3条 / 政策与行业生态 3条

访问完整简报：https://ai.18kr.cn/

— 三木AI 每日一刻钟 自动推送
"""

def send_email():
    print("Sending email...")
    print("From: %s" % SENDER_EMAIL)
    print("To: %s" % RECEIVER_EMAIL)
    print("Subject: %s" % SUBJECT)

    msg = MIMEText(BODY, 'plain', 'utf-8')
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = Header(SUBJECT, 'utf-8')

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
