from cluster import Cluster
import time


class Loader():

    def __init__(self, cluster, config):
        self.k8s = cluster
        self.config = config


        if config["prometheus_deploy"] == "True":
            self.prometheus_install()

        self.locust_install()



    def __str__(self):
        return "Loader for: " + str(self.k8s) 

    
    def locust_install(self):
        #print(type(self.config["loader_options"]))
        #print(self.config["loader_options"])
        self.k8s.helm_install(
            self.config["loader_name"],
            self.config["loader_repo"],
            self.config["loader_namespace"],
        )

    def prometheus_install(self):
        self.k8s.helm_install(
            self.config["prometheus_name"],
            self.config["prometheus_repo"],
            self.config["prometheus_namespace"],
            self.config["prometheus_options"],
        )

