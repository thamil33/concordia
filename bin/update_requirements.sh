#!/bin/bash
#
 
#
# Update requirements.txt.
set -euxo pipefail
cd "$(dirname "$0")/.."

pip-compile --generate-hashes --reuse-hashes --strip-extras  --allow-unsafe \
     --upgrade --extra dev setup.py examples/requirements.in
