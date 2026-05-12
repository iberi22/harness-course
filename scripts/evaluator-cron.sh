#!/usr/bin/env bash
# evaluator-cron.sh — Register/update/remove the autonomous evaluator cron job
#
# Usage:
#   ./evaluator-cron.sh              # Register daily cron (idempotent)
#   ./evaluator-cron.sh --remove     # Remove cron job
#   ./evaluator-cron.sh --status     # Show current registration status
#   ./evaluator-cron.sh --schedule "0 9 * * *"   # Custom schedule
#
# Makes the script idempotent: running twice never creates duplicates.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DATA_DIR="${REPO_ROOT}/data/evaluations"
JOB_NAME="harness-evaluator-v2"
DEFAULT_SCHEDULE="0 9 * * *"
SCHEDULE="${DEFAULT_SCHEDULE}"
AUTO_EVALUATE="${REPO_ROOT}/scripts/auto-evaluate.sh"
LOG_FILE="${DATA_DIR}/evaluator.log"
INDEX_FILE="${DATA_DIR}/index.json"

# Ensure data directory exists
mkdir -p "${DATA_DIR}"

# Parse arguments
REMOVE=false
STATUS=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --remove)
      REMOVE=true
      shift
      ;;
    --status)
      STATUS=true
      shift
      ;;
    --schedule)
      SCHEDULE="${2:-${DEFAULT_SCHEDULE}}"
      shift 2
      ;;
    --help|-h)
      echo "Usage: $0 [--remove|--status|--schedule \"CRON\"]"
      echo ""
      echo "Options:"
      echo "  (no args)         Register/update daily cron job (default: 9 AM)"
      echo "  --remove          Remove the registered cron job"
      echo "  --status          Show whether the cron job is registered"
      echo "  --schedule CRON   Use a custom cron expression"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

# Build the command string that the cron will run.
# We ensure PATH includes ~/.local/bin where harness CLI is typically installed.
CRON_COMMAND="cd ${REPO_ROOT} && PATH=\${PATH}:/home/belal/.local/bin:${HOME}/.local/bin bash ${AUTO_EVALUATE} --compare --alert-below 50 --output ${INDEX_FILE} >> ${LOG_FILE} 2>&1"

# Marker comment used to identify our cron line (idempotency key)
CRON_MARKER="# harness-evaluator-v2"

# --- Status mode ---
if [[ "${STATUS}" == true ]]; then
  echo "🤖 Autonomous Evaluator Agent — Cron Status"
  echo "======================================="
  echo "Repository: ${REPO_ROOT}"
  echo "Schedule:   ${SCHEDULE}"
  echo "Log file:   ${LOG_FILE}"
  echo "Index file: ${INDEX_FILE}"
  echo ""

  if crontab -l 2>/dev/null | grep -qF "${CRON_MARKER}"; then
    echo "Status:     ✅ Registered"
    echo ""
    echo "Matching crontab lines:"
    crontab -l | grep -nF "${CRON_MARKER}" | sed 's/^/  /'
  else
    echo "Status:     ❌ Not registered"
    echo ""
    echo "Register with: $0"
  fi

  # Also check hermes cron if available
  if command -v hermes &>/dev/null && hermes cron list 2>/dev/null | grep -q "${JOB_NAME}"; then
    echo ""
    echo "Hermes cron entry found:"
    hermes cron list | grep "${JOB_NAME}" | sed 's/^/  /'
  fi
  exit 0
fi

# --- Remove mode ---
if [[ "${REMOVE}" == true ]]; then
  echo "🗑️  Removing cron job for ${JOB_NAME}..."

  # Remove from crontab
  if crontab -l 2>/dev/null | grep -qF "${CRON_MARKER}"; then
    (crontab -l 2>/dev/null | grep -vF "${CRON_MARKER}") | crontab -
    echo "✅ Removed from crontab."
  else
    echo "ℹ️  No crontab entry found."
  fi

  # Remove from hermes cron if available
  if command -v hermes &>/dev/null && hermes cron list 2>/dev/null | grep -q "${JOB_NAME}"; then
    hermes cron remove "${JOB_NAME}" 2>/dev/null || true
    echo "✅ Removed from hermes cron."
  fi

  exit 0
fi

# --- Register / Update mode (idempotent) ---
echo "🤖 Autonomous Evaluator Agent — Cron Registration"
echo "================================================"
echo "Repository: ${REPO_ROOT}"
echo "Schedule:   ${SCHEDULE}"
echo "Log file:   ${LOG_FILE}"
echo "Index file: ${INDEX_FILE}"
echo ""

# Ensure auto-evaluate.sh exists
if [[ ! -f "${AUTO_EVALUATE}" ]]; then
  echo "❌ Error: ${AUTO_EVALUATE} not found." >&2
  echo "   Please create the script before registering the cron job." >&2
  exit 1
fi

# 1) Prefer hermes cron if available
if command -v hermes &>/dev/null; then
  echo "🔧 Hermes CLI detected. Attempting hermes cron registration..."

  # Remove existing hermes cron job with same name to ensure idempotency
  if hermes cron list 2>/dev/null | grep -q "${JOB_NAME}"; then
    hermes cron remove "${JOB_NAME}" 2>/dev/null || true
    echo "   Replaced existing hermes cron job '${JOB_NAME}'."
  fi

  # Create new hermes cron job
  # Note: hermes cron syntax varies by installation; we attempt the most common forms.
  if hermes cron create --name "${JOB_NAME}" --schedule "${SCHEDULE}" --command "${CRON_COMMAND}" &>/dev/null; then
    echo "✅ Registered via hermes cron: ${JOB_NAME}"
    hermes cron list | grep "${JOB_NAME}" | sed 's/^/   /'
    exit 0
  elif hermes cron create --schedule "${SCHEDULE}" --prompt "${CRON_COMMAND}" --name "${JOB_NAME}" &>/dev/null; then
    echo "✅ Registered via hermes cron (alt syntax): ${JOB_NAME}"
    hermes cron list | grep "${JOB_NAME}" | sed 's/^/   /'
    exit 0
  else
    echo "⚠️  hermes cron create failed, falling back to crontab..."
  fi
fi

# 2) Fallback: standard crontab (idempotent)
echo "🔧 Registering via system crontab..."

# Build the full cron line with marker
FULL_CRON_LINE="${SCHEDULE} ${CRON_COMMAND} ${CRON_MARKER}"

# Read existing crontab, filtering out any previous lines with our marker
EXISTING_CRONTAB=$(crontab -l 2>/dev/null | grep -vF "${CRON_MARKER}" || true)

# Append our new line
NEW_CRONTAB="${EXISTING_CRONTAB}
${FULL_CRON_LINE}"

# Install the new crontab
echo "${NEW_CRONTAB}" | crontab -

echo "✅ Cron job registered successfully."
echo ""
echo "Next run schedule: ${SCHEDULE}"
echo "Command: ${CRON_COMMAND}"
echo ""
echo "Check status anytime with: $0 --status"
echo "Remove with:               $0 --remove"
