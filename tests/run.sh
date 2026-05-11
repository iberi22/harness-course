#!/bin/bash
# Run all tests for Harness Course
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🧪 Harness Course Test Runner"
echo "================================"

# 1. Python test suite
echo ""
echo "📋 Running Python test suite..."
python3 "$SCRIPT_DIR/test_suite.py"
PY_EXIT=$?

# 2. Harness scan
echo ""
echo "📊 Running Harness scan..."
python3 "$PROJECT_DIR/scripts/harness_evaluator.py" scan "$PROJECT_DIR" --ci --threshold 50
HARNESS_EXIT=$?

# Summary
echo ""
echo "================================"
echo "Results:"

if [ $PY_EXIT -eq 0 ]; then
    echo "  ✅ Python tests: PASSED"
else
    echo "  ❌ Python tests: FAILED"
fi

if [ $HARNESS_EXIT -eq 0 ]; then
    echo "  ✅ Harness scan: PASSED (≥50%)"
else
    echo "  ❌ Harness scan: FAILED (<50%)"
fi

echo ""
exit $((PY_EXIT | HARNESS_EXIT))
