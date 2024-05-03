# Add-on installation structure

The helm chart [aws-sleek-addon-chart](../../common/addon-prerequisites) create the templates for installing the
add-on using [FluxCD](https://fluxcd.io/)

This is an example of the `kustomization` used for deploy the resources, if moved to the [addons](../../addons)
directory to match the `.spec.path` definition

A `Kustomization` is needed for each target cluster and addon:

AMD cluster:

```yaml
---
# Source: addon-management-cluster-manifests/templates/kustomization.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: example-seller-example-addon-1.0.0-addon-tester-amd-1-28
  namespace: upbound-system
  labels:
    app: aws-sleek-addon
    cluster: addon-tester-amd-1-28
spec:
  interval: 30s
  path: ./addons/example-addon-charts/example-addon/1.0.0
  prune: true
  sourceRef:
    kind: GitRepository
    name: crossplan-manifests
  kubeConfig:
    secretRef:
      name: addon-tester-amd-1-28-connection
      key: kubeconfig
```

ARM cluster:

```yaml
# Source: addon-management-cluster-manifests/templates/kustomization.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: example-seller-example-addon-1.0.0-addon-tester-arm-1-28
  namespace: upbound-system
  labels:
    app: aws-sleek-addon
    cluster: addon-tester-arm-1-28
spec:
  interval: 30s
  path: ./addons/example-addon-charts/example-addon/1.0.0
  prune: true
  sourceRef:
    kind: GitRepository
    name: crossplan-manifests
  kubeConfig:
    secretRef:
      name: addon-tester-arm-1-28-connection
      key: kubeconfig
```

`Kustomizations` are created using other helm chart.
