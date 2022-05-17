# Prerequisites

## GKE cluster

You can create a GKE cluster with either of GCP console or [gcloud CLI toolbox](https://cloud.google.com/sdk/gcloud/reference/container/clusters/create). For starteres, [Here's](https://www.youtube.com/watch?v=hxpGC19PzwI) a relevant resource. 

## IAM

- [Create](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) a
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

## Model release

In order for GitHub Action to handle automatic deployment on GKE, it is assumed that you already have a released model. The model should be the form of `SavedModel`, and it has to be comparessed with the name of `saved_model.tar.gz`(or you can set the filename differently as in the environment variable in GitHub Action). If you want to find out the simplest way to get `SavedModel`, please check out our [TF_Serving.ipynb notebook](https://github.com/deep-diver/ml-deployment-k8s-tfserving/blob/main/notebooks/TF_Serving.ipynb)
