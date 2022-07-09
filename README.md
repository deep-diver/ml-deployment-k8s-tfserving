# Deploying ML models with CPU based TFServing, Docker, and Kubernetes

*By: [Chansung Park](https://github.com/deep-diver) and [Sayak Paul](https://github.com/sayakpaul)*

<div align="center">
<img src="https://i.ibb.co/qBZMNFg/Screen-Shot-2022-07-09-at-9-26-47-AM.png" width="60%"/><br>
<sup>Figure developed by Chansung Park</sup>
</div>

This project shows how to serve a TensorFlow image classification model as RESTful and **gRPC** based services with **TFServing**, Docker, and Kubernetes. The idea is to first create a custom TFServing docker image with a TensorFlow model, and then deploy it on a k8s cluster running on [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine). We are particularly interested in deploying the model as **a gRPC endpoint with TF Serving on a k8s cluster using GKE** and also with [GitHub Actions](https://github.com/features/actions) to automate all the procedures when a new TensorFlow model is released.


👋 **NOTE**
- Even though this project uses an image classification its structure and techniques can be used to serve other models as well.
- There is a counter part of this project that uses FastAPI instead of TFServing. It shows how to convert a TensorFlow model to an ONNX optimized model and deploy it on a k8s cluster, check out the [this repo](https://github.com/sayakpaul/ml-deployment-k8s-fastapi).

## Deploying the model as a service with k8s

- [Prerequisites](./prerequisites.md): Doing anything beforehand, you have to create GKE cluster and service accounts with appropriate roles. Also, you need to grasp GCP credentials to access any GCP resources in GitHub Action. Please check out the more detailed information [here](./prerequisites.md).

```mermaid
flowchart LR
    A[First: Environmental Setup]-->B;
    B[Second: Build TFServing Image]-->C[Third: Deploy on GKE];
```

- To deploy a custom TFServing Docker image, we define [`deployment.yml`](https://github.com/deep-diver/ml-deployment-k8s-tfserving/blob/main/.github/workflows/deployment.yml) workflow file which is is only triggered when there is a new release for the current repository. It is subdivided into three parts to do the following tasks:
    - [First subtask](https://github.com/deep-diver/ml-deployment-k8s-tfserving/blob/main/.github/actions/setup/action.yml) handles the environmental setup.
        - GCP Authentication (GCP credential has to be provided in [GitHub Secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets))
        - Install `gcloud` CLI toolkit
        - Authenticate Docker to push images to GCR (Google Cloud Registry)
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
            - **NOTE**: `ConfigMap` is only used for batching enabled scenarios to inject batching configurations dynamically into the `Deployment`.
    - In order to use this repo for your own purpose, please read [this document](https://github.com/deep-diver/ml-deployment-k8s-tfserving/blob/main/how_to_setup.md) to know what environment variables have to be set.

If the entire workflow goes without any errors, you will see something silimar to the text below. As you see, two external interfaces(8500 for RESTful, 8501 for gRPC) are exposed. You can check out the complete logs in the [past runs](https://github.com/deep-diver/ml-deployment-k8s-tfserving/runs/6473365174?check_suite_focus=true).

```shell
NAME             TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)                          AGE
tfs-server       LoadBalancer   xxxxxxxxxx     xxxxxxxxxx      8500:30869/TCP,8501:31469/TCP    23m
kubernetes       ClusterIP      xxxxxxxxxx     <none>          443/TCP                         160m
```

## How to perform gRPC inference 

If you wonder how to perform gRPC inference, [grpc_client.py](https://github.com/deep-diver/ml-deployment-k8s-tfserving/tree/main/client_grpc_client.py) provides code to perform inference with the gRPC client ([grpc_client.py](https://github.com/deep-diver/ml-deployment-k8s-tfserving/tree/main/client_grpc_client.py) contains `$ENDPOINT` placeholder. To replace it with your own endpoint, you can `envsubst < grpc_client.py > grpc_client.py` after defining `ENDPOINT` environment variable). [TFServing API](https://github.com/tensorflow/serving/tree/master/tensorflow_serving/example) provides handy features to construct protobuf request message via `predict_pb2.PredictRequest()`, and `tf.make_tensor_proto(image)` creates protobuf compatible values from `Tensor` data type.

## Load testing

We used [Locust](https://locust.io/) to conduct load tests for both TFServing and FastAPI. Below is the results for TFServing (gRPC) on a various setups, and you can find out the result for FastAPI (RESTful) in a [separate repo](https://github.com/sayakpaul/ml-deployment-k8s-fastapi). For specific instructions about how to install Locust and run a load test, follow [this separate document](./locust/README.md).

### Hypothesis

<details>

- This is a follow-up project after [ONNX optimized FastAPI deployment](https://github.com/sayakpaul/ml-deployment-k8s-fastapi), so we wanted to know how CPU optimized TensorFlow runtime could be compared to ONNX based one.
- TFServing's [objective](https://www.tensorflow.org/tfx/serving/performance) is to maximize throughput while keeping tail-latency below certain bounds. We wanted to see if this is true, how reliably it provides a good throughput performance and how much throughput is sacrified to keep the reliability. 
- According to the [TFServing's official document](https://www.tensorflow.org/tfx/serving/performance#3_the_server_hardware_binary), TFServing can achieve the best performance when it is deployed on fewer, larger (in terms of CPU, RAM) machines. We wanted to estimate how large of machine and how many nodes are enough. For this, we have prepared a set of different setups in combination of (# of nodes + # of CPU cores + RAM capacity).
- TFServing has a number of [configurable options](https://github.com/tensorflow/serving/blob/b5a11f1e5388c9985a6fc56a58c3421e5f78149f/tensorflow_serving/model_servers/main.cc) to tune the performance. Especially, we wanted to find out how different values of [`--tensorflow_inter_op_parallelism`](https://github.com/tensorflow/serving/blob/b5a11f1e5388c9985a6fc56a58c3421e5f78149f/tensorflow_serving/model_servers/main.cc#L147), [`--tensorflow_intra_op_parallelism`](https://github.com/tensorflow/serving/blob/b5a11f1e5388c9985a6fc56a58c3421e5f78149f/tensorflow_serving/model_servers/main.cc#L141), and [`--enable_batching`](https://github.com/tensorflow/serving/blob/b5a11f1e5388c9985a6fc56a58c3421e5f78149f/tensorflow_serving/model_servers/main.cc#L75) options gives different results. 

</details>    
    
![](https://i.ibb.co/SBpbGvB/tfserving-load-test.png)

![](https://i.ibb.co/vjjb5kW/download-1.png)
    
### Conclusion

<details>

From the results above, 

- TFServing focuses more on **reliability** than performance(in terms of throughput). In any cases, no failures are observed, and the the response time is consistent. 
- Req/s is lower than ONNX optimized FastAPI deployment, so it sacrifies some performance to achieve reliability. However, you need to notice that TFServing comes with lots of built-in features which are required in most of ML serving scenarios such as multi model serving, dynamic batching, model versioning, and so on. Those features possibly make TFServing heavier than simple FastAPI server.
    - **NOTE**: We spawned requests every seconds to clearly see how TFServing behaves with the increasing number of clients. So you can assume that the Req/s doesn't reflect the real world situation where clients try to send requests in any time.
- 8vCPU + 16GB RAM seems like large enough machine. At least bigger size of RAM doesn't help much. We might achieve better performance if we increase the number of CPU core than 8, but beyond 8 cores is somewhat costly.
- In any cases, the optimal value of [`--tensorflow_inter_op_parallelism`](https://github.com/tensorflow/serving/blob/b5a11f1e5388c9985a6fc56a58c3421e5f78149f/tensorflow_serving/model_servers/main.cc#L147) seems like 4. The value of [`--tensorflow_intra_op_parallelism`](https://github.com/tensorflow/serving/blob/b5a11f1e5388c9985a6fc56a58c3421e5f78149f/tensorflow_serving/model_servers/main.cc#L141) is fixed to the number of CPU cores since it specifies the number of threads to use to parallelize the execution of an individual op.
- [`--enable_batching`](https://github.com/tensorflow/serving/blob/b5a11f1e5388c9985a6fc56a58c3421e5f78149f/tensorflow_serving/model_servers/main.cc#L75) could give you better performance. However, since TFServing doesn't immediately response to each requests, there is a trade-off.
- By considering cost trade-off, **our recommendation from the experiment is to choose `2n-8c-16r-interop4`(2 Nodes of (8vCPU + 16G RAM)) configuration - 2 replicas of TFServing with --tensorflow_inter_op_parallelism=4** unless you care about dynamic batching capabilities. Or you can write a similar setup by referencing `2n-8c-16r-interop2-batch` but for smaller machines as well. 

</details>    
    
👋 **NOTE**

- Locust doesn't have a built-in support to write a gRPC based client, so we have written one for ourselves. If you are curious about the implementation, check [this locustfile.py](./locust/locustfile.py) out.
- The plot is generated by `matplotlib` after collecting CSV files generated from `Locust`.
- For the legend in the plot, `n` means the number of nodes(pods), `c` means the number of CPU cores, `r` means the RAM capacity, `interop` means the number of [`--tensorflow_inter_op_parallelism`](https://github.com/tensorflow/serving/blob/b5a11f1e5388c9985a6fc56a58c3421e5f78149f/tensorflow_serving/model_servers/main.cc#L147), and `batch` means the batching configuration is enabled with this [config](https://github.com/deep-diver/ml-deployment-k8s-tfserving/blob/main/.kube/experiments/8vCPU%2B64GB%2Binter_op2_w_batch/tfs-config.yaml).

## Future works

- [ ] More load test comparisons with more ML inference frameworks such as [NVIDIA's Triton Inference Server](https://developer.nvidia.com/nvidia-triton-inference-server), [KServe](https://www.kubeflow.org/docs/external-add-ons/kserve/kserve/), and [RedisAI](https://oss.redis.com/redisai/).

- [ ] Advancing this repo by providing a semi-automatic model deployment. To be more specific, when new codes implementing new ML model is pull requested, maintainers could trigger model performance evaluable on GCP's Vertex Training via `comments`. The experiment results could be exposed through [TensorBoard.dev](https://tensorboard.dev/) or [W&B](https://wandb.ai/site). If it is approved, the code will be merged, the trained model will be released, and it is going to be deployed on GKE.

## Acknowledgements

* [ML-GDE program](https://developers.google.com/programs/experts/) for providing GCP credit support.
* [Hannes Hapke](https://www.linkedin.com/in/hanneshapke) for providing great insights for load-testing. 

