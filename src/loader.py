from cluster import Cluster
import time
import requests
import os


class Loader():

    def __init__(self, cluster, config):
        self.k8s = cluster
        self.config = config


        if config["prometheus_deploy"] == "True":
            self.prometheus_install()

        # self.locust_install()

        # self.application_install()

        self.locust_load(10,10)


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


    def application_install(self):
        self.k8s.helm_install(
            self.config["application_name"],
            self.config["application_repo"],
            self.config["application_namespace"],
            self.config["application_options"],
            # {
            #     self.config["application_horizontal"]: 5, \
            #     self.config["application_vertical"]: "480Mi", \
            # },
        )

    def application_scale(self):
        self.application_install(cpu, memoy, replicas)


    def locust_load(self, locust_count, hatch_rate):
        # node_port = "30002"  # could read from config file
        # base_url = "http://" + self.config["cluster_ip"] + ":" + node_port

        # start_params = {'locust_count': self.config["loader_load"]["users"],
        #           'hatch_rate': self.config["loader_load"]["users"],          
        # }
        # start_url = base_url + "/swarm"

        # print(start_params)
        # start_load = requests.post(start_url, params = start_params) 

        # # print(str(start_load.data))
        # print(str(start_load.headers))


        os.system('curl -XPOST http://192.168.99.111:30001/swarm -d"locust_count='+
                   self.config["loader_load"]["users"]+'&hatch_rate='+
                   self.config["loader_load"]["users"]+'"')

        time.sleep(3)  # wait time to hatch and system warmup

        start_time = time.time()

        # run measurement the given time
        time.sleep(int(self.config["loader_load"]["time"]))

        end_time = time.time()

        os.system('curl http://192.168.99.111:30001/stop')

        # os.system('curl http://192.168.99.111:30001/stats/requests/csv')
        a = requests.get("http://192.168.99.111:30001/stats/requests/csv")
        print(a.content)
        

    def prometheus_get_info(self, start, end):
        pass