#!/bin/bash
#
# Title: acars-driver.sh
# Description: start acarsdec
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
OUTPUT="json:file:path=/tmp/acars.json,rotate=hourly"
#
FREQUENCIES="129.125 129.350 130.025 130.450 131.125 131.475 131.550"
#
echo "start collector"
#
#acarsdec -i c4g -g 42 -p 0 --rtlsdr 0 --output json:file:path=/tmp/acars.json 131.450 131.525 131.550 131.725 131.850
#acarsdec -e -i c4g -g 42 -p 0 --output json:file:path=/tmp/acars.json,rotate=hourly --rtlsdr 0 130.025 130.425 130.450 131.125 131.550 131.475
acarsdec -e -i c4g -g 40 -p 0 --output $OUTPUT --rtlsdr 0 -c 130.300 $FREQUENCIES
#
echo "end collector"
#
