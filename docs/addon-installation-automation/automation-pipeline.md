# Addon Automation Pipeline

## Introduction

The aim of the automation is to streamline the process of onboarding AWS partners for the EKS Add-on Program.
In the default scenario, the partner takes their container marketplace product and adjusts the Helm chart to be
compatible to be deployed as an EKS addon. This could involve a number of steps to adjust the chart and to deploy and
test the addon.
The automation is implemented in order to enable the process to be carried out automatically and produce compatible
assets to be deployed by the partners, significantly reducing the overhead required in the manual approach.

## Preparation

In order to use the automation pipeline, first the partner needs to install the CLI tool that enables the user to create
an issue, which in turn kicks off the automated process.

The CLI tool can be accessed via the following github
repository: https://github.com/aws-samples/addons-transformer-for-amazon-eks

After installing the tool, the user should create a YAML input file, following the schema located in the following
file: https://github.com/aws-samples/addons-transformer-for-amazon-eks/blob/dev/schema/onboarding.schema.json

The input should include critical information such as the addon name, version, seller name, as well as the URLs to the
helm chart and relevant images. Please note that currently only input ECR charts/images are supported, so if the partner
stores these elsewhere, they should first push to an ECR repo.

The partner can then call the create-issue command in the CLI to create a GitHub issue in a relevant repository, that
will trigger the process of automatic addon creation in a test account.

Note that the process described below uses a separate reusable helper action throughout the course to parse the issue
body and save into a json file, which can be found here:
https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/.github/action-helpers/issue-body-parser/action.yaml

## Automation Step 1 - Determine if new addon / update

Once the issue is created by the CLI, it automatically triggers a GitHub workflow that assesses whether the Add-on is a
new addon or an update to an existing addon.
(https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/.github/workflows/1-process-issue-auto-assign-label.yaml)
The workflow establishes above based on two factors - the presence of a relevant directory within the structure of the
repository, as well as presence of a product requested within the marketplace.

First, it checks the repository. Any addon that gets added through the pipeline will have a relevant directory created
in the repository, following the tree structure convention `addons/{sellerMarketPlaceAlias}/{addonName}/{addonVersion}`.
It checks whether the directory for the addon exists, as well as whether the version requested already exists (which
should not be the case).
Secondly, the pipeline checks the marketplace to find if the add-on product already exists there with the desired
version, using aws cli: `aws eks describe-addon-versions`.

Once it makes the checks above, the workflow determines which label should be added to the issue. The possible options
are: NEW, UPDATE and UNKNOWN:
If the product is found in the addons repository and does NOT already have the version requested AND the product does
exist in the marketplace and does NOT have the version requested, the UPDATE label gets added to the issue.
Similarly, if the Addon does NOT exist at all in the repo and does NOT exist in the marketplace, then NEW label is added
Otherwise, the state of the addon is considered uncertain and requires manual overview, in which case the UNKNOWN tag
gets added. In such case it is expected for the operator to manually validate whether this is a new or existing addon.

A relevant comment is then added to the issue to indicate which label has been added and what predicates it has been
based on.

## Automation Step 2 - Processing the addon

Assuming that either NEW or UPDATE label gets added, the following workflow gets triggered automatically and is
responsible for processing the
addon: https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/.github/workflows/2-process-addon.yaml.
The workflow consists of a number of jobs that run one after another ensuring a smooth transition from the input data
into artefacts generated for the user. At each stage of the process, a relevant comment is added to the issue for
reference and to pass some important information.

### 2.1 Open PR

The first step of the process is to open a PR for the addon. This is intended to store important information and
artefacts for the addon. Initially, it just contains the metadata json file containing the input provided to the issue,
as well as the issue body in raw text format, in order to preserve any comments provided. To open the PR, the workflow
uses a third party github action: https://github.com/peter-evans/create-pull-request

### 2.2 Validation

The next step of the pipeline is the validation of the helm chart provided in the input. During this step, the workflow
runs the validate command from the previously mentioned CLI `addons-transformer-for-amazon-eks`. This can be either
built from source or installed using npm, depending on configuration of the repository. Note that by default we expect
to run this using the npm install, while the build from source option is mainly for debugging and development purposes.
The validation command checks the chart for incompatible components and in case of any issues, adds a comment
accordingly. If the validation passes, a relevant comment also gets added and workflow job completes successfully,
automatically triggering the next task.

### 2.3 Conversion to addon

The next step of the process is to run the job responsible for creating the addon request.
Creating/getting a product
Depending on the label originally attached to the issue in the former steps, we need to either create a new product or
retrieve details of existing product (job handle-create-or-get-product).

If we have a new addon, the workflow creates a new product in the test marketplace account that will be responsible for
storing the particular seller’s addon product in the future. To achieve that, we generate the payload required by the
CLI (https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/scripts/create_product_01_gen_product_payload.py)
and then call the catalog api to create a new free product using change
sets (https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/scripts/create_product_02_submit_new_product_request.py).
After product is created, we get it’s
details (https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/scripts/create_product_03_get_product_id.py)
and set the relevant outputs to be used by the next
step (https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/scripts/create_product_04_eval_ecr_repo_names.py)

In case this is an update of an existing addon, there is no need for the product to be created, since it already exists.
Therefore, in such cases we retrieve the details of the existing product instead based on the input details and evaluate
the outputs as per above.
Converting to an addon
Once we have the product created or retrieved, we are ready to create the addon. The job itself consists of a number of
steps:

First step is to process the images. The images supplied in the input are pulled, retagged and pushed to the repository
of the product evaluated in the previous step. In order to ensure uniqueness, the tags are built up from a number of
factors, including the current
timestamp. (https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/scripts/convert_addon_01_push_images_and_gen_mapping.py)
The script above is also responsible to generate a mapping file for source image urls to target image urls, so that
replacement through the chart can be made later.
The second step is processing of the
chart (https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/scripts/convert_addon_02_process_chart.sh).
The chart is pulled from the ECR repository, then based on the metadata of the chart and the current timestamp, a new
version is generated for it (to guarantee uniqueness). Pulled chart is unpacked and the metadata is amended to match the
repository name as well as the updated tag. Depending on the configuration specified in the input, the pipeline is
capable of automatically fixing some issues with the chart, such as hooks and use of the .Release.Service object.
FInally, based on the mapping file for the images generated in previous step, we replace these throughout the
chart (https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/scripts/convert_addon_02_replace_images.py)
After the chart is modified, it gets packaged and uploaded to a relevant ECR repository, belonging to the product.
Once the images and the chart have been pushed to their respective repositories, we follow by creating the payload based
on the previous
data (https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/scripts/convert_addon_03_gen_addon_payload.py)
and supply this to the aws marketplace catalog cli, that creates the change sets and process adding a new version of the
product as an eks
addon (https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/scripts/convert_addon_04_submit_addon_request.py)

## Automation Step 3 - periodical checks

After the add-on request has been submitted, it can take up to 5 business days for it to be processed. Therefore, there
exists another github action that runs periodically (every 6 hours) that checks the status of the
request (https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/.github/workflows/S1-check-request-status.yaml).
Once the request is successful and the add on is live, we can progress to the next step responsible for deploying the
add on on a set of clusters and ensuring that it can be deployed
successfully (https://github.com/jalawala/aws-eks-addon-publication-main /blob/main/.github/workflows/D1-on-addon-success.yaml).

## Automation Step 4 - Deployment and testing

TBD

## Automation Step 5 - Final assets generation

TBD
