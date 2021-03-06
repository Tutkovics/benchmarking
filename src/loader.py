import time
import datetime
import requests
import os
import json
import urllib


class Loader():

    def __init__(self, cluster, config):
        """Initialise to load

        :param cluster: cluster to install application
        :type cluster: Cluseter
        :param config: config parameters from config file
        :type config: dictionary
        """
        self.k8s = cluster
        self.config = config

        self.directory = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + \
                        "-" + self.config["application_name"]

        self.locust_install()
        # self.application_install()
        # self.locust_load(10,10)

        self.measure()


    def __str__(self):
        """String representation

        :return: name of cluster to load
        :rtype: string
        """

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


    def application_install(self, params={}):
        """Create and scale the profiling application

        :param params: dictionary contains optional settings for application.
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


    def locust_load(self, locust_count, settings):
        """Create load from Locust and collect datas from the measurement

        :param locust_count: number of users to simulate
        :type locust_count: int
        :param settings: envronment settings: #pods, cpu, memory
        :type settings: dictionary
        """

        # NOTE: Doesn't work with python requsts
        start_command = 'curl -XPOST http://192.168.99.111:30001/swarm -d"' \
                        'locust_count=' + str(locust_count) + '&' \
                        'hatch_rate=' + str(locust_count) + '"'

        print(start_command)
        os.system(start_command)

        # NOTE: Empirically 3 minute
        time.sleep( (60*3) )  # wait time to hatch and system warmup

        start_time = time.time()

        # run measurement the given time
        time.sleep(int(self.config["loader_load"]["time"]))

        end_time = time.time()

        # stop locust swarm
        os.system('curl http://192.168.99.111:30001/stop')

        a = requests.get("http://192.168.99.111:30001/stats/requests/csv")
        b = requests.get("http://192.168.99.111:30001/stats/distribution/csv")
        c = requests.get("http://192.168.99.111:30001/stats/failures/csv")
        d = requests.get("http://192.168.99.111:30001/exceptions/csv")
        # print(a.content)

        request = self.csv_to_json(a)
        distribution = self.csv_to_json(b)
        failures = self.csv_to_json(c)
        exceptions = self.csv_to_json(d)

        # TODO: process prometheus data
        cpu, memory = self.prometheus_get_statistic(start_time, end_time)

        settings["users"] = str(locust_count)
        settings["app"] = str(self.config["application_name"])

        self.write_statisctic(settings, request, distribution, failures, exceptions, cpu, memory)


    def csv_to_json(self, response):
        """Convert requests object to json to write data to file

        :param response: locust response
        :type response: requests.response
        """

        dictionary_row = response.content.decode("utf-8").split('\n')
        # only last row need.
        keys = dictionary_row[0].split(',')
        values = dictionary_row[-1].split(',')
        
        return({x.replace('"',''):y.replace('"','') for x,y in zip(keys,values)})


    def write_statisctic(self, settings, request, distribution, failures, exceptions, cpu, memory):
        """Concatenate the dictionaries, create a new directory and write the results

        :param settings: enviroment settings
        :type settings: dictionary
        :param locust: locust response related info
        :type locust: dictionary
        :param cpu: cpu usage info from prometheus
        :type cpu: dictionary
        :param memory: memory usage info from prometheus
        :type memory: dictionary
        """

        file_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + \
                    "-" + self.config["application_name"] + "-" + \
                    str.join("-", settings.values()) + ".json"

        if not os.path.exists("../results/" + self.directory):
            os.makedirs("../results/" + self.directory)

        with open("../results/" + self.directory + "/" + file_name, "w") as results_file:
            data = {"settings" : settings,
                    "locust" : request,
                    "distribution" : distribution,
                    "failures": failures,
                    "exceptions" : exceptions,
                    "cpu" : cpu,
                    "memory" : memory}
            results_file.write(json.dumps(data, indent=4))



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
        cpu_query = {"query": "sum(rate(container_cpu_usage_seconds_total{image!='', namespace=~'default|metrics', container!='POD'}[3m])) by (container)",
                     "start": str(start),
                     "end": str(end),
                     "step": "1",
                     "timeout": "1000ms"
        }

        memory_query = {"query": "sum(rate(container_memory_usage_bytes{image!='', namespace=~'default|metrics', container!='POD'}[3m])) by (container)",
                        "start": str(start),
                        "end": str(end),
                        "step": "1",
                        "timeout": "1000ms"
        }

        url = "http://" + self.config["cluster_ip"] + ":30000/api/v1/query_range?"

        cpu_res = json.loads(requests.get(url + urllib.parse.urlencode(cpu_query)).text)
        memory_res = json.loads(requests.get(url + urllib.parse.urlencode(memory_query)).text)

        return cpu_res, memory_res # cpu_metrics_res, memory_metrics_res


    def measure(self):
        """Do the measurement based on the given parameters from config file
        """

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

            self.k8s.helm_uninstall(self.config["application_name"], self.config["application_namespace"])
            # create test environment
            time.sleep(60)
            self.application_install(settings)

            for user_number in range(int(self.config["loader_load"]["min_users"]),
                                     int(self.config["loader_load"]["max_users"])+1,
                                     int(self.config["loader_load"]["step"])):
                # run measurement on every user number
                self.locust_load(user_number, settings)
