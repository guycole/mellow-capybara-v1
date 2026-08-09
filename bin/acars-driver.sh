#!/usr/bin/env bash
#
# Title: acars-driver.sh
# Description: start acarsdec with a safer, more configurable wrapper
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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORK_DIR="${WORK_DIR:-${REPO_ROOT}/src/collector}"
OUTPUT_DIR="${OUTPUT_DIR:-/tmp}"
OUTPUT_FILE="${OUTPUT_FILE:-${OUTPUT_DIR}/acars.json}"
OUTPUT="json:file:path=${OUTPUT_FILE},rotate=hourly"
ACARSDEC_BIN="${ACARSDEC_BIN:-$(command -v acarsdec || true)}"

DEFAULT_FREQUENCIES=(129.125 129.350 130.025 130.450 131.125 131.475 131.550)
FREQUENCIES=("${@:-${DEFAULT_FREQUENCIES[@]}}")

if [[ -z "${ACARSDEC_BIN}" ]]; then
    echo "acarsdec not found in PATH" >&2
    exit 127
fi

if [[ ! -d "${WORK_DIR}" ]]; then
    echo "work directory not found: ${WORK_DIR}" >&2
    exit 1
fi

mkdir -p "${OUTPUT_DIR}"

log "start collector"

(
    cd "${WORK_DIR}"
    "${ACARSDEC_BIN}" -e -i c4g -g 40 -p 0 --output "${OUTPUT}" --rtlsdr 0 -c 130.300 "${FREQUENCIES[@]}"
)

log "end collector"
