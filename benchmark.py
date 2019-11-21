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

### VARIABLES
#  This values come from a config yaml file
###
if( len(sys.argv) != 2 ):
    print("Please give configuration yaml file")
    sys.exit(-1)
else:
    with open( str(sys.argv[1]) ) as config_file:
        config = yaml.safe_load(config_file)

        # get values from yaml
        mode = config["develop"]["mode"]
        log_level = config["develop"]["log_level"]
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
        qps_min = config["benchmark"]["qps_min"]
        qps_max = config["benchmark"]["qps_max"]
        qps_granularity = config["benchmark"]["qps_granularity"]
        pods = ["2", "8"] # config["benchmark"]["pods"]
        cpu = ['200m', '50m'] # config["benchmark"]["cpu"]
        memory = ['64Mi', '200Mi'] #config["benchmark"]["memory"]

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
    if(mode != "develop"):
        return " > /dev/null"
    else:
        return ""

# measurement start time

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

def deploy_application():
    logger.debug("Start deploy application")
    with open("application_template.yaml") as template_file:
        with open("./tmp/live_applicatin_deployment.yaml", "w") as live_file:
            for line in template_file:
                # dictioanry for replace missing values in template configuration
                replace = {"[APPLICATION_NAME]" : application_name, "[POD_COUNT]" : pods[0], "[APPLICATION_IMAGE]" : application_image, "[CPU]" : cpu[0], "[MEMORY]" : memory[0], "[APPLICATION_PORT]" : application_port, "[WORKER_NODE]" : worker_node}
                # replace values with regex
                new_line = re.sub('({})'.format('|'.join(map(re.escape, replace.keys()))), lambda m: replace[m.group()], line)
                live_file.writelines(new_line) # write the updated line
    logger.debug("New live configuration created for application")

    # apply new configuration file
    if( os.system("kubectl apply -f ./tmp/live_applicatin_deployment.yaml" + dev_null()) == 0):
        logger.debug("Application deployment and service created")
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
    logger.debug("Check and wait all pods to start - be patient or check in other terminal :)")
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
    os.system("kubectl scale deploy nginx-deployment --replicas=0" + dev_null())
    logger.debug("Wait to scale down all pod")
    time.sleep(10)

def run_measurement():
    # TODO: fragment function
    number_of_test_cases = len(pods)
    for i in range(0, number_of_test_cases):
        # kill all pod 
        kill_all_app_pod()

        # podok fel / le skálázása
        # TODO: merge with deploy_application() function
        logger.debug("Start new measurement")
        with open("application_template.yaml") as template_file:
            with open("./tmp/live_applicatin_deployment.yaml", "w") as live_file:
                for line in template_file:
                    # dictioanry for replace missing values in template configuration
                    replace = {"[APPLICATION_NAME]" : application_name, "[POD_COUNT]" : pods[i], "[APPLICATION_IMAGE]" : application_image, "[CPU]" : cpu[i], "[MEMORY]" : memory[i], "[APPLICATION_PORT]" : application_port, "[WORKER_NODE]" : worker_node}
                    # replace values with regex
                    new_line = re.sub('({})'.format('|'.join(map(re.escape, replace.keys()))), lambda m: replace[m.group()], line)
                    live_file.writelines(new_line) # write the updated line
        values = "measurement: #" + str(i) + ", Pod count: " + pods[i] + ", CPU: " + cpu[i] + ", Memory: " + memory[i]
        logger.debug("New configuration created for application [" + values + "]")

        # apply new configuration file
        if( os.system("kubectl apply -f ./tmp/live_applicatin_deployment.yaml" + dev_null()) == 0):
            logger.debug("Application deployment and service scaled")
        else:
            logger.warning("Can't scale application deployment")

        wait_for_start_pods() # wait until apply changes

        # generate traffic with benchmark tool
        service_ip = get_service_ip(application_name + "-service")
        
        # benchmark tool specific code! (until prometheus)
        url_benchmark = "http://" + cluster_ip + ":30001/fortio/?labels=&url=http://" + service_ip + ":" + application_port + "&qps=" + qps_min + "&t=" + benchmark_time + "s&n=&c=10&p=50%2C+75%2C+90%2C+99%2C+99.9&r=0.0001&runner=http&grpc-ping-delay=0&json=on&load=Start&timeout=1000ms"
        logger.debug("Benchmarking on url: " + url_benchmark)

        start_time = time.time()  # start and end time needed for prometheus
        benchmark_res = json.loads((requests.get(url_benchmark)).text)
        time.sleep(10) # deleay to send all statistics
        end_time = time.time()

        # process resoults from benchmark tool
        # TODO

        # get data from Prometheus
        # TODO: get out from url 
        #container_cpu_usage_seconds_total{pod=~"nginx-deployment-.+"}
        #print(str(start_time) + "   " + str(end_time))

        cpu_query = { "query": "sum(container_cpu_usage_seconds_total{pod=~'" + application_name + "-deployment-.+'}) by (pod)", "start": str(start_time), "end": str(end_time), "step": "0.1", "timeout": "1000ms" }
        memory_query = { "query": "sum(container_memory_usage_bytes{pod=~'" + application_name + "-deployment-.+'}) by (pod)", "start": str(start_time), "end": str(end_time), "step": "0.1", "timeout": "1000ms" }
        url = "http://" + cluster_ip + ":30000/api/v1/query_range?" 

#url_cpu = "http://" + cluster_ip + ":30000/api/v1/query_range?query=sum(container_cpu_usage_seconds_total{pod=~'" + application_name + "-deployment-.+'})&start=" + str(start_time) + "&end=" + str(end_time) + "&step=0.1&timeout=1000ms"
        logger.debug("Prometheus API url: " + url + urllib.parse.urlencode(cpu_query))
        prometheus_cpu_res = json.loads(requests.get(url + urllib.parse.urlencode(cpu_query)).text)
        prometheus_memory_res = json.loads(requests.get(url + urllib.parse.urlencode(memory_query)).text)
        #print(str(json.loads(requests.get(url_cpu).text)))
        
        #mem_usage = json.loads(requests.get(url="http://10.106.36.184:9090/api/v1/query_range?query=sum(rate(container_memory_usage_bytes{{container_name=\"nodejs-app\"}}[10s]))&start={0}&end={1}&step={2}".format(start_time,end_time,1,benchmark_time)).text)

        # write data to file
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
            
            if pods_consumed_cpu != pods[i]: # count more or less pods than should be
                logger.warning(str(pods_consumed_cpu) + " pods consumed CPU (should:" + pods[i] + ")")
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
            
            if pods_consumed_memory != pods[i]: # count more or less pods than should be
                logger.warning(str(pods_consumed_memory) + " pods consumed MEMORY (should:" + pods[i] + ")")
        else:
            logger.debug("Can't get MEMORY metrics from Prometheus")

        with open("./results/latest.json", "w") as res_file:
            res_file.write(str(benchmark_res))
            res_file.write(str(prometheus_cpu_res))
            res_file.write(pods_statistic)
            res_file.write("CPU: " + str(value_of_cpu_used) + " -- MEMORY: " + str(value_of_memory_used))

        # let the cluster and pods have free time
        time.sleep(50)



if __name__ == "__main__":

    logger.debug("Start script")
    cluster_config()
    deploy_application()
    deploy_benchmark_tool()
    wait_for_start_pods()
    
    run_measurement()
    get_service_ip(application_name + "-service")
    #delete_application()
