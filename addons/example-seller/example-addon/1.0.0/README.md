# Example template

## Template cration:

```shell
CHART_PATH="../../../../../common/aws-sleek-addon-chart"
helm template test $CHART_PATH -f values.kustomization.yaml.txt > templates.yaml
```

## values input:

[values.yaml](values.yaml.txt)

```yaml
sellerName: example-addon-charts
addonName: example-addon
addonVersion: 1.0.0
```
