#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Send daily AI briefing email - 2026-09-01"""

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

SUBJECT = "「三木AI 每日一刻钟」2026年09月01日 完整简报"

BODY = """你好！

「三木AI 每日一刻钟」2026年09月01日 简报已自动生成并发布。

今日核心要点（13条真实资讯）：

1. OpenAI广告业务年化收入突破10亿美元：推出仅200天，覆盖40多国，9月1日起向印度、欧洲、中东和北非开放自助投放
2. OpenClaw 2.0发布：933贡献者、1.6万PR史上最大更新，重构Active Memory与多Agent协作，支持Shared Cloud Sessions
3. DeepSeek开源V4-Flash-Vision-Exp多模态模型：DeepSWE 59.3%反超Opus-4.8登顶真实软件工程评测
4. 英伟达35亿美元入股联发科：联发科XPU接入NVLink Fusion+NVHBM，AI芯片生态再扩张
5. OpenAI采购数万台Mac mini和Mac Studio做强化学习：训练可自主操作电脑的Computer-Use Agent
6. 欧盟将ChatGPT列入VLOSE：数字服务法最严格平台规则，首批适用AI服务
7. 智谱开源GLM-5.3权重：国产模型周调用量占全球约68%，连续19周居首
8. 阿里巴巴配售800亿港元新股：全额投入全栈AI建设，2019港股上市以来首次新股配售
9. DeepSeek拟50亿美元融资估值740亿美元：瞄准2027年上海科创板IPO
10. Waymo融资160亿美元估值1260亿美元：滴滴自动驾驶R2开启无人载客测试
11. 工信部启动AI应用服务商培育专项行动：探索首购首用、风险补偿模式加大大模型/智能体/Token采购
12. 国家数据局：日均词元调用量突破500万亿，两年增长超5000倍
13. 全球首个太空算力云常态化运行：北邮牵头，大模型推理能效比达10Token/J

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
