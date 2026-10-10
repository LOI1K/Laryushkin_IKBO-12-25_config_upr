#!/bin/bash

cd "$(dirname "$0")/.."

./run.sh \
    --vfs vfs_examples/nested \
    --script scripts/stage3.txt