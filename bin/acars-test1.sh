#!/bin/bash
#
# Title: collector.sh
# Description: drive the collection pass
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
hostname=$(hostname)
logger -p local3.info "collector capybara $hostname"
#
WORK_DIR="/home/wombat/github/mellow-capybara-v1/src/collector"
#
echo "start collector"
#
#acarsdec -i c4g -g 42 -p 0 --rtlsdr 0 --output json:file:path=/tmp/acars.json 131.450 131.525 131.550 131.725 131.850
acarsdec -e -i c4g -g 42 -p 0 --output json:file:path=/tmp/acars.json,rotate=hourly --rtlsdr 0 130.025 130.425 130.450 131.125 131.550
#
echo "end collector"
#
