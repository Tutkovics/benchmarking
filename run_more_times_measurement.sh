#!/bin/bash
for i in {1..5} #deadline is comming
do
    echo "=== Start measurement #$i ==="
    time python3 benchmark.py configs/nginx-long-measurement-config-bugfix.yaml
    echo "=== End ==="
done