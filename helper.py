import time
import yaml

def read_config_file(file_name):
    """Setup config parameters
    Read and store configuration parameters \
    from given config file
    """

    
    with open( file_name ) as config_file:
        config_values = {}
        config = yaml.safe_load(config_file)

        # get values from yaml
        config_values["mode"] = config["develop"]["mode"]
        config_values["log_level"] = config["develop"]["log_level"]
        config_values["cluster_ip"] = config["cluster"]["ip"]
        config_values["cluster_name"] = config["cluster"]["name"]
        config_values["worker_node"] = config["cluster"]["worker_node"]
        config_values["benchmark_node"] = config["cluster"]["benchmark_node"]
        config_values["deploy_prometheus"] = config["prometheus"]["deploy"]
        config_values["prometheus_node_port"] = config["prometheus"]["node_port"]
        config_values["application_name"] = config["application"]["name"]
        config_values["application_image"] = config["application"]["image"]
        config_values["application_port"] = config["application"]["port"]
        config_values["benchmark_tool"] = config["benchmark"]["tool"]["name"]
        config_values["benchmark_image"] = config["benchmark"]["tool"]["image"]
        config_values["benchmark_port"] = config["benchmark"]["tool"]["port"]
        config_values["benchmark_time"] = config["benchmark"]["time"]
        config_values["qps_min"] = int(config["benchmark"]["qps_min"])
        config_values["qps_max"] = int(config["benchmark"]["qps_max"])
        config_values["qps_granularity"] = int(config["benchmark"]["qps_granularity"])
        config_values["pods"] = config["benchmark"]["pods"].split(",")
        config_values["cpu"] = config["benchmark"]["cpu"].split(",")
        config_values["memory"] = config["benchmark"]["memory"].split(",")
        config_values["save_results"] = config["benchmark"]["save_results"]

    return config_values


def timeit(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print('func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts))
        return result

    return timed