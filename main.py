from cluster import Cluster
from helper import read_config_file
import yaml
import sys




def main():
    """Main function. 
    This will orchestrate the measurement
    """

    # read the given config file and store values
    config = read_config_file( str(sys.argv[1]) )


    k8s = Cluster(config["cluster_name"])
    k8s.get_name()
    k8s.get_all_nodes()

    ret = k8s.get_all_pods()
    for i in ret.items:
        pass
        #print("%s\t%s\t%s" %
        #      (i.status.pod_ip, i.metadata.namespace, i.metadata))

    


if __name__ == '__main__':
    # check if all ready to launch 
    if len(sys.argv) != 2:
        # if onfig file is not given
        raise("Please give (one and only one) configuration yaml file")
        sys.exit(-1)
    elif(False):
        pass
    else:
        main()