# aws-sleek-addon-kustomization helm chart

The resources created with this template need to be applied on the management repo for testing the addon when is 
approved, but later removed when the PR is merged

## Resources:

* `GitRepository` (source.toolkit.fluxcd.io/v1) Refearing to the PR branch as temporal source until is approved and merged
* `Kustomization` (kustomize.toolkit.fluxcd.io/v1) refearing `GitRepository` above
* `Kustomization` (kustomize.toolkit.fluxcd.io/v1) for each cluster, for installing the add-on resources created with [aws-sleek-addon-chart](../addon-prerequisites) 
