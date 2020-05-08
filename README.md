# Application profiling

Offline profiling applications in Kubernetes cluster. Run more measurements and get efficient scaling information.

## Under refactor
  Will use Python kubernetes client and helm install instead deploy from manually created .yaml files. Hopefully we can use Prometheus offical python libary.

## Usage
1. **Get project**

    Clone the repo: \
    `$ git clone git@github.com:Tutkovics/benchmarking.git` \
    `$ cd benchmarking`

    Install Python requirements: \
    `$ python3 -m venv env` \
    `$ source env/bin/activate  # on linux` \
    `$ pip3 install -r requirements.txt`

    Run the profiling:
    `$ python benchmarking/src/manin.py <config_file.yaml>`

2. **Requirements**
   
  - Has installed Helm.
  - Has a *kubeconfig* file, to target cluster

2. **Environment** 
    - Kubernetes 1.16 (Minikube: v1.4.0)
    - Helm v3.2.0

## Architecture
![UML diagram](https://plantuml.atug.com/svg/dLHBRzim3BxxLwXPW2L0asB33aFX-B2komPaQD5sPq6HwKI8R1bwDCqU_tsKBBjE6dHhUqXDyYFvyIKkcJ7aGZfZGPDV2S4_KHdBf8ISReLTqpN8CkYvqa1PBOB0wjfq0c_yQSLA20fAHIKifQDn58tLdRG2IskLcvweePQ2Csh0HgtFIgr06fhoDV1DNnyPzbMkUav97mrRXiIyobEWLb7jgaDJf6E5gZmY1oCqH50RiTQg1Bi6rzQ1SJ3ToiVTOzoh3Tl0h3Dxvl0Tcaov553PW-eUyxG6Jyc0lWUDa3z9miCCumn8cfOgTnAo33_9wFkfqdmjyZ51nPlFJ6zkWSqrG1MdVVTjiRYyeTTNDtTz-UlLxLqJl0axdNPRSewRK5c6R4WMar-egX2hBqB2fTRABnAwNZvmg7qFIVfxSWY9Zj1Yp8k8O_IUf-TsGE08Hsnn_Oh-y12PtZFfmFGquTEQE6BZf6qqpG5C9fDeORWDJOW2sSMXMb62iCtu8g_992CxLigfOGLGgLYEHJY3ENi0xpVrF_zZQyfUOAJkj3SVdvJmxAbAnN7c_zp8QC0teJkRVKkCuwjw6cGL3qCOAtWqby2C2pVNBRXi2ddXcaGlN97OY2ERKQBqohtOwwfK_OtnuzxR1P-cFNfLrX9ih2_azoDylB0mm4xVKG_g97cx40XZ5d3lSo3VMOt1kLPeEy76SiYnTyJtL-MZeN-LJycmPfgLPZOOZ1FiHWu5ILsMBhDWJy-MMNhcib64ZR5ZoGbKUHTkB_I3Xc8qn7VHOk2DgFBPm0iO-aGKP1HKP3OZ0wESve3wb2kfzFaDv1cc3Qu-NteMz1dcaWRwg0Zfp5KkYYUCXjpNZtcYerOx9Z_XfMQf4J_X_Ds7R11HonuiZ5DY_-QQxLhe-mwwwa6F8vP7SxRMkcUzTXedtQUJS7paSPg5KlxV7AemofmiTsGkx8zIakrsErq9w_0rm4r9_W80)

## Notes
1. **benchmark.py**
  - Was the previous project's main file

2. **Tasks**

- [x] Integrate Kubernetes client
- [x] Integrate Helm client 
- [x] Integrate Prometheus client
- [x] Integrate Locust (loadgenerator)
