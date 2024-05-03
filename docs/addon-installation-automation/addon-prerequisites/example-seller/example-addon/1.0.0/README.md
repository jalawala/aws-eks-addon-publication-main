# Example template

## Template cration:

```shell
CHART_PATH="../../../../../../common/addon-prerequisites"
COMMON_VALUES="../../../../../../common/test-addon-values.yaml"
helm template test $CHART_PATH -f $COMMON_VALUES -f values.yaml.txt > templates.yaml
```

## values input:

[values.yaml](values.yaml.txt)

```yaml
sellerName: example-addon-charts
addonName: example-addon
addonVersion: 1.0.0
```
