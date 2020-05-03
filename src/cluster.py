from kubernetes import client, config
from kubernetes.client.rest import ApiException
from time import sleep
from progress.spinner import Spinner
from os import system
#from pyhelm.chartbuilder import ChartBuilder
#from pyhelm.tiller import Tiller
# from helper import timeit
from pprint import pprint
# import json

# install loadgenerator
# get data from

# https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md
TILLER_PORT = 44134
TILLER_HOST = "127.0.0.1"

class Cluster():
    """This class represent one Kubernetes cluster
    """

    def __init__(self, name):
        """Initialise cluster. Check and setup client and cluster

        :param name: This will represent the cluster
        :type name: string
        """
        # initialise variables
        self.installed_with_helm = {}  # store installed charts to easy clean cluster

        # load kube config to client
        config.load_kube_config()
        self.core_api = client.CoreV1Api()
        self.apps_api = client.AppsV1Api()
        self.cluster_name = name

        # check if cluster has installed Helm
        self.check_helm_client_install()
        # self.prometheus_install_to_server()

        # Helm 3 doesn't need tho have deployed tiller pod
        #self.tiller_pod = self.helm_tiller_check()


    def __str__(self):
        """Convert Cluster object to string when need to print.

        :return: cluster name
        :rtype: string
        """
        return self.cluster_name


    def get_pods(self, filters={}):
        """Helper function to get pod.

        :param filters: Contains the search filets for the API call
                        (no parameter given: all pods from all namespaces)
        :type filters: dict
        :return: List from the pod match for query
        :rtype: V1PodList
        """

        # note: maximum 56 items will give
        try:
            api_response = self.core_api.list_pod_for_all_namespaces(**filters)
            return api_response
        except ApiException as e:
            raise("Exception when calling 'get_pods': %s\n" % e)


    def get_replica_set(self, filters={}):
        """Helper fuction to get replica sets.

        :param filters: Contains the search filets for the API call
                        (no parameter given: all pods from all namespaces)
        :type filters: dict, optional
        :return: List from replica sets match for query
        :rtype: V1ReplicaSetList
        """
        try:
            api_response = self.apps_api.list_replica_set_for_all_namespaces(**filters)
            return api_response
        except ApiException as e:
            raise("Exception when calling AppsV1Api->list_replica_set_for_all_namespaces: %s\n" % e)


    def helm_tiller_check(self):
        """Check if Helm Tiller pod is given and Running

        :return: True if Tiller correct
        :rtype: bool
        """

        filter = {"watch": False, "label_selector": "app=helm,name=tiller"}
        api_response = self.get_pods(filter)

        pods = api_response.items

        # if we get exactly one pod
        if not len(pods) == 1:
            raise("Tiller pod not found (or ambiguous)! \
                   pod need to have following labels: {app=helm,name=tiller}")
        # and the pod is running
        elif not self.running_pod_check(pods[0]):
            raise("Helm Tiller pod exists but not running...")
        else:
            return pods[0]


    def helm_install(self, deploy_name="deployment", chart=None, namespace="default", *args, **kwargs):
        """Deploy application with Helm

        :param deploy_name: Name for Helm deployment, defaults to "deployment"
        :type deploy_name: str, optional
        :param chart: Specify chart to deploy, defaults to None
        :type chart: [type], optional
        """

        config_arguments = ""
        for element in args:
            for key, value in element.items():
                config_arguments += " --set " + str(key) + "=" + str(value)
            #config_arguments += str("--set" + element + "=" + kwargs)
            
        command = "helm upgrade --install --output json --namespace " + namespace + " " + \
                   config_arguments + " " + \
                   deploy_name + " " + \
                   chart + " > ../tmp/helm.json"
        

        print(command)  # for debug
        if not system(command) == 0:
            print("Unable install Helm repo: " + str(chart))
            return
        
        self.installed_with_helm[deploy_name] = namespace

        print(self.installed_with_helm)

        # in horizontal scale add now pod
        self.wait_all_replication_to_desire("Helm install (" + deploy_name + ") : ")


    def helm_uninstall(self, deploy_name="deployment", namespace="default"):
        response = system("helm uninstall " + deploy_name + " -n " + namespace)

        if response != 0:
            print("Can't delete [" + deploy_name + "] deployment.")
            return False
        
        # self.installed_with_helm().pop(deploy_name)

        self.wait_all_pods_to_run("Delete deployment: ")
        return True


    def helm_uninstall_all(self):
        success = True
        items = self.installed_with_helm.items()

        for app, namespace in items:
            if not self.helm_uninstall(app, namespace):
                success = False

        self.installed_with_helm.clear()
        return success


    def wait_all_pods_to_run(self, message="Wait pods to start: "):
        need_wait = True
        spinner = Spinner(message)
        while(need_wait):
            for i in range(15):
                spinner.next()
                sleep(0.2)

            need_wait = False
            api_response = self.get_pods()

            for pod in api_response.items:
                if not self.running_pod_check(pod):
                    need_wait = True
        print()

    
    def wait_all_replication_to_desire(self, message="Wait for replica sets: "):
        filter = {"watch": False, "namespace": "default"}
        need_wait = True
        spinner = Spinner(message)
        while(need_wait):
            for i in range(15):
                spinner.next()
                sleep(0.2)

            need_wait = False
            api_response = self.get_replica_set()
            
            for rs in api_response.items:
                if not self.replica_set_status_check(rs):
                    need_wait = True
        print()


    def install_prometheus(self):
        pass


    def running_pod_check(self, pod):
        if pod.status.phase == "Running":
            return True
        return False


    def replica_set_status_check(self, rs):
        """Check if the given Replicaset has the desired number of pods.

        :param rs: Replicaset to check
        :type rs: V1ReplicaSet
        :return: Status of the replica set. True if everything works fine.
        :rtype: bool
        """
        # print(rs.metadata.name + "--> " + "(" \
        #         + str(rs.status.replicas) + "/" \
        #         + str(rs.status.ready_replicas) + "/" \
        #         + str(rs.status.fully_labeled_replicas) + "/" \
        #         + str(rs.status.available_replicas) +")" 
        # )
        if not rs.status.replicas == 0:  # filter already not used replicasets
            if not rs.status.replicas == rs.status.ready_replicas:
                # print("WAIT: " + rs.metadata.name + "--> " + "(" + str(rs.status.replicas) + "/" + str(rs.status.ready_replicas) +")" )
                return False
        
        return True


    def check_helm_client_install(self):
        if not system("helm version --short > /dev/null") == 0:
            raise "Are you sure have installed Helm?"
        return True

    
    def prometheus_install_to_server(self):
        # namespace ins kubernetes need to exist
        self.helm_install("prometheus", "stable/prometheus", "metrics", {"server.service.type": "NodePort",
                        "server.service.nodePort": "30000"})
