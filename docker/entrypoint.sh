#!/bin/sh

# This script is required to overcome issues with cron loading in environmental variables.
printenv > /etc/environment
cron && tail -f /var/log/cron.log