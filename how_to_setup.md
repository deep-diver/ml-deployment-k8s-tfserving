## What to setup for your own workflow

You need to setup a set of environment variables defined in the [GitHub Action workflow](https://github.com/deep-diver/ml-deployment-k8s-tfserving/blob/main/.github/workflows/deployment.yml)

```yml
env:
  GCP_PROJECT_ID: <<YOUR GCP PROJECT ID>>
  GKE_CLUSTER_NAME: <<GKE CLUSTER NAME THAT YOU PROVISIONED>>
  GKE_ZONE: <<GCP ZONE THAT YOUR GKE CLUSTER IS PROVISIONED>>
  GKE_DEPLOYMENT_NAME: <<DEPLOYMENT NAME(LABEL) AS IN K8S RESOURCE>>
  
  BASE_IMAGE_TAG: <<BASE TFSERVING DOCKER IMAGE>>
  MODEL_NAME: <<YOUR MODEL NAME>>
  
  MODEL_RELEASE_REPO: <<GITHUB REPO THAT YOUR MODEL IS RELEASED>>
  MODEL_RELEASE_FILE: <<COMPRESSED ARCHIVE FILENAME WITHIN THE LATEST RELEASE>>
  TARGET_EXPERIMENT: "8vCPU+16GB+inter_op4"
```
