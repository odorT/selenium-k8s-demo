# Test execution in K8S with selenium test case controller and runner pods

## Test Case Controller pod
This pod is responsible for executing tests using [testcase image](../testcase/Dockerfile). Selenium test runner pods endpoints are passed via environment variable (check [pod config](./test-case-controller.yaml)). We rely on kubernetes service loadbalancing to distribute tests across selenium nodes (not always works as expected though).


## Selenium Test Runner pod
I mainly used firefox webdriver for testing, but chrome pod should also work if your CPU arch is amd64(chrome node container does not support arm). This version runs selenium node without separate grid hub server(in standalone mode, everything in one instance).

### Selenium Test Runner container images
```shell
VERSION=v0.2 && docker build -t odort/selenium-k8s-demo:firefox-runner-node-$VERSION -f firefox-runner-node.Dockerfile . && docker push odort/selenium-k8s-demo:firefox-runner-node-$VERSION
VERSION=v0.2 && docker build -t odort/selenium-k8s-demo:chrome-runner-node-$VERSION -f chrome-runner-node.Dockerfile . && docker push odort/selenium-k8s-demo:chrome-runner-node-$VERSION
```


## Running tests locally with minikube (any other k8s distro should work, e.g. kind, k3s)

1. Start k8s
```shell
minikube start
```

2. Prepare venv and install dependencies
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Execute tests
```shell
python run.py -h
```
```shell
usage: run.py [-h] [-p {eks,local}] [-n K8S_CLUSTER_NAME] [-c NODE_COUNT] [-d | --auto-delete | --no-auto-delete]

optional arguments:
  -h, --help            show this help message and exit
  -p {eks,local}, --k8s-provider {eks,local}
                        k8s provider to choose. options: local, eks. default is local
  -n K8S_CLUSTER_NAME, --k8s-cluster-name K8S_CLUSTER_NAME
                        k8s cluster name
  -c NODE_COUNT, --node-count NODE_COUNT
                        test runner node count. e.g. 3. default is 1
  -d, --auto-delete, --no-auto-delete
                        automatically delete namespace used for test execution. (default: False)
```

```shell
python run.py -p local -c 3
```

[run.py](./run.py) is a wrapper script around k8s api which:
1. Uses different strategies for k8s authentication (different approach for EKS) 
2. Applies k8s manifests(test namespace, test controller pod, test runner deployment and service). Note that it explicitly waits until all test runner pods are active(matching desired NODE_COUNT param)
3. Waits until test controller pod finishes test execution. After successful execution, prints logs to stdout
4. Destroys namespace if --auto-delete param is true


## Running tests in EKS

1. Prepare EKS and make sure that API server is accessible, aws cli and kubectl is configured properly

2. Prepare venv and install dependencies
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Execute tests
```shell
python run.py -p eks -n selenium-demo -c 3
```
