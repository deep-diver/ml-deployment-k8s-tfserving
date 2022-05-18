# Load Test with Locust

This directory contains a Locust script for load testing. 

```
│   locustfile.py    # gRPC locust client
│   load_test.conf   # load test configs
│   test_grpc_api.py # test script to call gRPC server
│   cat_224x224.jpeg # resized test image
```

## How to run load tests

1. Install Locust with `pip`. You have to open up a new terminal session (or sourcing the `~/.bashrc`) to enable `locust` CLI.

```bash
pip install locust
```

2. Replace placeholderes. In `load_test.conf` and `locustfile.py`, there are three placeholders of `<<EXTERNAL-CLUSTER-IP>>`. You have to replace those with the actual endpoint that your TFServing is deployed on. Also you need to replace `<<WHERE-TO-STORE-RESPORT>>` placeholders in `load_test.conf` with where you want to save the final report.


3. `locust` the `load_test.conf`. Every bits of configurations are defined in `load_test.conf`, so you only need to specify it in `--config` option.

```bash
$ locust --config=load_test.conf
```

### Inside `load_test.conf`

```
locustfile = locustfile.py
headless = true
users = 150
spawn-rate = 1
run-time = 5m
host = http://<<EXTERNAL-CLUSTER-IP>>
html = <<WHERE-TO-STORE-REPORT>>.html
csv = <<WHERE-TO-STORE-REPORT>>
```

More complete descriptions for each configuration can be found in the [official doc](https://docs.locust.io/en/stable/configuration.html), but here we provide a brief summary.

- **locustfile**: the python script file which implements the client behaviour.
- **headless**: whether not to use UI or not. If you set this `True`, no UI is involved, and the load test runs right away.
- **users**: the maximum number of users(requests).
- **spawn-rate**: how many users should be added at a time. You can decide the time interval between spawns in the `locustfile.py`.
- **run-time**: how much time the load test should be conducted. Here, `m` means minutes.
- **host**: endpoint
- **html**: path where the HTML based report should be stored.
- **csv**: path where the CSV based report should be stored. Notice that we don't set file extension `.csv` here because multiple csv files for each circumstances would be generated.