
#!/bin/bash

cd "$(dirname "$0")/.."
printf 'exit\n' | ./run.sh --script scripts/demo.txt
