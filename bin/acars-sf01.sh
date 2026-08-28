#!/usr/bin/env bash
#
# Title: acars-sf01.sh
# Description: acarsdec for SFO
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
set -euo pipefail

PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH

log() {
    local message="$1"
    logger -p local3.info "collector acars-sf01 $(hostname): $message"
    echo "$message"
}

ACARSDEC_BIN="${ACARSDEC_BIN:-$(command -v acarsdec || true)}"

OUTPUT_DIR="${OUTPUT_DIR:-/tmp}"
OUTPUT_FILE="${OUTPUT_FILE:-${OUTPUT_DIR}/acars.json}"
OUTPUT="json:file:path=${OUTPUT_FILE},rotate=hourly"

FREQUENCIES=(129.125 129.350 130.025 130.450 131.125 131.475 131.550)

min_freq=$(printf '%s' "${FREQUENCIES[@]}" | sort -n | head -n1)
max_freq=$(printf '%s' "${FREQUENCIES[@]}" | sort -n | tail -n1)
CENTER_FREQUENCY=$(awk -v min="$min_freq" -v max="$max_freq" 'BEGIN { print (min + max) / 2.0 }')

if [[ -z "${ACARSDEC_BIN}" ]]; then
    echo "acarsdec not found in PATH" >&2
    exit 127
fi

mkdir -p "${OUTPUT_DIR}"

log "start collector"

"${ACARSDEC_BIN}" -e -i c4g -g 40 -p 0 --output "${OUTPUT}" --rtlsdr 0 -c "${CENTER_FREQUENCY}" "${FREQUENCIES[@]}"

log "end collector"
