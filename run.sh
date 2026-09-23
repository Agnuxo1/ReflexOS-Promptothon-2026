#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}" exec python run_reflexos.py "$@"
