# Application profiling

Create measurements over Kubernetes and profiling application.

## Usage
1. **Create a new configuration file**

  Examples under `configs` directory. You can configure cluster, benchmarking and load generator tool. Setup the benchmark environment. (Eg: min-, max QPS and pods' resource limits )

2. **Start the benchmarking**

  Start master script: `python3 benchmark.py your-config.yaml`. Result goes to `results` directory. 
  Full benchmark and visualize flowchart:
  
  ![Full benchmark and visualize](https://raw.githubusercontent.com/Tutkovics/benchmarking/master/figures/test/flowchart_clear_vertical_average.png)
  
3. **Visualize results**

  TODO
