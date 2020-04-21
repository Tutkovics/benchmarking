from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pyhelm.chartbuilder import ChartBuilder
from pyhelm.tiller import Tiller
# from helper import timeit
# from pprint import pprint
# import json

# install prometheus
# install application
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
        # load kube config to client
        config.load_kube_config()
        self.core_api = client.CoreV1Api()
        self.cluster_name = name

        # check if cluster has installed Helm
        self.tiller_pod = self.helm_tiller_check()

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

    def helm_install(self, chart=None):
        # resp = self.core_api.connect_get_namespaced_pod_portforward(
        #     self.tiller_pod.metadata.name, self.tiller_pod.metadata.namespace,
        #     ports=TILLER_PORT,
        #     _request_timeout=60,
        #     _preload_content=False
        # )

        tiller = Tiller(TILLER_HOST)
        chart = ChartBuilder({"name": "nginx-ingress", "source": {"type": "repo", "location": "https://kubernetes-charts.storage.googleapis.com"}})
        # print("Copy chart: " + chart)
        tiller.install_release(chart.get_helm_chart(), dry_run=False, namespace='default')

        print(resp)

    def install_prometheus(self):
        pass

    def install_app(self):
        pass

    def running_pod_check(self, pod):
        if pod.status.phase == "Running":
            return True
        return False
