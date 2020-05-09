---
description: |
    API documentation for modules: src, src.benchmark, src.cluster, src.helper, src.loader, src.main.

lang: en

classoption: oneside
geometry: margin=1in
papersize: a4

linkcolor: blue
links-as-notes: true
...


    
# Namespace `src` {#src}




    
## Sub-modules

* [src.benchmark](#src.benchmark)
* [src.cluster](#src.cluster)
* [src.helper](#src.helper)
* [src.loader](#src.loader)
* [src.main](#src.main)






    
# Module `src.benchmark` {#src.benchmark}






    
## Functions


    
### Function `calculate_usages` {#src.benchmark.calculate_usages}



    
> `def calculate_usages(prometheus_cpu_res, prometheus_memory_res, test_case_number)`




    
### Function `cluster_config` {#src.benchmark.cluster_config}



    
> `def cluster_config()`




    
### Function `delete_application` {#src.benchmark.delete_application}



    
> `def delete_application(kill_prometheus=False)`




    
### Function `deploy_application` {#src.benchmark.deploy_application}



    
> `def deploy_application(test_case_number)`




    
### Function `deploy_benchmark_tool` {#src.benchmark.deploy_benchmark_tool}



    
> `def deploy_benchmark_tool()`




    
### Function `dev_null` {#src.benchmark.dev_null}



    
> `def dev_null()`




    
### Function `get_log_level` {#src.benchmark.get_log_level}



    
> `def get_log_level(argument)`




    
### Function `get_prometheus_stats` {#src.benchmark.get_prometheus_stats}



    
> `def get_prometheus_stats(start_time, end_time, test_case_number)`




    
### Function `get_service_ip` {#src.benchmark.get_service_ip}



    
> `def get_service_ip(app_name)`




    
### Function `is_pod_should_consume` {#src.benchmark.is_pod_should_consume}



    
> `def is_pod_should_consume(pod_name)`




    
### Function `kill_all_app_pod` {#src.benchmark.kill_all_app_pod}



    
> `def kill_all_app_pod()`




    
### Function `run_measurement` {#src.benchmark.run_measurement}



    
> `def run_measurement()`




    
### Function `wait_for_start_pods` {#src.benchmark.wait_for_start_pods}



    
> `def wait_for_start_pods()`




    
### Function `write_results_to_file` {#src.benchmark.write_results_to_file}



    
> `def write_results_to_file(id)`







    
# Module `src.cluster` {#src.cluster}







    
## Classes


    
### Class `Cluster` {#src.cluster.Cluster}



> `class Cluster(name, config_f)`


This class represent one Kubernetes cluster
    

Initialise cluster. Check and setup client and cluster

:param name: This will represent the cluster
:type name: string







    
#### Methods


    
##### Method `check_helm_client_install` {#src.cluster.Cluster.check_helm_client_install}



    
> `def check_helm_client_install(self)`


Check if installed helm command can used

:return: success of helm command
:rtype: bool

    
##### Method `get_pods` {#src.cluster.Cluster.get_pods}



    
> `def get_pods(self, filters={})`


Helper function to get pod.

:param filters: Contains the search filets for the API call
                (no parameter given: all pods from all namespaces)
:type filters: dict
:return: List from the pod match for query
:rtype: V1PodList

    
##### Method `get_replica_set` {#src.cluster.Cluster.get_replica_set}



    
> `def get_replica_set(self, filters={})`


Helper fuction to get replica sets.

:param filters: Contains the search filets for the API call
                (no parameter given: all pods from all namespaces)
:type filters: dict, optional
:return: List from replica sets match for query
:rtype: V1ReplicaSetList

    
##### Method `helm_install` {#src.cluster.Cluster.helm_install}



    
> `def helm_install(self, deploy_name='deployment', chart=None, namespace='default', *args, **kwargs)`


Deploy application with Helm

:param deploy_name: Name for Helm deployment, defaults to "deployment"
:type deploy_name: str, optional
:param chart: Specify chart to deploy, defaults to None
:type chart: [type], optional

    
##### Method `helm_tiller_check` {#src.cluster.Cluster.helm_tiller_check}



    
> `def helm_tiller_check(self)`


Check if Helm Tiller pod is given and Running

:return: True if Tiller correct
:rtype: bool

    
##### Method `helm_uninstall` {#src.cluster.Cluster.helm_uninstall}



    
> `def helm_uninstall(self, deploy_name, namespace='default')`


Uninstall a deployment by Helm

:param deploy_name: deployment name used in Helm install
:type deploy_name: str
:param namespace: deployment's nsmespace, defaults to "default"
:type namespace: str, optional
:return: Success of delete
:rtype: bool

    
##### Method `helm_uninstall_all` {#src.cluster.Cluster.helm_uninstall_all}



    
> `def helm_uninstall_all(self)`


Uninstall all deployment was created by the script

:return: Success of delete
:rtype: bool

    
##### Method `prometheus_install_to_server` {#src.cluster.Cluster.prometheus_install_to_server}



    
> `def prometheus_install_to_server(self)`


Install Prometheus to the cluster

    
##### Method `replica_set_status_check` {#src.cluster.Cluster.replica_set_status_check}



    
> `def replica_set_status_check(self, rs)`


Check if the given Replicaset has the desired number of pods.

:param rs: Replicaset to check
:type rs: V1ReplicaSet
:return: Status of the replica set. True if everything works fine.
:rtype: bool

    
##### Method `running_pod_check` {#src.cluster.Cluster.running_pod_check}



    
> `def running_pod_check(self, pod)`


Check the given Pod's status to be Running

:param pod: one pod object 
:type pod: Pod
:return: status of the pod
:rtype: bool

    
##### Method `wait_all_pods_to_run` {#src.cluster.Cluster.wait_all_pods_to_run}



    
> `def wait_all_pods_to_run(self, message='Wait pods to start: ')`


Check all pods in default namespace and status need to be running

:param message: Spinner message, defaults to "Wait pods to start: "
:type message: str, optional

    
##### Method `wait_all_replication_to_desire` {#src.cluster.Cluster.wait_all_replication_to_desire}



    
> `def wait_all_replication_to_desire(self, message='Wait for replica sets: ', namespace='default')`


Check all replicasets and need to be running in the given namespace

:param message: spinner message, defaults to "Wait for replica sets: "
:type message: str, optional
:param namespace: namespace for check, defaults to "default"
:type namespace: str, optional



    
# Module `src.helper` {#src.helper}






    
## Functions


    
### Function `read_config_file` {#src.helper.read_config_file}



    
> `def read_config_file(file_name)`


Setup config parameters
Read and store configuration parameters
from given config file




    
# Module `src.loader` {#src.loader}







    
## Classes


    
### Class `Loader` {#src.loader.Loader}



> `class Loader(cluster, config)`


Initialise to load

:param cluster: cluster to install application
:type cluster: Cluseter
:param config: config parameters from config file
:type config: dictionary







    
#### Methods


    
##### Method `application_install` {#src.loader.Loader.application_install}



    
> `def application_install(self, params={})`


Create and scale the profiling application

:param params: dictionary contains optional settings for application.
:type params: dict, optional

    
##### Method `csv_to_json` {#src.loader.Loader.csv_to_json}



    
> `def csv_to_json(self, response)`


Convert requests object to json to write data to file

:param response: locust response
:type response: requests.response

    
##### Method `locust_install` {#src.loader.Loader.locust_install}



    
> `def locust_install(self)`


Function to install load generator with the given parameters

    
##### Method `locust_load` {#src.loader.Loader.locust_load}



    
> `def locust_load(self, locust_count, settings)`


Create load from Locust and collect datas from the measurement

:param locust_count: number of users to simulate
:type locust_count: int
:param settings: envronment settings: #pods, cpu, memory
:type settings: dictionary

    
##### Method `measure` {#src.loader.Loader.measure}



    
> `def measure(self)`


Do the measurement based on the given parameters from config file

    
##### Method `prometheus_get_statistic` {#src.loader.Loader.prometheus_get_statistic}



    
> `def prometheus_get_statistic(self, start, end)`


Get usage statistic from Prometheus.

:param start: start time for the load
:type start: time
:param end: end time for the load
:type end: time
:return: Cpu and memory usage in the requested time
:rtype: 2 json object

    
##### Method `prometheus_install` {#src.loader.Loader.prometheus_install}



    
> `def prometheus_install(self)`


Function to install Prometheus with the given parameter if need

    
##### Method `write_statisctic` {#src.loader.Loader.write_statisctic}



    
> `def write_statisctic(self, settings, locust, cpu, memory)`


Concatenate the dictionaries, create a new directory and write the results

:param settings: enviroment settings
:type settings: dictionary
:param locust: locust response related info
:type locust: dictionary
:param cpu: cpu usage info from prometheus
:type cpu: dictionary
:param memory: memory usage info from prometheus
:type memory: dictionary



    
# Module `src.main` {#src.main}






    
## Functions


    
### Function `main` {#src.main.main}



    
> `def main(config_file)`


Main function.
This will orchestrate the measurement



-----
Generated by *pdoc* 0.8.1 (<https://pdoc3.github.io>).
