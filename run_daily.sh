#!/bin/bash
# 贾维斯每日运行脚本
# 设置定时任务: 7:50生成报告, 9:25推送热点, 22:00生成晚报

cd "$(dirname "$0")"

LOG="reports/daily_$(date +%Y%m%d).log"

echo "[$(date)] 开始每日流程" >> $LOG

# 早间报告
echo "[$(date)] 生成早间报告..." >> $LOG
python3 main.py --mode morning >> $LOG 2>&1

# 热点推送 (延迟到9:25)
sleep $((9*60+25*60 - $(date +%s) % $(date +%s) )) 2>/dev/null || true
echo "[$(date)] 生成热点推送..." >> $LOG
python3 main.py --mode hot >> $LOG 2>&1

# 舆情监控 (后台运行)
echo "[$(date)] 启动舆情监控..." >> $LOG
python3 -c "
from src.sentiment_monitor import SentimentMonitor
monitor = SentimentMonitor()
for i in range(30):  # 每10分钟运行一次，共5小时
    monitor.run_once()
    import time
    time.sleep(600)
" >> $LOG 2>&1 &

echo "[$(date)] 每日流程完成" >> $LOG
