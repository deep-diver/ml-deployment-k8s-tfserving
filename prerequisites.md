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
