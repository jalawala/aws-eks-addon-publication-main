#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

echo "Process Image"

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Error. Not all params passed. Usage: $0 <source_image_url> <target_image_url>"
    exit 1
fi

SOURCE_URL=$1
echo "SOURCE_URL: $SOURCE_URL"
TARGET_URL=$2
echo "TARGET_URL: $TARGET_URL"
echo "Pulling image $SOURCE_URL"

if [[ "$SOURCE_URL" == *"public.ecr.aws"* ]];
then
  echo "Docker login in AWS public ECR"
  aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${SOURCE_URL%%/*}
elif [[ "$SOURCE_URL" == *"amazonaws"* ]];
then
  echo "Docker login in private ECR"
  terms=($(echo $SOURCE_URL | tr "." "\n"))
  SOURCE_REGION=${terms[3]}
  aws ecr get-login-password --region ${SOURCE_REGION} | docker login --username AWS --password-stdin ${SOURCE_URL%%/*}
else
  echo "No login needed. Assuming public image."
fi

echo "Login & Push image to Destination ECR (usually Marketplace ECR Repo)"
echo "Login"
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${TARGET_URL%%/*}

echo "Copy ${SOURCE_URL} to ${TARGET_URL}"
# this works for any container image multi-arch or not
/home/runner/regctl image copy $SOURCE_URL $TARGET_URL
