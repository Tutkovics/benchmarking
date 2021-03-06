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

        config_values["application_name"] = config["app"]["name"]
        config_values["application_repo"] = config["app"]["repo"]
        config_values["application_scale"] = config["app"]["scale"]
        config_values["application_namespace"] = config["app"]["namespace"]
        config_values["application_options"] = config["app"]["options"]

        config_values["loader_name"] = config["loader"]["name"]
        config_values["loader_repo"] = config["loader"]["repo"]
        config_values["loader_options"] = config["loader"]["options"]
        config_values["loader_namespace"] = config["loader"]["namespace"]
        config_values["loader_load"] = config["loader"]["load"]

        config_values["prometheus_deploy"] = config["prometheus"]["deploy"]
        config_values["prometheus_name"] = config["prometheus"]["name"]
        config_values["prometheus_repo"] = config["prometheus"]["repo"]
        config_values["prometheus_options"] = config["prometheus"]["options"]
        config_values["prometheus_namespace"] = config["prometheus"]["nspace"]

    return config_values
