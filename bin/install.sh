#!/bin/bash
#
 
#
# Install concordia.
set -euxo pipefail
cd "$(dirname "$0")/.."

echo 'Installing requirements...'
pip install --no-deps --require-hashes --requirement requirements.txt
echo
echo

echo 'Installing Concordia...'
pip install --no-deps --no-index --no-build-isolation --editable .
echo
echo

pip list
