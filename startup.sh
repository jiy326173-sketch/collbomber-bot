#!/bin/bash
# Start cron daemon if not running, then run keep_alive
pgrep -a cron >/dev/null 2>&1 || service cron start 2>/dev/null
cd /root/workspace && bash keep_alive.shnohup bash /root/workspace/monitor.sh > /dev/null 2>&1 &
