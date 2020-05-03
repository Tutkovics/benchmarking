from cluster import Cluster
import time


class Loader():

    def __init__(self, cluster, config):
        self.k8s = cluster
        self.config = config


        if config["prometheus_deploy"] == "True":
            self.prometheus_install()

        self.locust_install()

        # self.applicapplication_scale()


    def __str__(self):
        return "Loader for: " + str(self.k8s) 

    
    def locust_install(self):
        #print(type(self.config["loader_options"]))
        #print(self.config["loader_options"])
        self.k8s.helm_install(
            self.config["loader_name"],
            self.config["loader_repo"],
            self.config["loader_namespace"],
            self.config["loader_options"],
        )


    def prometheus_install(self):
        self.k8s.helm_install(
            self.config["prometheus_name"],
            self.config["prometheus_repo"],
            self.config["prometheus_namespace"],
            self.config["prometheus_options"],
        )


    def application_install(self, cpu, memoy, replicas):
        self.k8s.helm_install(
            self.config["application_name"],
            self.config["application_repo"],
            self.config["application_namespace"],
            self.config["application_options"],
            {
                self.config["application_horizontal"]: 5, \
                self.config["application_vertical"]: "480Mi", \
            },
        )

    def application_scale(self):
        self.application_install(cpu, memoy, replicas)

