# aws-sleek-addon-chart

Resources for the add-on. They will be installing using a `kustomization` per each
test cluster.

Only one set of manifest will be created, flux will fan out the creation of the resources based on the kustomizations 
deployed on the management cluster

## Resources:

* `namespace`
* `ExternalSecret` (external-secrets.io/v1beta1)
