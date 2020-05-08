from cluster import Cluster
from loader import Loader
from helper import read_config_file
# from exceptions import ConfigFileError
import sys
import readline, glob


def main(config_file):
    """Main function.
    This will orchestrate the measurement
    """

    # read the given config file and store values
    config = read_config_file(config_file)

    k8s = Cluster(config["cluster_name"])
    
    print("Cluster: ", str(k8s))

    lo = Loader(k8s, config)

    # k8s.helm_uninstall_all()



if __name__ == '__main__':
    try:
        # check if all ready to launch
        if len(sys.argv) != 2:
            # if config file is not given
            print("Please give (one and only one) configuration yaml file")

            # get config file (on runtime) with autocomplete  
            def complete(text, state):
                return (glob.glob(text+'*')+[None])[state]

            readline.set_completer_delims(' \t\n;')
            readline.parse_and_bind("tab: complete")
            readline.set_completer(complete)

            config_file = input("Config file: ")

            main(config_file)
        elif(False):
            pass
        else:
            main(str(sys.argv[1]))
    finally:
        print("Program exited")
