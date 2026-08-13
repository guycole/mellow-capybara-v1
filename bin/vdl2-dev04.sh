#!/usr/bin/env bash
#
# Title: vdl2-dev04.sh
# Description: vdl2 search group 4
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

FREQUENCIES=(136.775 136.800 136.825 136.850 136.875 136.900 136.925 136.950 136.975 137.000)

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

"${VDL2_BIN}" --rtlsdr 0 --gain 40 --correction 0 --utc --station-id VDL2-DEV04 --output "${OUTPUT}" "${FREQUENCIES_HZ[@]}"

log "end collector"
