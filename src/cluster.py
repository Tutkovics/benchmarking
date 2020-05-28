from kubernetes import client, config
from kubernetes.client.rest import ApiException
from time import sleep
from progress.spinner import Spinner
from os import system
from pprint import pprint

# https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md


class Cluster():
    """This class represent one Kubernetes cluster
    """

    def __init__(self, name, config_f):
        """Initialise cluster. Check and setup client and cluster

        :param name: This will represent the cluster
        :type name: string
        """
        # initialise variables
        self.installed_with_helm = {}  # store installed charts to easy clean cluster
        self.config = config_f           # get config parameters from config file
        self.cluster_name = name       # just for fun

        # load kube config to client
        config.load_kube_config()      # default: .kube/config
        self.core_api = client.CoreV1Api()
        self.apps_api = client.AppsV1Api()

        # check if can use Helm (from commandline)
        self.check_helm_client_install()

        # check if need to install Prometheus
        if self.config["prometheus_deploy"] == "True":
            self.prometheus_install_to_server()


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
        #NOTE: not used function, because Helm 3 not required Tiller
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
        self.wait_all_replication_to_desire("Helm install (" + deploy_name + ") : ", namespace)


    def helm_uninstall(self, deploy_name, namespace="default"):
        """Uninstall a deployment by Helm

        :param deploy_name: deployment name used in Helm install
        :type deploy_name: str
        :param namespace: deployment's nsmespace, defaults to "default"
        :type namespace: str, optional
        :return: Success of delete
        :rtype: bool
        """
        response = system("helm uninstall " + deploy_name + " -n " + namespace)

        if response != 0:
            print("Can't delete [" + deploy_name + "] deployment.")
            return False

        self.wait_all_pods_to_run("Delete deployment: ")
        return True


    def helm_uninstall_all(self):
        """Uninstall all deployment was created by the script

        :return: Success of delete
        :rtype: bool
        """
        success = True
        items = self.installed_with_helm.items()

        for app, namespace in items:
            if not self.helm_uninstall(app, namespace):
                success = False

        self.installed_with_helm.clear()
        return success


    def wait_all_pods_to_run(self, message="Wait pods to start: "):
        """Check all pods in default namespace and status need to be running

        :param message: Spinner message, defaults to "Wait pods to start: "
        :type message: str, optional
        """
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


    def wait_all_replication_to_desire(self, message="Wait for replica sets: ", namespace="default"):
        """Check all replicasets and need to be running in the given namespace

        :param message: spinner message, defaults to "Wait for replica sets: "
        :type message: str, optional
        :param namespace: namespace for check, defaults to "default"
        :type namespace: str, optional
        """
        filter = {"watch": False, "namespace": namespace}
        need_wait = True
        spinner = Spinner(message)
        while(need_wait):
            for i in range(15):
                spinner.next()
                sleep(0.2)

            need_wait = False
            # Can't use filter because can't get replicasets from specific namespace
            api_response = self.get_replica_set()
            
            for rs in api_response.items:
                if not self.replica_set_status_check(rs):
                    need_wait = True
        print()


    def running_pod_check(self, pod):
        """Check the given Pod's status to be Running

        :param pod: one pod object 
        :type pod: Pod
        :return: status of the pod
        :rtype: bool
        """
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

        if not rs.status.replicas == 0:  # filter already not used replicasets
            if not rs.status.replicas == rs.status.ready_replicas:
                # print("WAIT: " + rs.metadata.name + "--> " + "(" + str(rs.status.replicas) + "/" + str(rs.status.ready_replicas) +")" )
                return False
        
        return True


    def check_helm_client_install(self):
        """Check if installed helm command can used

        :return: success of helm command
        :rtype: bool
        """
        if not system("helm version --short > /dev/null") == 0:
            raise "Are you sure have installed Helm?"
        return True

    
    def prometheus_install_to_server(self):
        """Install Prometheus to the cluster
        """
        # namespace in kubernetes need to exist
        self.helm_install(
            self.config["prometheus_name"],
            self.config["prometheus_repo"],
            self.config["prometheus_namespace"],
            self.config["prometheus_options"],
        )
