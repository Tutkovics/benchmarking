import time
import yaml


def read_config_file(file_name):
    """Setup config parameters
    Read and store configuration parameters
    from given config file
    """

    with open(file_name) as config_file:
        config_values = {}
        config = yaml.safe_load(config_file)

        # get values from yaml
        config_values["cluster_name"] = config["cluster"]["name"]
        config_values["cluster_ip"] = config["cluster"]["ip"]

        config_values["application_name"] = config["application"]["name"]
        config_values["application_repo"] = config["application"]["repo"]
        config_values["application_scale"] = config["application"]["scale"]
        config_values["application_namespace"] = config["application"]["namespace"]
        config_values["application_options"] = config["application"]["options"]

        config_values["loader_name"] = config["loader"]["name"]
        config_values["loader_repo"] = config["loader"]["repo"]
        config_values["loader_options"] = config["loader"]["options"]
        config_values["loader_namespace"] = config["loader"]["namespace"]
        config_values["loader_load"] = config["loader"]["load"]

        config_values["prometheus_deploy"] = config["prometheus"]["deploy"]
        config_values["prometheus_name"] = config["prometheus"]["name"]
        config_values["prometheus_repo"] = config["prometheus"]["repo"]
        config_values["prometheus_options"] = config["prometheus"]["options"]
        config_values["prometheus_namespace"] = config["prometheus"]["namespace"]
        

    return config_values


def timeit(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print("func:%r args:[%r, %r] took: %2.4f sec" %
              (f.__name__, args, kw, te-ts))
        return result

    return timed
