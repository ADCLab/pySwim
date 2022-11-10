#!/bin/bash

# This script is required to overcome issues with cron loading in environmental variables.
printenv > /etc/environment
echo "$CRONSTRING root /usr/local/bin/python3 /rcvr.py >> /var/log/cron.log 2>&1" > /etc/cron.d/rcvr-cron
chmod +x /etc/cron.d/rcvr-cron
cron && tail -f /var/log/cron.log