# Example template

## Template creation:

```shell
CHART_PATH="../../../../../../common/addon-management-cluster-manifests"
COMMON_VALUES="../../../../../../common/test-addon-values.yaml"
helm template test $CHART_PATH -f $COMMON_VALUES -f values.kustomization.yaml.txt > kustomization.yaml
```

## values input:

[values.kustomization.yaml.txt](values.kustomization.yaml.txt)

```yaml
sellerName: example-seller
addonName: example-addon
addonVersion: 1.0.0
```
