#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="$REPO_ROOT/data/evaluations"
PROJECTS_ROOT="/home/belal/projects"
MAX_PARALLEL=3

# ── JSON tooling ──────────────────────────────────────────────
JSON_TOOL=""
if command -v jq &>/dev/null; then
    JSON_TOOL="jq"
else
    JSON_TOOL="python3"
fi

json_get() {
    local file="$1"
    local key="$2"
    # Strip leading dot for python path
    local pykey="${key#.}"
    if [ "$JSON_TOOL" = "jq" ]; then
        jq -r "$key // \"null\"" "$file" 2>/dev/null || echo "null"
    else
        python3 -c "
import sys, json
try:
    d = json.load(open('$file'))
    keys = '$pykey'.split('.')
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            d = None
            break
    print(d if d is not None else 'null')
except Exception:
    print('null')
" 2>/dev/null || echo "null"
    fi
}

# ── Colors ────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ── Help ──────────────────────────────────────────────────────
usage() {
    cat <<EOF
Autonomous Harness Evaluation Runner

Usage: $(basename "$0") [OPTIONS]

Options:
  --compare              Print a colorized table comparison of scores
  --alert-below N        Exit non-zero and list projects below N%% score
  --help                 Show this help message

Behavior:
  Scans all project directories under $PROJECTS_ROOT,
  runs 'harness scan . --json --ci --threshold 50' for each,
  stores results in $DATA_DIR/{slug}/{timestamp}.json,
  and updates $DATA_DIR/index.json.

Parallelism: max $MAX_PARALLEL projects at a time.
EOF
}

# ── Parse flags ───────────────────────────────────────────────
MODE="scan"
ALERT_THRESHOLD=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --compare)
            MODE="compare"
            shift
            ;;
        --alert-below)
            MODE="alert"
            ALERT_THRESHOLD="$2"
            shift 2
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

# ── Ensure data dir ───────────────────────────────────────────
mkdir -p "$DATA_DIR"

# ── Compare mode ──────────────────────────────────────────────
if [ "$MODE" = "compare" ]; then
    if [ ! -f "$DATA_DIR/index.json" ]; then
        echo "No index.json found. Run a scan first." >&2
        exit 1
    fi

    printf "${BLUE}%-30s %10s %10s %10s %10s${NC}\n" "PROJECT" "LATEST" "PREV" "DELTA" "STATUS"
    printf '%0.s─' $(seq 1 80); echo

    if [ "$JSON_TOOL" = "jq" ]; then
        jq -r '.projects // {} | to_entries[] | "\(.key)|\(.value.latest_score // \"N/A\")|\(.value.previous_score // \"N/A\")|\(.value.delta // \"N/A\")|\(.value.status)"' "$DATA_DIR/index.json" 2>/dev/null | while IFS='|' read -r name latest prev delta status; do
            if [ "$status" = "error" ]; then
                printf "${RED}%-30s %10s %10s %10s %10s${NC}\n" "$name" "$latest" "$prev" "$delta" "$status"
            else
                printf "%-30s %10s %10s %10s %10s\n" "$name" "$latest" "$prev" "$delta" "$status"
            fi
        done
    else
        python3 -c "
import json, sys

try:
    with open('$DATA_DIR/index.json') as f:
        idx = json.load(f)
except Exception:
    sys.exit(1)

projects = idx.get('projects', {})
for name, info in sorted(projects.items()):
    latest = info.get('latest_score', 'N/A')
    prev = info.get('previous_score', 'N/A')
    delta = info.get('delta', 'N/A')
    status = info.get('status', 'unknown')
    latest_s = str(latest) if latest is not None else 'N/A'
    prev_s = str(prev) if prev is not None else 'N/A'
    delta_s = str(delta) if delta is not None else 'N/A'
    color_red = '\033[0;31m'
    color_nc = '\033[0m'
    if status == 'error':
        print(f'{color_red}{name:30} {latest_s:>10} {prev_s:>10} {delta_s:>10} {status:>10}{color_nc}')
    else:
        print(f'{name:30} {latest_s:>10} {prev_s:>10} {delta_s:>10} {status:>10}')
"
    fi
    exit 0
fi

# ── Alert mode ────────────────────────────────────────────────
if [ "$MODE" = "alert" ]; then
    if [ ! -f "$DATA_DIR/index.json" ]; then
        echo "No index.json found. Run a scan first." >&2
        exit 1
    fi
    if ! [[ "$ALERT_THRESHOLD" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        echo "Invalid threshold: $ALERT_THRESHOLD" >&2
        exit 1
    fi

    alerts=()
    if [ "$JSON_TOOL" = "jq" ]; then
        while IFS= read -r line; do
            name="${line%%|*}"
            score="${line#*|}"
            if [ "$score" != "null" ] && (( $(echo "$score < $ALERT_THRESHOLD" | bc -l) )); then
                alerts+=("$name ($score)")
            fi
        done < <(jq -r '.projects // {} | to_entries[] | select(.value.latest_score != null) | "\(.key)|\(.value.latest_score)"' "$DATA_DIR/index.json" 2>/dev/null)
    else
        while IFS= read -r line; do
            name="${line%%|*}"
            score="${line#*|}"
            if [ "$score" != "null" ] && [ "$score" != "N/A" ] && python3 -c "import sys; sys.exit(0 if float('$score') < float('$ALERT_THRESHOLD') else 1)" 2>/dev/null; then
                alerts+=("$name ($score)")
            fi
        done < <(python3 -c "
import json
with open('$DATA_DIR/index.json') as f:
    idx = json.load(f)
for name, info in idx.get('projects', {}).items():
    s = info.get('latest_score')
    if s is not None:
        print(f'{name}|{s}')
" 2>/dev/null)
    fi

    if [ ${#alerts[@]} -gt 0 ]; then
        echo "ALERT: Projects below ${ALERT_THRESHOLD}%:"
        for a in "${alerts[@]}"; do
            echo "  - $a"
        done
        exit 1
    else
        echo "All projects meet the ${ALERT_THRESHOLD}% threshold."
        exit 0
    fi
fi

# ── Scan mode ─────────────────────────────────────────────────
echo "🔍 Starting autonomous evaluation scan..."
echo "   Projects root: $PROJECTS_ROOT"
echo "   Data dir:      $DATA_DIR"
echo ""

# Timestamp for this run
TIMESTAMP=$(date +"%Y-%m-%dT%H-%M-%S")
ISO_NOW=$(date -Iseconds)

# Temporary directory for parallel result tracking
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# Collect project directories
PROJECTS=()
for dir in "$PROJECTS_ROOT"/*/; do
    [ -d "$dir" ] || continue
    name=$(basename "$dir")
    PROJECTS+=("$name")
done

if [ ${#PROJECTS[@]} -eq 0 ]; then
    echo "No projects found in $PROJECTS_ROOT" >&2
    exit 1
fi

echo "Found ${#PROJECTS[@]} projects: ${PROJECTS[*]}"
echo ""

# Load existing index for delta calculation
PREV_INDEX="$TMPDIR/prev_index.json"
if [ -f "$DATA_DIR/index.json" ]; then
    cp "$DATA_DIR/index.json" "$PREV_INDEX"
else
    echo '{"projects":{}}' > "$PREV_INDEX"
fi

# Worker function
scan_one() {
    local project_name="$1"
    local project_path="$PROJECTS_ROOT/$project_name"
    local slug="$project_name"
    local outdir="$DATA_DIR/$slug"
    local outfile="$outdir/${TIMESTAMP}.json"
    local tmpout="$TMPDIR/${slug}.json"
    local tmperr="$TMPDIR/${slug}.err"
    local statusfile="$TMPDIR/${slug}.status"

    mkdir -p "$outdir"

    if (cd "$project_path" && harness scan . --json --ci --threshold 50 > "$tmpout" 2> "$tmperr"); then
        mv "$tmpout" "$outfile"
        rm -f "$tmperr"
        local score
        score=$(json_get "$outfile" ".overall.score")
        printf '%s\t%s\t%s\t%s\n' "$project_name" "$outfile" "$score" "ok" > "$statusfile"
    else
        if [ -s "$tmpout" ]; then
            mv "$tmpout" "$outfile"
        else
            echo '{"overall":{"score":null}}' > "$outfile"
        fi
        local err_msg
        err_msg=$(cat "$tmperr" 2>/dev/null || echo "harness scan failed")
        rm -f "$tmperr"
        local score
        score=$(json_get "$outfile" ".overall.score")
        printf '%s\t%s\t%s\t%s\t%s\n' "$project_name" "$outfile" "$score" "error" "$err_msg" > "$statusfile"
    fi
}

# Run scans with max parallelism
running=0
for pname in "${PROJECTS[@]}"; do
    scan_one "$pname" &
    ((running++))
    if [ "$running" -ge "$MAX_PARALLEL" ]; then
        wait -n || true
        ((running--))
    fi
done
while [ "$running" -gt 0 ]; do
    wait -n || true
    ((running--))
done

# ── Build index.json ──────────────────────────────────────────
echo ""
echo "📊 Building index.json..."

if [ "$JSON_TOOL" = "jq" ]; then
    NEW_INDEX="$TMPDIR/new_index.json"
    echo '{"projects":{}}' > "$NEW_INDEX"

    for statusfile in "$TMPDIR"/*.status; do
        [ -f "$statusfile" ] || continue
        IFS=$'\t' read -r -a fields < "$statusfile"
        name="${fields[0]}"
        file="${fields[1]}"
        score="${fields[2]}"
        status="${fields[3]}"
        err_msg=""
        if [ "$status" = "error" ]; then
            err_msg="${fields[4]}"
        fi

        prev_score=$(jq -r ".projects.\"$name\".latest_score // \"null\"" "$PREV_INDEX" 2>/dev/null || echo "null")

        delta="null"
        if [ "$score" != "null" ] && [ "$prev_score" != "null" ]; then
            delta=$(python3 -c "print(round(float('$score') - float('$prev_score'), 2))" 2>/dev/null || echo "null")
        fi

        entry=$(jq -n \
            --arg path "$PROJECTS_ROOT/$name" \
            --argjson score "${score:-null}" \
            --arg file "${TIMESTAMP}.json" \
            --argjson prev "${prev_score:-null}" \
            --argjson delta "${delta:-null}" \
            --arg status "$status" \
            --arg err "${err_msg:-null}" \
            '{path: $path, latest_score: $score, latest_file: $file, previous_score: $prev, delta: $delta, status: $status, error_msg: (if $err == "null" then null else $err end)}')

        jq --arg name "$name" --argjson entry "$entry" '.projects[$name] = $entry' "$NEW_INDEX" > "$TMPDIR/tmp_idx.json" && mv "$TMPDIR/tmp_idx.json" "$NEW_INDEX"
    done

    jq --arg last "$ISO_NOW" '{last_updated: $last, projects: .projects}' "$NEW_INDEX" > "$DATA_DIR/index.json"
else
    python3 -c "
import json, os, glob

prev = {'projects': {}}
try:
    with open('$PREV_INDEX') as f:
        prev = json.load(f)
except Exception:
    pass

index = {'last_updated': '$ISO_NOW', 'projects': {}}

for sf in glob.glob('$TMPDIR/*.status'):
    with open(sf) as f:
        parts = f.read().rstrip('\n').split('\t')
    name = parts[0]
    file_path = parts[1]
    score_str = parts[2]
    status = parts[3]
    err_msg = parts[4] if len(parts) > 4 else None

    score = float(score_str) if score_str not in ('null', 'None', '') else None
    prev_score = prev.get('projects', {}).get(name, {}).get('latest_score')

    delta = None
    if score is not None and prev_score is not None:
        try:
            delta = round(score - prev_score, 2)
        except Exception:
            pass

    index['projects'][name] = {
        'path': os.path.join('$PROJECTS_ROOT', name),
        'latest_score': score,
        'latest_file': '${TIMESTAMP}.json',
        'previous_score': prev_score,
        'delta': delta,
        'status': status,
        'error_msg': err_msg
    }

with open('$DATA_DIR/index.json', 'w') as f:
    json.dump(index, f, indent=2)
"
fi

echo "✅ Scan complete. Results stored in $DATA_DIR"
echo ""

# Print summary table
printf "${BLUE}%-30s %10s %10s %10s %10s${NC}\n" "PROJECT" "LATEST" "PREV" "DELTA" "STATUS"
printf '%0.s─' $(seq 1 80); echo

if [ "$JSON_TOOL" = "jq" ]; then
    jq -r '.projects | to_entries[] | "\(.key)|\(.value.latest_score // \"N/A\")|\(.value.previous_score // \"N/A\")|\(.value.delta // \"N/A\")|\(.value.status)"' "$DATA_DIR/index.json" | while IFS='|' read -r name latest prev delta status; do
        if [ "$status" = "error" ]; then
            printf "${RED}%-30s %10s %10s %10s %10s${NC}\n" "$name" "$latest" "$prev" "$delta" "$status"
        else
            printf "%-30s %10s %10s %10s %10s\n" "$name" "$latest" "$prev" "$delta" "$status"
        fi
    done
else
    python3 -c "
import json
with open('$DATA_DIR/index.json') as f:
    idx = json.load(f)
for name, info in sorted(idx.get('projects', {}).items()):
    latest = info.get('latest_score', 'N/A')
    prev = info.get('previous_score', 'N/A')
    delta = info.get('delta', 'N/A')
    status = info.get('status', 'unknown')
    latest_s = str(latest) if latest is not None else 'N/A'
    prev_s = str(prev) if prev is not None else 'N/A'
    delta_s = str(delta) if delta is not None else 'N/A'
    red = '\033[0;31m'
    nc = '\033[0m'
    if status == 'error':
        print(f'{red}{name:30} {latest_s:>10} {prev_s:>10} {delta_s:>10} {status:>10}{nc}')
    else:
        print(f'{name:30} {latest_s:>10} {prev_s:>10} {delta_s:>10} {status:>10}')
"
fi

echo ""
