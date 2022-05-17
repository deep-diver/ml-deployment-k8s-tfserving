# Deploying ML models with TFServing, Docker, and Kubernetes

*By: [Chansung Park](https://github.com/deep-diver) and [Sayak Paul](https://github.com/sayakpaul)*

This project shows how to serve an TensorFlow based image classification model as a
RESTful and gRPC web services with TFServing, Docker, and Kubernetes(k8s). The idea is to first
embed TensorFlow model into the TFServing docker image and then deploy it on a k8s cluster running on [Google Kubernetes
Engine (GKE)](https://cloud.google.com/kubernetes-engine). We do this integration
using [GitHub Actions](https://github.com/features/actions). 

👋 **Note**: Even though this project uses an image classification its structure and techniques can
be used to serve other models as well.
👋 **Note**: There is a counter part project using FastAPI instead of TFServing. If you want to know
how to deploy FastAPI servers on k8s, please check out the [repo here](https://github.com/sayakpaul/ml-deployment-k8s-fastapi).

## Deploying the model as a service with k8s

- We provide the test code for TFServing in a local environment. Please take a look at [notebooks/TF_Serving.ipynb](...) notebook for this.

- To deploy the custom TFServing image, we define our `deployment.yaml` workflow file inside .github/workflows. It does the following tasks:
    - Looks for any new release in this repo using [release downloader GitHub Action](https://github.com/robinraju/release-downloader). A new release contains a compressed [`SavedModel`](https://www.tensorflow.org/guide/saved_model).
    - Create a custom Docker image based on CPU optimized TFServing base image.
      - You can find how to compile the CPU optimized TFServing base image [here](https://github.com/tensorflow/serving/blob/master/tensorflow_serving/g3doc/setup.md#optimized-build).
      - Also, you can find how to create a custom TFServing docker image [here](https://www.tensorflow.org/tfx/serving/serving_kubernetes#commit_image_for_deployment).
    - Pushes the latest Docker image to [Google Container Register (GCR)](https://cloud.google.com/container-registry).
    - Deploys the Docker container on the k8s cluster running on GKE. 


## Configurations needed beforehand

* Create a k8s cluster on GKE. [Here's](https://www.youtube.com/watch?v=hxpGC19PzwI) a
relevant resource. 
* [Create](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) a
service account key (JSON) file. It's a good practice to only grant it the roles
required for the project. For example, for this project, we created a fresh service 
account and granted it permissions for the following: Storage Admin, GKE Developer, and
GCR Developer. 
* Crete a secret named `GCP_CREDENTIALS` on your GitHub repository and copy paste the
contents of the service account key file into the secret. 
* Configure bucket storage related permissions for the service account:

    ```shell
    $ export PROJECT_ID=<PROJECT_ID>
    $ export ACCOUNT=<ACCOUNT>
    
    $ gcloud -q projects add-iam-policy-binding ${PROJECT_ID} \
        --member=serviceAccount:${ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
        --role roles/storage.admin
    
    $ gcloud -q projects add-iam-policy-binding ${PROJECT_ID} \
        --member=serviceAccount:${ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
        --role roles/storage.objectAdmin
    
    gcloud -q projects add-iam-policy-binding ${PROJECT_ID} \
        --member=serviceAccount:${ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
        --role roles/storage.objectCreator
    ```
* If you're on the `main` branch already then upon a new push, the worflow defined
in `.github/workflows/deployment.yaml` should automatically run. Here's how the
final outputs should look like so ([run link](https://github.com/sayakpaul/ml-deployment-k8s-fastapi/runs/5343002731)):

![](https://i.ibb.co/fDGFbpr/Screenshot-2022-03-01-at-12-25-42-PM.png)

## Notes

* We use [Kustomize](https://kustomize.io) to manage the deployment on k8s.

## Querying the API endpoint

From workflow outputs, you should see something like so:

```shell
NAME             TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)        AGE
fastapi-server   LoadBalancer   xxxxxxxxxx   xxxxxxxxxx        80:30768/TCP   23m
kubernetes       ClusterIP      xxxxxxxxxx     <none>          443/TCP        160m
```

Note the `EXTERNAL-IP` corresponding to `tfs-server` (iff you have named
your service like so). Then cURL it:

....

## Acknowledgements

[ML-GDE program](https://developers.google.com/programs/experts/) for providing GCP credit support.

