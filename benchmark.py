#!/usr/bin/env python3

### INCLUDES
# Used libaries for measurements
###
import os
import sys
import logging
import time
import fileinput
import re
import json
import requests
import urllib
import yaml
import datetime
#from datetime import datetime

### VARIABLES
#  This values come from a config yaml file
###
if len(sys.argv) != 2:
    print("Please give configuration yaml file")
    sys.exit(-1)
else:
    with open( str(sys.argv[1]) ) as config_file:
        config = yaml.safe_load(config_file)

        # get values from yaml
        mode = config["develop"]["mode"]
        log_level = config["develop"]["log_level"] # does not take effect
        cluster_ip = config["cluster"]["ip"]
        cluster_name = config["cluster"]["name"]
        worker_node = config["cluster"]["worker_node"]
        benchmark_node = config["cluster"]["benchmark_node"]
        deploy_prometheus = config["prometheus"]["deploy"]
        prometheus_node_port = config["prometheus"]["node_port"]
        application_name = config["application"]["name"]
        application_image = config["application"]["image"]
        application_port = config["application"]["port"]
        benchmark_tool = config["benchmark"]["tool"]["name"]
        benchmark_image = config["benchmark"]["tool"]["image"]
        benchmark_port = config["benchmark"]["tool"]["port"]
        benchmark_time = config["benchmark"]["time"]
        qps_min = int(config["benchmark"]["qps_min"])
        qps_max = int(config["benchmark"]["qps_max"])
        qps_granularity = int(config["benchmark"]["qps_granularity"])
        pods = config["benchmark"]["pods"].split(",")
        cpu = config["benchmark"]["cpu"].split(",")
        memory = config["benchmark"]["memory"].split(",")
        save_results = config["benchmark"]["save_results"]

results_to_file = {} # every component can add information 
tmp_results = {}

### INITIALIZE

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) # here set log level. TODO: get from configuration (debug, info, warning, error, critical)
ch = logging.StreamHandler() # create console handler
formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch) # add the handlers to logger
logging.getLogger("urllib3").setLevel(logging.WARNING) # hope to disable requests libary logging (don't spam my logging infos)

def dev_null():
    # hide stdout from console commands
    if mode != "develop":
        return " > /dev/null"
    else:
        return ""


def cluster_config():
    logger.debug("Start cluster config")
    # configure kubectl context
    if( os.system("kubectl config use-context " + cluster_name + dev_null()) == 0):
        # command run with success
        logger.debug("Kubectl using context: " + cluster_name)
    else:
        logger.warning("Kubectl can't context switch to: " + cluster_name)

    # need to deploy prometheus
    if(deploy_prometheus):
        if (os.system("kubectl apply -f prometheus/ " + dev_null()) == 0):
            # command run with success
            logger.debug("Prometheus successfully started")
        else:
            logger.warning("Prometheus can't star")
    
    # TODO: flag nodes 
    logger.debug("End cluster configuration")

def deploy_application(test_case_number):
    logger.debug("Start deploy application")
    with open("application_template.yaml") as template_file:
        with open("./tmp/live_applicatin_deployment.yaml", "w") as live_file:
            for line in template_file:
                # dictioanry for replace missing values in template configuration
                replace = {"[APPLICATION_NAME]" : application_name, "[POD_COUNT]" : pods[test_case_number], "[APPLICATION_IMAGE]" : application_image, "[CPU]" : cpu[test_case_number], "[MEMORY]" : memory[test_case_number], "[APPLICATION_PORT]" : application_port, "[WORKER_NODE]" : worker_node}
                # replace values with regex
                new_line = re.sub('({})'.format('|'.join(map(re.escape, replace.keys()))), lambda m: replace[m.group()], line)
                live_file.writelines(new_line) # write the updated line

    values = "measurement: #" + str(test_case_number) + ", Pod count: " + pods[test_case_number] + ", CPU: " + cpu[test_case_number] + ", Memory: " + memory[test_case_number]
    logger.debug("New configuration created for application [" + values + "]")


    results_to_file["number_of_pod"] = pods[test_case_number]
    results_to_file["benchmark_time"] = benchmark_time
    results_to_file["cpu_limit"] = cpu[test_case_number]
    results_to_file["memory_limit"] = memory[test_case_number]

    # apply new configuration file
    if( os.system("kubectl apply -f ./tmp/live_applicatin_deployment.yaml" + dev_null()) == 0):
        logger.debug("Application deployment and service applied")
    else:
        logger.warning("Can't create application deployment")



def get_service_ip(app_name):
    logger.debug("Get " + app_name +" service IP")
    services = json.loads(os.popen("kubectl get services --all-namespaces -o json").read()) # get services in json  
    valid_service = False

    # find cluster IP for given service
    for service in services["items"]:
        if service["metadata"]["name"] == app_name:
            ip = service["spec"]["clusterIP"]
            valid_service = True
    
    if(valid_service):
        logger.debug(app_name + " --> " + ip)
        # return ip if found
        return ip
    else:
        logger.warning("Can't find service ip for " + app_name)

def deploy_benchmark_tool():
    # TODO: almost same as deploy_application --> merge them
    # TODO: check if valid tool was given
    logger.debug("Start deploy benchmark tool")
    with open("benchmark_tool_template.yaml") as template_file:
        with open("./tmp/live_benchmark_deployment.yaml", "w") as live_file:
            for line in template_file:
                # dictioanry for replace missing values in template configuration
                replace = {"[BECHMARK_NAME]" : benchmark_tool, "[BENCHMARK_IMAGE]" : benchmark_image, "[BENCHMARK_PORT]" : benchmark_port, "[BENCHMARK_NODE]" : benchmark_node}
                # replace values with regex
                new_line = re.sub('({})'.format('|'.join(map(re.escape, replace.keys()))), lambda m: replace[m.group()], line)
                live_file.writelines(new_line) # write the updated line
    logger.debug("New live configuration created for benchmark")

    # apply new configuration file
    if( os.system("kubectl apply -f ./tmp/live_benchmark_deployment.yaml" + dev_null()) == 0):
        logger.debug("Benchmark deployment and service created")
    else:
        logger.warning("Can't create benchmark deployment")

def wait_for_start_pods():
    logger.debug("Check and wait all pods to start")
    need_to_wait = True

    while(need_to_wait):
        need_to_wait = False
        # if too slow or need much memory enough to get from default namespace
        pods = json.loads(os.popen("kubectl get pods --all-namespaces -o json").read()) # get pods in json

        for pod in pods["items"]:
            if pod["status"]["phase"] != "Running":
                # if exist pod with Pedding, Terminatin or other status
                # commented out, becaus of spam --> logger.debug("Pod: " + pod["metadata"]["name"] + " need more time. (" + pod["status"]["phase"] + ")")
                need_to_wait = True

        # wait 3 sec before check again
        # something to see while waiting --> print(".", end='', flush=True)
        time.sleep(3)
        

    logger.debug("All pods running")

def delete_application(kill_prometheus = False):
    # delte measured deployment if needed delete prometeus too
    if(kill_prometheus):
        if (os.system("kubectl delete -f prometheus/ " + dev_null()) == 0):
            # command run with success
            logger.debug("Prometheus successfully deleted")
        else:
            logger.warning("Can't delete Prometheus")

    logger.debug("Delete " + application_name + " deployment")

    # delete current application deployment
    if( os.system("kubectl delete -f ./tmp/live_applicatin_deployment.yaml" + dev_null()) == 0):
        logger.debug("Application deployment and service successfully deleted")
    else:
        logger.warning("Can't delete application deployment and service")

    # delete current benchmark deployment
    if( os.system("kubectl delete -f ./tmp/live_benchmark_deployment.yaml" + dev_null()) == 0):
        logger.debug("Benchmark deployment and service successfully deleted")
    else:
        logger.warning("Can't delete benchmark deployment and service")

def kill_all_app_pod():
    name = application_name + "-deployment"

    deployments = json.loads(os.popen("kubectl get deployment --all-namespaces -o json").read())
    for deployment in deployments["items"]:
        if deployment["metadata"]["name"] == name:
            # will not throw error in #1 measurement when deployment not exists
            os.system("kubectl scale deploy " + name + " --replicas=0" + dev_null())
            logger.debug("Wait to scale down all pod")
    time.sleep(2)
    wait_for_start_pods() # funny but it works

def run_measurement():
    number_of_test_cases = len(pods)
    for i in range(0, number_of_test_cases):
        global tmp_results
        
        json_array = []

        for requested_qps in range(qps_min, qps_max, qps_granularity):
            tmp_results.clear()
            time.sleep(20)

            # kill all pod 
            kill_all_app_pod()

            time.sleep(10)

            # scale up and down pods
            deploy_application(i)

            wait_for_start_pods() # wait until apply changes

            # generate traffic with benchmark tool
            service_ip = get_service_ip(application_name + "-service")
            
            # benchmark tool specific code! (until prometheus)

            tmp_results["requested_qps"] = requested_qps

            timeout = 200 # set fortio timeout [ms]

            url_benchmark = "http://" + cluster_ip + ":30001/fortio/?labels=&url=http://" + service_ip + ":" + application_port + "&qps=" + str(requested_qps) + "&t=" + benchmark_time + "s&n=&c=10&p=50%2C+75%2C+90%2C+99%2C+99.9&r=0.0001&runner=http&grpc-ping-delay=0&json=on&load=Start&timeout=" + str(timeout) + "ms"
            logger.debug("Benchmarking on url: " + url_benchmark)

            start_time = time.time()  # start and end time needed for prometheus
            benchmark_res = json.loads((requests.get(url_benchmark)).text)

            tmp_results["actualQPS"] = benchmark_res["ActualQPS"]
            tmp_results["fortio_req_qps"] = benchmark_res["RequestedQPS"]
            tmp_results["fortio_threads"] = benchmark_res["NumThreads"]
            tmp_results["min_response"] = benchmark_res["DurationHistogram"]["Min"]
            tmp_results["max_response"] = benchmark_res["DurationHistogram"]["Max"]
            tmp_results["avg_response"] = benchmark_res["DurationHistogram"]["Avg"]
            tmp_results["dev_response"] = benchmark_res["DurationHistogram"]["StdDev"]
            tmp_results["response_histogram"] = benchmark_res["DurationHistogram"]["Data"]
            

            time.sleep(30) # deleay to send all statistics
            end_time = time.time()

            # get data from Prometheus
            get_prometheus_stats(start_time, end_time, i)

            json_array.append(dict(tmp_results))


        results_to_file["measurements"] = json_array # convert to string for bugfix

        # write data to file
        if( save_results == "True"):
            write_results_to_file(i)

def get_prometheus_stats(start_time, end_time, test_case_number):
    # urls for query
    cpu_query = { "query": "sum(container_cpu_usage_seconds_total{pod=~'" + application_name + "-deployment-.+'}) by (pod)", "start": str(start_time), "end": str(end_time), "step": "0.1", "timeout": "1000ms" }
    memory_query = { "query": "sum(container_memory_usage_bytes{pod=~'" + application_name + "-deployment-.+'}) by (pod)", "start": str(start_time), "end": str(end_time), "step": "0.1", "timeout": "1000ms" }
    url = "http://" + cluster_ip + ":30000/api/v1/query_range?" 

    # actual querys
    logger.debug("Prometheus API url: " + url + urllib.parse.urlencode(cpu_query))
    prometheus_cpu_res = json.loads(requests.get(url + urllib.parse.urlencode(cpu_query)).text)
    prometheus_memory_res = json.loads(requests.get(url + urllib.parse.urlencode(memory_query)).text)

    calculate_usages(prometheus_cpu_res, prometheus_memory_res, test_case_number)

def calculate_usages(prometheus_cpu_res, prometheus_memory_res, test_case_number):
    global tmp_results

    pods_consumed_cpu = 0 # count number of pods used cpu and memory
    pods_consumed_memory = 0 
    value_of_cpu_used = 0.0 # sum of pods' memory and cpu usage
    value_of_memory_used = 0.0
    pods_statistic = "" # for debugging collect statistic


    if prometheus_cpu_res["status"] == "success": # api responded with success status 
        logger.debug("Successfully get CPU metrics from Prometheus")
        for pod in prometheus_cpu_res["data"]["result"]:
            # delete pod statistic which was not increment usage
            if pod["values"][0][1] == pod["values"][-1][1]:
                pods_statistic += "[CPU] Pod: " + pod["metric"]["pod"] + " doesn't incremented -- " + pod["values"][0][1] + "\n"
            else:
                pods_consumed_cpu += 1
                value_of_cpu_used += float(pod["values"][-1][1])
                pods_statistic += "[CPU] Pod: " + pod["metric"]["pod"] + " consumed: " + pod["values"][-1][1] + "\n"
        
        if str(pods_consumed_cpu) != pods[test_case_number]: # count more or less pods than should be
            logger.warning(str(pods_consumed_cpu) + " pods consumed CPU (should:" + pods[test_case_number] + ")")
    else:
        logger.debug("Can't get CPU metrics from Prometheus")

    if prometheus_memory_res["status"] == "success": # api responded with success status 
        logger.debug("Successfully get MEMORY metrics from Prometheus")
        for pod in prometheus_memory_res["data"]["result"]:
            # delete pod statistic which was not increment usage
            if pod["values"][0][1] == pod["values"][-1][1]:
                pods_statistic += "[MEMORY] Pod: " + pod["metric"]["pod"] + " doesn't incremented -- " + pod["values"][0][1] + "\n"
            else:
                pods_consumed_memory += 1
                value_of_memory_used += float(pod["values"][-1][1])
                pods_statistic += "[MEMORY] Pod: " + pod["metric"]["pod"] + " consumed: " + pod["values"][-1][1] + "\n"
        
        if str(pods_consumed_memory) != pods[test_case_number]: # count more or less pods than should be
            logger.warning(str(pods_consumed_memory) + " pods consumed MEMORY (should:" + pods[test_case_number] + ")")
    else:
        logger.debug("Can't get MEMORY metrics from Prometheus")

    tmp_results["cpu_used"] = value_of_cpu_used
    tmp_results["memory_used"] = value_of_memory_used
    print(tmp_results)


def write_results_to_file(id):
    # write to file
    #now = datetime.now()
    file_name = application_name + "-" + pods[id] + "-" + cpu[id] + "-" + memory[id] + "-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".json"
    print(file_name)

    with open("./results/" + file_name, "w") as res_file:
        global results_to_file
        results = json.dumps(results_to_file)
        res_file.write(str(results))
        results_to_file = {}


if __name__ == "__main__":
    start = str(datetime.datetime.now())
    results_to_file["start"] = start

    logger.debug("Start script: " + start)
    cluster_config()

    deploy_benchmark_tool()
    wait_for_start_pods()
    
    run_measurement()
    #get_service_ip(application_name + "-service")
    delete_application()

    logger.debug("End script: " + str(datetime.datetime.now()))
