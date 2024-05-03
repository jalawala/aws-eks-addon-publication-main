# Report generation

Two different _GitHub Actions_ are responsible for the creation of the add-on installation report.

1. [M1-generate-all-reports](../../.github/workflows/M1-generate-all-reports.yaml): it queries all the issues with the
   label stored in the environment var "LABEL_READY_FOR_TEST", per each one of them, it dispatches a new job
   execute `D2-generate-issue-report` passing as parameter the issue id
2. [D2-generate-issue-report](../../.github/workflows/D2-generate-issue-report.yaml): finds the `addon-values.yaml` file
   used for doing the installation, stored in the branch, and it used its values for get the **seller** and **addon name
   **, the **version**, the **namespace** and identify on which **clusters** has been installed, then per each cluster,
   it lists all the resources on each cluster, within that namespace. A markdown file will be added to the pull request
   in a add-on subdirectory: `$ADDON_DIR/reports/report-$REPORT_TIME.md`. Finally, for the operator information, the
   action will show the list of `addons.eks.aws.upbound.io` applied on the management clusters

## Important:

Few important considerations:

* For being able to log in on each cluster, the pipeline depends of course on the AWS credentials, but also on
  configuring  `~/.kube/config`. It gets this information from the Cloudformation stack that deployed each cluster. Each
  stack has an output containing the command to add the cluster configuration to the context:
*

```yaml
aws eks update-kubeconfig --name $STACK_NAME --region $CLUSTER_REGION --role-arn $ROLE_ARN
``` 

> **CAUTION:** As the `$STACK_NAME` is computed based on the name of the cluster, changes on the EKS blueprints in
> the [CDK Cluster Repo](https://github.com/cloudsoft-fusion/aws-addon-clusters) for naming the
> clusters need to be propagated into the actions. See the declaration of the variable `TEST_CLUSTER_STACK_NAME`.

> **CAUTION:** Changes on the comments format for adding into the issue the PR number associated, identified by the
> prefix stored in `PR_PREFIX`, needs to be updated on the action too.
