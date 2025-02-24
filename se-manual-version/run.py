from kubernetes import client, config
import yaml
import time
import os
import eks_token
import boto3
import tempfile
import base64
from argparse import ArgumentParser, BooleanOptionalAction
from enum import Enum

def load_minikube_config():
    print("loading minikube kubeconfig")
    config.load_kube_config()

    v1 = client.CoreV1Api()
    apps = client.AppsV1Api()

    return v1, apps

def load_aws_config(cluster_name):
    print("loading eks kubeconfig")

    token = eks_token.get_token(cluster_name)

    bclient = boto3.client('eks')
    cluster_data = bclient.describe_cluster(name=cluster_name)['cluster']
    k8s_cafile = _write_cafile(cluster_data['certificateAuthority']['data'])

    kclient = build_k8s_api_client(
        endpoint=cluster_data['endpoint'],
        token=token['status']['token'],
        cafile=k8s_cafile.name
    )

    v1 = client.CoreV1Api(api_client=kclient)
    apps = client.AppsV1Api(api_client=kclient)

    return v1, apps

def build_k8s_api_client(endpoint: str, token: str, cafile: str) -> client.CoreV1Api:
    kconfig = config.kube_config.Configuration(
        host=endpoint,
        api_key={'authorization': 'Bearer ' + token}
    )
    kconfig.ssl_ca_cert = cafile
    kclient = client.ApiClient(configuration=kconfig)

    return kclient

def _write_cafile(data: str) -> tempfile.NamedTemporaryFile:
    cafile = tempfile.NamedTemporaryFile(delete=False)
    cadata_b64 = data
    cadata = base64.b64decode(cadata_b64)
    cafile.write(cadata)
    cafile.flush()

    return cafile

def create_ns(v1, apps):
    with open("ns.yaml") as f:
        ns_yaml = yaml.safe_load(f)
        print("Creating namespace for test execution")
        
        resp = v1.create_namespace(body=ns_yaml)

        for _ in range(20):
            ns = v1.read_namespace_status(name=resp.metadata.name)

            if ns.status.phase != "Active":
                print(f"Namespace is not active yet")
                time.sleep(3)
            else:
                print("Namespace is active")
                break

    return ns.metadata.name

def create_deploy(v1, apps, namespace, test_runner_pod_count):
    with open("firefox-node-deploy.yaml") as f:
        deploy_yaml = yaml.safe_load(f)
        print("Creating selenium node deployment")
        resp = apps.create_namespaced_deployment(body=deploy_yaml, namespace=namespace)

        scale = {"spec": {"replicas": test_runner_pod_count}}
        print("Scaling pod count to", test_runner_pod_count)

        apps.patch_namespaced_deployment_scale(name=resp.metadata.name, namespace=namespace, body=scale)

        for _ in range(20):
            deploy = apps.read_namespaced_deployment_status(name=resp.metadata.name, namespace=namespace)

            if deploy.status.available_replicas != test_runner_pod_count:
                print(f"Deployment available replica count: {deploy.status.available_replicas}, expected: {test_runner_pod_count}")
                time.sleep(5)
            else:
                print("Deployment available replicas reached desired count", test_runner_pod_count)
                break

    return deploy.metadata.name

def create_svc(v1, apps, namespace):
    with open("firefox-node-svc.yaml") as f:
        svc_yaml = yaml.safe_load(f)
        print("Creating selenium node service")
        resp = v1.create_namespaced_service(body=svc_yaml, namespace=namespace)

    return resp.metadata.name

def create_test_pod(v1, apps, namespace):
    with open("test-case-controller.yaml") as f:
        pod_yaml = yaml.safe_load(f)
        print("Creating test case controller pod")
        resp = v1.create_namespaced_pod(body=pod_yaml, namespace=namespace)

        for _ in range(20):
            pod = v1.read_namespaced_pod_status(name=resp.metadata.name, namespace=namespace)

            if pod.status.phase == "Pending":
                print(f"Test execution pod is in pending state")
                time.sleep(2)
                continue
            elif pod.status.phase == "Running":
                print("Running test execution")
                time.sleep(10)
                continue
            elif pod.status.phase == "Succeeded":
                print(f"Test execution succeeded")
                print(f"---------Test Case Controller Logs---------")
                print(v1.read_namespaced_pod_log(name=pod.metadata.name, namespace=namespace))
                print(f"---------Test Case Controller Logs---------")

                started_at = pod.status.container_statuses[0].state.terminated.started_at
                finished_at = pod.status.container_statuses[0].state.terminated.finished_at
                
                time_diff = finished_at - started_at
                print(f"Test execution started at {started_at}, finished at {finished_at}, took {time_diff.total_seconds()} seconds")
                break
            else:
                print("Something went unexpected, please check pod logs")
                break

    return resp.metadata.name

def destroy_env(v1, apps, deploy_name, svc_name, test_case_controller_pod, ns_name):
    print("Deleting deployment", deploy_name)
    apps.delete_namespaced_deployment(name=deploy_name, namespace=ns_name)

    print("Deleting service", svc_name)
    v1.delete_namespaced_service(name=deploy_name, namespace=ns_name)

    print("Deleting test case controller pod", test_case_controller_pod)
    v1.delete_namespaced_pod(name=test_case_controller_pod, namespace=ns_name)

    print("Deleting test namespace", ns_name)
    v1.delete_namespace(name=ns_name)

class K8SProvider(Enum):
    eks = 'eks'
    local = 'local'

    def __str__(self):
        return self.value

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-p", "--k8s-provider", help="k8s provider to choose. options: local, eks. default is local",
                        type=K8SProvider, choices=list(K8SProvider), default=K8SProvider.local)
    parser.add_argument("-n", "--k8s-cluster-name", help="k8s cluster name", default="selenium-demo")
    parser.add_argument("-c", "--node-count", help="test runner node count. e.g. 3. default is 1", type=int, default=1)
    parser.add_argument("-d", "--auto-delete", help="automatically delete namespace used for test execution.", action=BooleanOptionalAction, default=False)
    
    args = parser.parse_args()

    if args.k8s_provider == K8SProvider.eks:
        v1, apps = load_aws_config(args.k8s_cluster_name)
    else:
        v1, apps = load_minikube_config()

    ns_name = create_ns(v1, apps)
    svc_name = create_svc(v1, apps, ns_name)
    deploy_name = create_deploy(v1, apps, ns_name, args.node_count)
    test_case_controller_pod = create_test_pod(v1, apps, ns_name)

    if args.auto_delete:
        destroy_env(v1, apps, deploy_name, svc_name, test_case_controller_pod, ns_name)
