# Deploying ML models with TFServing, Docker, and Kubernetes

*By: [Chansung Park](https://github.com/deep-diver) and [Sayak Paul](https://github.com/sayakpaul)*

This project shows how to serve an TensorFlow based image classification model as a
RESTful and gRPC web services with TFServing, Docker, and Kubernetes(k8s). The idea is to first
embed TensorFlow model into the TFServing docker image and then deploy it on a k8s cluster running on [Google Kubernetes
Engine (GKE)](https://cloud.google.com/kubernetes-engine). We do this integration
using [GitHub Actions](https://github.com/features/actions). 

👋 **Note**: Even though this project uses an image classification its structure and techniques can
be used to serve other models as well.

## Deploying the model as a service with k8s

- We provide the test code for TFServing in a local environment. Please take a look at [notebooks/TF_to_ONNX.ipynb](...) notebook for this.

- To deploy the custom TFServing image, we define our `deployment.yaml` workflow file inside .github/workflows. It does the following tasks:
    - Looks for any new release in this repo. A new release contains a compressed [`SavedModel`](https://www.tensorflow.org/guide/saved_model).
    - Create a custom Docker image based on CPU optimized TFServing base image.
      - You can find how to compile the CPU optimized TFServing base image [here](https://github.com/tensorflow/serving/blob/master/tensorflow_serving/g3doc/setup.md#optimized-build).
      - Also, you can find how to create a custom TFServing docker image [here](https://www.tensorflow.org/tfx/serving/serving_kubernetes#commit_image_for_deployment).
    - Pushes the latest Docker image to [Google Container Register (GCR)](https://cloud.google.com/container-registry).
    - Deploys the Docker container on the k8s cluster running on GKE. 


## Configurations needed beforehand



## Acknowledgements

[ML-GDE program](https://developers.google.com/programs/experts/) for providing GCP credit support.

