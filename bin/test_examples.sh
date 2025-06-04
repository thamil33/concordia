#!/bin/bash

# Test the examples.
set -euxo pipefail
cd "$(dirname "$0")/.."
FAILURES=false

echo "pytest examples..."
pytest examples || FAILURES=true
echo
echo

echo "pytype examples..."
pytype examples || FAILURES=true
echo
echo

echo "pylint examples..."
pylint --errors-only examples || FAILURES=true
echo
echo

echo "convert notebooks..."
./bin/convert_notebooks.sh notebooks
echo
echo

echo "pytype notebooks..."
pytype --pythonpath=. notebooks || FAILURES=true
echo
echo

echo "pylint notebooks..."
pylint --errors-only notebooks || FAILURES=true
echo
echo

if "${FAILURES}"; then
  echo -e '\033[0;31mFAILURE\033[0m' && exit 1
else
  echo -e '\033[0;32mSUCCESS\033[0m'
fi
