# Selenium Grid Deployment with helm chart

Selenium Grid Helm chart eases deployment of distributed Selenium Grid server in k8s

## Install Selenium Grid and run tests

1. Install Selenium Grid via helm chart
```shell
helm repo add docker-selenium https://www.selenium.dev/docker-selenium
helm repo update
helm upgrade --install selenium-grid docker-selenium/selenium-grid -n se-grid --create-namespace -f values.yaml
```

2. Run tests
```shell
kubectl apply -f run-tests.yaml
```
K8S Job will be created and will run to completion. You can check logs later

3. Destroy
```shell
helm uninstall selenium-grid -n se-grid
kubectl delete ns se-grid
```