# Load Test Guide

## Setup

1. Create load test models for this application in this directory, see [Locust docs](https://docs.locust.io/en/stable/) for help. Create different TaskSets/Locusts to encapsulate different types of users of the system.
2. Run `locust-nest --configure` in this directory.
3. Launch the system under test and find its host e.g. http://localhost:8089
4. Run `locust-nest [options]`

For example: 
```bash
locust-nest --model_dir=./ --print-stats --only-summary --no-web --csv-base-name=`date +%Y-%m-%d.%H:%M:%S` --run-time=30s --clients=1 --hatch-rate=1`
```

Save the options used e.g. as a bash script in this directory, so that future tests use the same basis.

## Continuation

1. Each time there is an update to this codebase, add a load test to reflect this change (if appropriate).
2. Run `locust-nest` in this directory with the same options as before, ensuring a file with summary statistics is created.
3. Compare the scalability of the system by looking at the diffs in the median response times of the various endpoints, and observe any broken features as a result of the changes.