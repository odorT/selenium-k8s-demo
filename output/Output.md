# Output

## EKS is ready
![Empty EKS](image.png)

## Running tests
![Part 1](image-1.png)
![Part 2](image-2.png)

## Logs from pods. Note that 2 of tests was run by the same container(because how k8s internal loadbalancing works, we can't assure requests will be equally distributed)
![Kubectl logs](image-3.png)
![Test Case Controller logs](image-4.png)
![Test Runner #1 logs](image-5.png)
![Test Runner #2 logs](image-6.png)
![Test Runner #3 logs](image-7.png)
