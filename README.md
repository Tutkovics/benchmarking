# Application profiling

Offline profiling applications in Kubernetes cluster. Run more measurements and get efficient scaling information.

## Under refactor
  Will use Python kubernetes client and helm install instead deploy from manually created .yaml files. Hopefully we can use Prometheus offical python libary.

## Usage
1. **Get project**
  Clone the repo:
  `$ git clone git@github.com:Tutkovics/benchmarking.git`

  Install Python requirements:
  `$ pip3 install -r requirements.txt`

  Run the profiling:
  `$ python benchmarking/src/manin.py <config_file.yaml>`

2. **Cluster requirements**
  - Kubernetes cluster
    - Kubernetes 1.16
    
  - Has installed Helm.
    - Helm v3.2.0
  
  - Develop environment:
    - Minikube: v1.4.0

## Notes
1. **benchmark.py**
  - Was the previous project's main file

2. **Tasks**
  - [x] Integrate Kubernetes client
  - [x] Integrate Helm client 
  - [] Integrate Prometheus client
  - [] Integrate Locust (loadgenerator)
  
