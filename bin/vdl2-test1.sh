#!/usr/bin/env bash
#
# Title: vdl2-test1.sh
# Description: original dumpvdl2 test
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
/usr/local/bin/dumpvdl2 --rtlsdr 0 --gain 40 --correction 0 --utc --station-id WOMBAT-SFO-VDL2 --output 'decoded:json:file:path=/tmp/vdl2.json,rotate=hourly' 136100000 136300000 136600000 136650000 136700000 136800000 136975000
#