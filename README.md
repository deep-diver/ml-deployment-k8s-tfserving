# Deploying ML models with TFServing, Docker, and Kubernetes

*By: [Chansung Park](https://github.com/deep-diver) and [Sayak Paul](https://github.com/sayakpaul)*

This project shows how to serve a TensorFlow image classification model as RESTful and **gRPC** based service with **TFServing**, Docker, and Kubernetes.
The idea is to first create a custom TFServing docker image with a TensorFlow model, and then deploy it on a k8s cluster running on [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine). Also we are using [GitHub Actions](https://github.com/features/actions) to automate all the procedures when a new TensorFlow model is released. 

👋 **Note**
- Even though this project uses an image classification its structure and techniques can be used to serve other models as well.
- There is a counter part project using FastAPI instead of TFServing. If you wonder from how to convert TensorFlow model to ONNX optimized model to deploy it on k8s cluster, check out the [this repo](https://github.com/sayakpaul/ml-deployment-k8s-fastapi).

## Deploying the model as a service with k8s

- [Prerequisites](./prerequisites.md): Doing anything beforehand, you have to create GKE cluster and service accounts with appropriate roles. Also, you need to grasp GCP credentials to access any GCP resources in GitHub Action. Please check out the more detailed information [here](./prerequisites.md)

- To deploy a custom TFServing docker image, we define [`deployment.yml`](https://github.com/deep-diver/ml-deployment-k8s-tfserving/blob/main/.github/workflows/deployment.yml) workflow file which is is only triggered when there is a new release for the current repository. It is subdivided into three parts to do the following tasks:
    - [First subtask](https://github.com/deep-diver/ml-deployment-k8s-tfserving/blob/main/.github/actions/setup/action.yml) handles the environmental setup.
        - GCP Authentication (GCP credential has to be provided in [GitHub Secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets))
        - Install gcloud CLI toolkit
        - Authenticate Docker to push images to GCR(Google Cloud Registry)
        - Connect to the designated GKE cluster
    - [Second subtask](https://github.com/deep-diver/ml-deployment-k8s-tfserving/blob/main/.github/actions/build/action.yml) handles building a custom TFServing image.
        - Download and extract the latest released model from the current repository
        - Run the CPU optimized TFServing image which is compiled from the source code (FYI. image tag is `gcr.io/gcp-ml-172005/tfs-resnet-cpu-opt`, and it is publicly available)
        - Copy the extracted model into the running container
        - Commit the changes of the running container and give it a new image name
        - Push the commited image
    - [Third subtask](https://github.com/deep-diver/ml-deployment-k8s-tfserving/blob/main/.github/actions/provision/action.yml) handles deploying the custom TFServing image to GKE cluster.
        - Pick a one of the scenarios from a various [experiments](https://github.com/deep-diver/ml-deployment-k8s-tfserving/tree/main/.kube/experiments)
        - Download [Kustomize](https://kustomize.io) toolkit to handle overlay configurations.
        - Update image tag with the currently built one with Kustomize
        - By provisioning `Deployment`, `Service`, and `ConfigMap`, the custom TFServing image gets deployed.
            - 👋 **NOTE**: `ConfigMap` is only used for batching enabled scenarios to inject batching configurations dynamically into the `Deployment`.

If the entire workflow goes without any errors, you will see something silimar to the text below. As you see, two external interfaces(8500 for RESTful, 8501 for gRPC) are exposed.
```shell
NAME             TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)                          AGE
tfs-server       LoadBalancer   xxxxxxxxxx     xxxxxxxxxx      8500:30869/TCP,8501:31469/TCP    23m
kubernetes       ClusterIP      xxxxxxxxxx     <none>          443/TCP                         160m
```

## Load testing

We used [Locust](https://locust.io/) to conduct load tests for both TFServing and FastAPI. Below is the results for TFServing(gRPC) on a various setups, and you can find out the result for FastAPI(RESTful) in a [separate repo](https://github.com/sayakpaul/ml-deployment-k8s-fastapi). For specific instructions about how to install Locust and run a load test, follow [this separate document](./locust/README.md).

👋 **NOTE**
- Locust doesnt' have a built-in support to write a gRPC based client, so we have written one for ourselves. If you are curious about the implementation, check [this locustfile.py](./locust/locustfile.py) out.
- For the legend in the plot, `n` means the number of nodes(pods), `c` means the number of CPU cores, `r` means the RAM capacity, `interop` means the number of [`--tensorflow_inter_op_parallelism`](https://github.com/tensorflow/serving/blob/b5a11f1e5388c9985a6fc56a58c3421e5f78149f/tensorflow_serving/model_servers/main.cc#L147), and `batch` means the batching configuration is enabled with this [config](https://github.com/deep-diver/ml-deployment-k8s-tfserving/blob/main/.kube/experiments/8vCPU%2B64GB%2Binter_op2_w_batch/tfs-config.yaml).

![](https://i.ibb.co/SBpbGvB/tfserving-load-test.png)

From the results above, we see TFServing focuses more on **reliability** than performance(in terms of throughput). In any cases, no failures are observed, and the the response time is consistent. Also as stated in the [official document](https://www.tensorflow.org/tfx/serving/performance#3_the_server_hardware_binary), TFServing shows a better performance when it is deployed on fewer, larger(CPU, RAM) machines. However, there is a cost tradeoff, so our recommendation from the experiment is to choose `2n-8c-16r-interop4` configuration unless you care about dynamic batching capabilities. Or you can write a similar setup by referencing `2n-8c-64r-interop2-batch` but for smaller machines as well. 

## Acknowledgements

[ML-GDE program](https://developers.google.com/programs/experts/) for providing GCP credit support.

