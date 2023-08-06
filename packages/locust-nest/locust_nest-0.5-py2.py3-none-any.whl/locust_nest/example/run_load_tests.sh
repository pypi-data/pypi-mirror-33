#!/bin/bash

# Ensure the script always runs from the same location
script_path=$(dirname "$0")
cd "$script_path"

# Run locust-nest
locust-nest --model-dir=./ --print-stats --only-summary --no-web --csv-base-name=load_test --run-time=30s --clients=1 --hatch-rate=1
