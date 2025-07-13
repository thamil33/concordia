#!/bin/bash
#
 
#
# Test concordia.
set -euxo pipefail
cd "$(dirname "$0")/.."
FAILURES=false

echo "pytest concordia..."
pytest concordia || FAILURES=true
echo
echo

echo "pytype concordia..."
pytype concordia || FAILURES=true
echo
echo

echo "pylint concordia..."
pylint --errors-only concordia || FAILURES=true
echo
echo

if "${FAILURES}"; then
  echo -e '\033[0;31mFAILURE\033[0m' && exit 1
else
  echo -e '\033[0;32mSUCCESS\033[0m'
fi
