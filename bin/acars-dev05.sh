#!/usr/bin/env bash
#
# Title: acars-dev05.sh
# Description: acarsdec search group 5
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

ACARSDEC_BIN="${ACARSDEC_BIN:-$(command -v acarsdec || true)}"

OUTPUT_DIR="${OUTPUT_DIR:-/tmp}"
OUTPUT_FILE="${OUTPUT_FILE:-${OUTPUT_DIR}/acars.json}"
OUTPUT="json:file:path=${OUTPUT_FILE},rotate=hourly"

FREQUENCIES=(129.800 129.825 129.850 129.875 129.900 129.925 129.950 129.975)

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
