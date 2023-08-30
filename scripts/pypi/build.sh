#!/usr/bin/env bash

set -ex

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
repo_root="$script_dir/../.."
cd $repo_root

python3 -m venv .pypi-venv
. .pypi-venv/bin/activate
python3 -m pip install build==0.10.0
python3 -m build
