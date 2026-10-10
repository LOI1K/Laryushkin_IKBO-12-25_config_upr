#!/bin/bash

cd "$(dirname "$0")/.."

./run.sh \
    --vfs vfs_examples/minimal \
    --script scripts/stage3.txt