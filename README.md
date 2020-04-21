# Application profiling

Offline profiling applications in Kubernetes cluster. Run more measurements and get efficient scaling information.

## Under refactor
  Will use Python kubernetes client and helm install instead deploy from manually created .yaml files. Hopefully we can use Prometheus offical python libary.

## Usage
1. **Get project**
  Clone the repo:
  `git clone git@github.com:Tutkovics/benchmarking.git`

  Install Python requirements:
  `pip3 install -r requirements.txt`

  Run the profiling:
  `python manin.py <config_file.yaml>`

2. **Cluster requirements**
  - Has installed Helm Tiller pod. (only one exists) 
    - pod labels: `{app=helm,name=tiller}`
  
  - Develop environment:
    - Minikube: v1.4.0

## Notes
1. **benchmark.py**
  - Was the previous project's main file

2. **Tasks**
  - [x] Integrate Kubernetes client
  - [] Integrate Helm client 
  - [] Integrate Prometheus client
  - [] Integrate Locust (loadgenerator)
  
