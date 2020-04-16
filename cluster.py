from kubernetes import client, config
from helper import timeit
from pprint import pprint

class Cluster():
    """This class represent one Kubernetes cluster
    """


    def __init__(self, name): 
        config.load_kube_config()
        self.core_api = client.CoreV1Api()
        self.cluster_name = name

        self.check_helm()

    def get_name(self):
        print(self.cluster_name)

    def get_all_pods(self):
        return self.core_api.list_pod_for_all_namespaces(watch=False)

    def get_all_nodes(self):
        try:
            api_response = self.core_api.list_node(pretty=True, timeout_seconds=15, watch=False)
            #pprint(api_response)
            return api_response
        except client.rest.ApiException as e:
            print("Exception when calling CoreV1Api->list_node: %s\n" % e)
    
    def check_helm(self):
        pods = self.core_api.list_pod_for_all_namespaces(watch=False, label_selector="app=helm,name=tiller")
        print(pods)
        

    def install_prometheus():
        pass

    def install_app():
        pass

#
 #   install prometheus
  #  install application
   # install loadgenerator
    #get data from 
    