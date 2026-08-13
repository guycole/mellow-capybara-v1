#!/usr/bin/env bash
#
# Title: vdl2-sf01.sh
# Description: vdl2 sf collector script
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
set -euo pipefail

PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH

log() {
    local message="$1"
    logger -p local3.info "collector capybara $(hostname): $message"
    echo "$message"
}

VDL2_BIN="${VDL2_BIN:-$(command -v dumpvdl2 || true)}"

OUTPUT_DIR="${OUTPUT_DIR:-/tmp}"
OUTPUT_FILE="${OUTPUT_FILE:-${OUTPUT_DIR}/vdl2.json}"
OUTPUT="decoded:json:file:path=${OUTPUT_FILE},rotate=hourly"

FREQUENCIES=(136.100 136.300 136.600 136.650 136.700 136.800 136.975)

FREQUENCIES_HZ=()
for freq in "${FREQUENCIES[@]}"; do
    FREQUENCIES_HZ+=("$(awk -v freq="$freq" 'BEGIN { printf "%.0f", freq * 1000000 }')")
done

if [[ -z "${VDL2_BIN}" ]]; then
    echo "dumpvdl2 not found in PATH" >&2
    exit 127
fi

mkdir -p "${OUTPUT_DIR}"

log "start collector"

"${VDL2_BIN}" --rtlsdr 0 --gain 40 --correction 0 --utc --station-id VDL2-SFO1 --output "${OUTPUT}" "${FREQUENCIES_HZ[@]}"

log "end collector"
