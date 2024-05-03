#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

EKS_SERVICE="eks"
COPY_CHART_DIR=sleek_release_service_cleaner_chart_copy

showHelp() {
    echo "Usage: ./sleekReleaseServiceCleaner.sh CHART_PATH [--dry-run | --keep]
This scripts:
* Creates the manifests based on the chart and default values on '${COPY_CHART_DIR}'
* Search for appearances of the Release.Service helm objects
* If its not a dry-run
  * Creates a copy of the original chart '${EKS_SERVICE}'
  * Replaces the appearances found from the original files
  * Repackages the chart adding the 'cs-no-service' suffix to the version

Flags:
  -d,   --dry-run       Perform dry-run execution
  -k,   --keep          Keep temp files
"
}

main(){
    CHART_PATH=$1

    IS_DRY_RUN=false
    KEEP_TEMP_DIR=false
    KUBE_VERSION=1.27

    if [ ${2:-default} == '-d' ] || [ ${2:-default} == '--dry-run' ]; then
        IS_DRY_RUN=true
        echo "Dry run, not creating a new chart."
    fi

    if [ ${2:-default} == '-k' ] || [ ${2:-default} == '--keep' ]; then
        KEEP_TEMP_DIR=true
    fi

    TO_REPLACE=()
    while read -r FILE ; do
        echo ".Release.Service found in template '$FILE'"
        TO_REPLACE+=($FILE)
    done < <(grep -rlE '{{\s?.Release.Service\s?}}' $CHART_PATH)

    if [[ "${#TO_REPLACE[@]}" -eq 0 ]];
    then
        echo "No .Release.Service found, no changes required. Exiting"
        exit 0
    fi

    if [[ "$IS_DRY_RUN" = "true" ]];
    then
        echo "Dry run execution. Exiting"
        exit 0
    fi

    echo "Total templates to be modified: ${#TO_REPLACE[@]}"

    if [ -d $COPY_CHART_DIR ]; then
        echo "Chart copy directory already exists. Cleaning";
        rm -rf $COPY_CHART_DIR
    fi

    echo "Creating backup of $CHART_PATH in $COPY_CHART_DIR"
    cp -r $CHART_PATH $COPY_CHART_DIR

    for TEMPLATE in "${TO_REPLACE[@]}"; do
      echo Replacing in $TEMPLATE
      sed -i "s/{{ .Release.Service }}/$EKS_SERVICE/g" $TEMPLATE
    done

    # repackage with new version
    COPY_VERSION=$(helm show chart $CHART_PATH |yq .version)-cs-no-service
    CHART_NAME=$(helm show chart $CHART_PATH |yq .name)
    echo "Chart without .Service.Release available in ${CHART_PATH}"
    helm package $CHART_PATH --version $COPY_VERSION
    helm lint $CHART_NAME-$COPY_VERSION.tgz

    exit 0
}

# Show help and error if the directory is no parameters
if [[ $# -eq 0 ]];
then
    showHelp "$@"
    exit 1
fi

# Show help
if [[ "${1-}" =~ ^-*h(elp)?$ ]];
then
    showHelp "$@"
    exit
fi

# Error if the directory is not found
if [[ ! -d "${1}" ]];
then
  echo "Directory ${1} does not exist"
  exit 1
fi

# Error if the directory doesn't look like a helm chart
if [ ! -f "${1}/Chart.yaml" ];
then
    echo "There is not Chart.yaml file in ${1}"
    exit 1
fi

main "$@"
