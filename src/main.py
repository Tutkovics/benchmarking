from cluster import Cluster
from helper import read_config_file
# from exceptions import ConfigFileError
import sys


def main():
    """Main function.
    This will orchestrate the measurement
    """

    # read the given config file and store values
    config = read_config_file(str(sys.argv[1]))

    k8s = Cluster(config["cluster_name"])
    print("Cluster: ", str(k8s))

    #k8s.helm_install(config["application_name"], config["application_repo"])
    k8s.helm_install(
        config["application_name"],
        config["application_repo"],
        config["application_namespace"],
        { 
            config["application_horizontal"]: 5, \
            config["application_vertical"]: "480Mi", \
        }
    )
    # k8s.helm_uninstall(config["application_name"])


if __name__ == '__main__':
    try:
        # check if all ready to launch
        if len(sys.argv) != 2:
            # if onfig file is not given
            raise("Please give (one and only one) configuration yaml file")
            sys.exit(-1)
        elif(False):
            pass
        else:
            main()
    finally:
        print("Program exited")
