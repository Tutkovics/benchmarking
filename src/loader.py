from cluster import Cluster
import time
import requests
import os
import json
import urllib

class Loader():

    def __init__(self, cluster, config):
        self.k8s = cluster
        self.config = config


        if config["prometheus_deploy"] == "True":
            self.prometheus_install()

        # self.locust_install()

        # self.application_install()

        # self.locust_load(10,10)

        self.measure()


    def __str__(self):
        return "Loader for: " + str(self.k8s) 

    
    def locust_install(self):
        """Function to install load generator with the given parameters
        """
        self.k8s.helm_install(
            self.config["loader_name"],
            self.config["loader_repo"],
            self.config["loader_namespace"],
            self.config["loader_options"],
        )


    def prometheus_install(self):
        """Function to install Prometheus with the given parameter if need
        """
        self.k8s.helm_install(
            self.config["prometheus_name"],
            self.config["prometheus_repo"],
            self.config["prometheus_namespace"],
            self.config["prometheus_options"],
        )


    def application_install(self, params = {}):
        """Create and scale the profiling application

        :param params: dictionary contains optional settings for application. Eg: cpu limit
        :type params: dict, optional
        """
        self.k8s.helm_install(
            self.config["application_name"],
            self.config["application_repo"],
            self.config["application_namespace"],
            self.config["application_options"],
            params
            # {
            #     self.config["application_horizontal"]: 5, \
            #     self.config["application_vertical"]: "480Mi", \
            # },
        )


    def locust_load(self, locust_count, hatch_rate):
        # NOTE: Doesn't work with python requsts
        start_command  = 'curl -XPOST http://192.168.99.111:30001/swarm -d"' \
                         'locust_count=' + locust_count+'&' \
                         'hatch_rate=' + hatch_rate+'"'
        
        print(start_command)
        os.system(start_command)

        # NOTE: Empirically 3 minute
        time.sleep(60)  # wait time to hatch and system warmup

        start_time = time.time()

        # run measurement the given time
        time.sleep(int(self.config["loader_load"]["time"]))

        end_time = time.time()

        # stop locust swarm
        os.system('curl http://192.168.99.111:30001/stop')

        a = requests.get("http://192.168.99.111:30001/stats/requests/csv")
        # print(a.content)

        # TODO: process prometheus data 
        cpu, memory = self.prometheus_get_statistic(start_time, end_time)

        self.write_statisctic([cpu, memory])



    def write_statisctic(self, data):
        with open("../tmp/data.txt", "w") as f: 
            f.write(str(data)) 
        

    def prometheus_get_statistic(self, start, end):
        """Get usage statistic from Prometheus.

        :param start: start time for the load
        :type start: time
        :param end: end time for the load
        :type end: time
        :return: Cpu and memory usage in the requested time
        :rtype: 2 json object
        """

        # NOTE: could use prometheus python client
        cpu_query = {"query": "sum(rate(container_cpu_usage_seconds_total{image!=''}[3m])) by (namespace)",
                     "start": str(start),
                     "end": str(end),
                     "step": "1",
                     "timeout": "1000ms"
        }
        
        memory_query = {"query": "sum(rate(container_memory_usage_bytes{image!=''}[3m])) by (namespace)",
                        "start": str(start),
                        "end": str(end),
                        "step": "1",
                        "timeout": "1000ms"
        }


        url = "http://" + self.config["cluster_ip"] + ":30000/api/v1/query_range?"

        cpu_res = json.loads(requests.get(url + urllib.parse.urlencode(cpu_query)).text)
        memory_res = json.loads(requests.get(url + urllib.parse.urlencode(memory_query)).text)

        return cpu_res, memory_res


    def measure(self):
        scale_options = self.config["application_scale"]

        # get length of the first "value" from dictionary
        sum_test_environment = len(next(iter(scale_options.values())))

        for i in range(sum_test_environment):
            # additional settings for each test/scale case
            # Eg: {'resources.limits.memory': '64Mi', 'resources.limits.cpu': '200m', 'replicas': '2'}
            settings = {}
            for parameter in scale_options:
                settings[parameter] = scale_options[parameter][i]
            print(settings)

            # create test environment
            self.application_install(settings)

            users_to_simulate =  self.config["loader_load"]["users"]
            hatch_rate =  self.config["loader_load"]["hatch"]

            # create load
            self.locust_load(users_to_simulate, hatch_rate)
