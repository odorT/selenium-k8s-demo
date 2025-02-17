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
pip install kubernetes boto3 eks-token
```

3. Execute tests
```shell
python run.py
```
[run.py](./run.py) is a wrapper script around k8s api which:
1. Uses different strategies for k8s authentication (different approach for EKS) 
2. Applies k8s manifests(test namespace, test controller pod, test runner deployment and service)
3. Waits until test controller pod finishes test execution. After successful execution, prints logs to stdout
4. Destroys namespace


## Running tests in EKS

1. Prepare EKS and make sure that API server is accessible, aws cli and kubectl is configured properly

2. Prepare venv and install dependencies
```shell
python3 -m venv venv
source venv/bin/activate
pip install kubernetes boto3 eks-token
```

3. Execute tests
```shell
export K8S_PROVIDER=EKS
export K8S_CLUSTER_NAME=selenium-demo
python run.py
```


## Additional notes
`test_runner_pod_count` variable in run.py controls how many selenium test runner pods will be created