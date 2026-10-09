
#!/bin/bash

cd "$(dirname "$0")/.."
printf 'exit\n' | ./run.sh --vfs vfs_examples/minimal
