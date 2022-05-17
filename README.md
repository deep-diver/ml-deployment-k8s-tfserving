# Deploying ML models with TFServing, Docker, and Kubernetes

*By: [Chansung Park](https://github.com/deep-diver) and [Sayak Paul](https://github.com/sayakpaul)*

This project shows how to serve a TensorFlow image classification model as RESTful and **gRPC** based service with **TFServing**, Docker, and Kubernetes.
The idea is to first create a custom TFServing docker image with a TensorFlow model, and then deploy it on a k8s cluster running on [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine). Also we are using [GitHub Actions](https://github.com/features/actions) to automate all the procedures when a new TensorFlow model is released. 

👋 **Note**
- Even though this project uses an image classification its structure and techniques can be used to serve other models as well.
- There is a counter part project using FastAPI instead of TFServing. If you wonder from how to convert TensorFlow model to ONNX optimized model to deploy it on k8s cluster, please check out the [this repo](https://github.com/sayakpaul/ml-deployment-k8s-fastapi).

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
        - Run the CPU optimized TFServing image which is compiled from the source code (FYI. image tag is `gcr.io/gcp-ml-172005/tfs-resnet-cpu-opt`)
        - Copy the extracted model into the running container
        - Commit the changes of the running container and give it a new image name
        - Push the commited image
    - [Third subtask](https://github.com/deep-diver/ml-deployment-k8s-tfserving/blob/main/.github/actions/provision/action.yml) handles deploying the custom TFServing image to GKE cluster.
        - Pick a one of the scenarios from a various [experiments](https://github.com/deep-diver/ml-deployment-k8s-tfserving/tree/main/.kube/experiments)
        - Download [Kustomize](https://kustomize.io) toolkit to handle overlay configurations.
        - Update image tag with the currently built one with Kustomize
        - By provisioning `Deployment`, `Service`, and `ConfigMap`, the custom TFServing image gets deployed.
            - NOTE: `ConfigMap` is only used for batching enabled scenarios to inject batching configurations dynamically into the `Deployment`.

If the entire workflow goes without any errors, you will see something silimar to the text below. As you see, two external interfaces(8500 for RESTful, 8501 for gRPC).
```shell
NAME             TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)                          AGE
tfs-server       LoadBalancer   xxxxxxxxxx     xxxxxxxxxx      8500:30869/TCP,8501:31469/TCP    23m
kubernetes       ClusterIP      xxxxxxxxxx     <none>          443/TCP                         160m

## Load testing



## Acknowledgements

[ML-GDE program](https://developers.google.com/programs/experts/) for providing GCP credit support.

