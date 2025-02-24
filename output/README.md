# Output

## EKS is ready
![Empty EKS](image-4.png)

## Running tests
![Run logs](image.png)

## Logs from pods. Note that 2 of tests was run by the same container(because how k8s internal loadbalancing works, we can't assure requests will be equally distributed)
![Kubectl logs](image-2.png)
![Test Case Controller logs](image-1.png)
![Test Runner logs](image-3.png)
