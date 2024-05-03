# Example template

## Template creation:

```shell
CHART_PATH="../../../../../../common/addon-installation"
COMMON_VALUES="../../../../../../common/test-addon-values.yaml"
helm template test $CHART_PATH -f $COMMON_VALUES -f values.addon.yaml.txt > addon.yaml
```

## values input:

[values.kustomization.yaml.txt](values.kustomization.yaml.txt)

```yaml
sellerName: example-seller
addonName: example-addon
addonVersion: 1.0.0
```
