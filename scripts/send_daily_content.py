#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Send daily AI briefing email - 2026-08-31"""

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

SUBJECT = "「三木AI 每日一刻钟」2026年08月31日 完整简报"

BODY = """你好！

「三木AI 每日一刻钟」2026年08月31日 简报已自动生成并发布。

今日核心要点（13条真实资讯）：

1. OpenAI新模型Astra内测曝光：代号mozaik-alpha-fdm，零样本生成3D等距地图与交互网页，端到端多智能体编排，预计9月3日正式发布
2. 谷歌发布Gemini Omni 1.1 Flash：视频可延展至40秒，新增首尾帧控制与视频参考输入，360p草稿模式吞吐提升约60%
3. Anthropic发布MHS硬件标准：打通AI与物理设备接口，卡内基梅隆实验提速3倍，QuEra激光重锁从150秒压至6秒
4. OpenAI官宣终止向Cursor供应模型：11月12日过渡期结束，SpaceX收购后底层模型API中立性被竞争关系取代
5. 微软收紧AI成本：员工28天挥霍2.8万美元Token，默认工作负载切换至GPT-5.6 Sol降本
6. 大厂AI变阵竞赛：百度Agent业务升格事业部，阿里字节腾讯密集重组智能体团队
7. 韩国启动"All for AI"计划：生成式AI作为公共事业向全民免费无限量提供，9月开启公测
8. 外资密集调研中国AI产业链：高盛称错配修复或带来超千亿美元增量外资，澜起科技获56家外资调研居首
9. 燧原科技9月2日登陆科创板：拟募资60亿元，国产GPU四小龙齐聚资本市场
10. 长鑫科技LPDDR6全球首发量产：首搭小米18 Fold，国产存储首次在高端内存标准全球首发
11. 金监总局发布AI金融安全开发应用指导意见：系统部署治理架构、数据治理、算力建设与风险管理
12. 中消协敦促AI客服加强信息质量管理：不得以"算法自动生成"简单免责
13. 人民日报：数据要素筑基AI加速落地应用，词元调用量成AI新度量衡，贵阳壹号词元工厂发布

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
