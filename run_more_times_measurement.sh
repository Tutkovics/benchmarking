#!/bin/bash
for i in {1..5}
do
    echo "=== Start measurement #$i ==="
    time python3 benchmark.py configs/nginx-long-measurement-config.yaml
    echo "=== End ==="
done