#!/bin/bash
for i in {1..3} #deadline is comming
do
    echo "=== Start measurement #$i ==="
    time python benchmark.py configs/apache-measurement-config-increment.yaml
    echo "=== End ==="
done