#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

echo "Process the hem chart"
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Error. Not all params passed. Usage: $0 <source_helm_chart_url> <path_to_mapping_file>"
    exit 1
fi
echo "Process Input, Determine Output & List them all"
HELM_URL=$1
echo "HELM_URL: $HELM_URL"
MAPPING_FILE=$2
echo "IMAGES_MAPPING_FILE: $MAPPING_FILE"
HELM_MAPPING_FILE=$3
echo "HELM_MAPPING_FILE: $HELM_MAPPING_FILE"

CORRECT_HOOKS=$4
CORRECT_RELEASE_SERVICE=$5
JSON_ISSUE_FILEPATH=$6
TIMESTAMP=$7
TARGET_HELM_REPO=$8

HELM_REPO=$( echo "$HELM_URL" | cut -d ":" -f 1 | sed 's/\"//g')
echo "HELM_REPO: $HELM_REPO"
HELM_TAG=$( echo "$HELM_URL" | cut -d ":" -f 2 | sed 's/\"//g')
echo "HELM_TAG: $HELM_TAG"
HELM_CHART_NAME=$(echo $HELM_URL| sed 's/.*\///;s/:.*//')
echo "HELM_CHART_NAME: $HELM_CHART_NAME"
ECR_CHART_REGION=$(echo $HELM_REPO | awk -F'.' '{print $(NF-2)}')
echo "ECR_CHART_REGION: $ECR_CHART_REGION"
echo "TIMESTAMP: $TIMESTAMP"
echo "TARGET_HELM_REPO: $TARGET_HELM_REPO"

echo "Login & pull the chart"
if [[ "$HELM_REPO" == *"public.ecr.aws"* ]];
then
  echo "Helm login in public ECR"
  aws ecr-public get-login-password --region $ECR_CHART_REGION | helm registry login --username AWS --password-stdin $HELM_REPO
else
  echo "Helm login in private ECR"
  aws ecr get-login-password --region $ECR_CHART_REGION | helm registry login --username AWS --password-stdin $HELM_REPO
fi
helm pull oci://$HELM_REPO --version $HELM_TAG

echo "Chart pulled, helm logout of repo $HELM_REPO"
helm registry logout $HELM_REPO


echo "Determine the pulled chart name and evaluate the unique addon version tag"
echo "Echo inputs"
echo " > CORRECT_HOOKS: $CORRECT_HOOKS"
echo " > CORRECT_RELEASE_SERVICE: $CORRECT_RELEASE_SERVICE"
PULLED_CHART=$(find . -name '*.tgz')
echo " > PULLED_CHART: $PULLED_CHART"
CHART_NAME=$(helm show chart $PULLED_CHART | yq .name)
echo " > CHART_NAME: $CHART_NAME"
echo " > HELM_CHART_NAME: $HELM_CHART_NAME"
CHART_VERSION=$(helm show chart $PULLED_CHART | yq .version)
echo " > CHART_VERSION: $CHART_VERSION"
NEW_CHART_VERSION=$CHART_VERSION-${CHART_NAME//_}-$TIMESTAMP
echo " > NEW_CHART_VERSION: $NEW_CHART_VERSION"

echo "Unpack chart $HELM_CHART_NAME"
tar -xf $PULLED_CHART

echo "Adjust the helm chart - remove addon-incompatible features"

chmod +x scripts/sleekHooksCleaner.sh
chmod +x scripts/sleekReleaseServiceCleaner.sh

# for debugging
#echo "$ ls -l"
#ls -l
#echo "$ ls -l ${HELM_CHART_NAME}"
#ls -l $HELM_CHART_NAME
#echo "Script first lines"
#head -n 1 scripts/sleekHooksCleaner.sh
#head -n 1 scripts/sleekReleaseServiceCleaner.sh

echo "...Removing hooks..."
if [ "$CORRECT_HOOKS" = true ]; then
  echo "Opt-in cleaning hooks"
  touch sleekHookCleaner.log
  ./scripts/sleekHooksCleaner.sh $HELM_CHART_NAME >> sleekHookCleaner.log 2>&1
  cat sleekHookCleaner.log
  gh issue comment $GITHUB_ISSUE_NO --body-file sleekHookCleaner.log
else
  echo "No opt-in cleaning hooks"
fi

echo "...Removing .Release.Service..."
if [ "$CORRECT_RELEASE_SERVICE" = true ]; then
  echo "Opt-in cleaning .Release.Service"
  touch sleekReleaseServiceCleaner.log
  ./scripts/sleekReleaseServiceCleaner.sh $HELM_CHART_NAME >> sleekReleaseServiceCleaner.log 2>&1
  cat sleekReleaseServiceCleaner.log
  gh issue comment $GITHUB_ISSUE_NO --body-file sleekReleaseServiceCleaner.log
else
  echo "No opt-in cleaning .Release.Service"
fi

echo "Update name & version in  $HELM_CHART_NAME/Chart.yaml"
TARGET_HELM_REPO_NAME="${TARGET_HELM_REPO##*/}"
yq e ".name = \"$TARGET_HELM_REPO_NAME\"" -i $HELM_CHART_NAME/Chart.yaml
yq e ".version = \"$NEW_CHART_VERSION\"" -i $HELM_CHART_NAME/Chart.yaml

echo "Replace the container images throughout the chart - based on $MAPPING_FILE mapping file"
python3 scripts/convert_addon_02_replace_images.py $HELM_CHART_NAME $MAPPING_FILE

echo "Repackage final version of chart $HELM_CHART_NAME"
helm package $HELM_CHART_NAME

echo "Helm log into Marketplace repo: ${TARGET_HELM_REPO%%/*}"
ECR_CHART_REGION=$(echo $TARGET_HELM_REPO | awk -F'.' '{print $(NF-2)}')
echo "ECR_CHART_REGION: $ECR_CHART_REGION"
aws ecr get-login-password --region $ECR_CHART_REGION | helm registry login --username AWS --password-stdin ${TARGET_HELM_REPO%%/*}

echo "helm push ${TARGET_HELM_REPO_NAME}-${NEW_CHART_VERSION}.tgz oci://${TARGET_HELM_REPO%/*}"
helm push $TARGET_HELM_REPO_NAME-$NEW_CHART_VERSION.tgz oci://${TARGET_HELM_REPO%/*}
echo "Push the chart $TARGET_HELM_REPO_NAME-$NEW_CHART_VERSION.tgz with version $NEW_CHART_VERSION successfully to  ${TARGET_HELM_REPO}:${NEW_CHART_VERSION}"
python3 scripts/convert_addon_02_gen_helm_mapping.py $HELM_MAPPING_FILE $HELM_REPO $HELM_TAG "${TARGET_HELM_REPO%/*}/$TARGET_HELM_REPO_NAME" $NEW_CHART_VERSION

echo "---------"
cat $HELM_MAPPING_FILE
echo "---------"
