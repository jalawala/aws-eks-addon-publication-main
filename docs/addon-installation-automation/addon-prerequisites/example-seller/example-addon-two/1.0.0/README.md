# Example template

## Template cration:

```shell
CHART_PATH="../../../../../../common/aws-sleek-addon-chart"
helm template test $CHART_PATH -f values.kustomization.yaml.txt > templates.yaml
```

## values input:

[values.yaml](values.yaml.txt)

```yaml
addonNamespace: example-ns-two
sellerName: example-addon-charts
addonName: example-addon-two
addonVersion: 1.0.0
secretMapping:
  exampleSecretOne:
    - secretKeyOneOne
    - secretKeyOneTwo
  exampleSecretTwo:
    - secretKeyTwoOne
    - secretKeyTwoTwo
clusters:
  - addon-tester-amd-1-28
  - addon-tester-arm-1-28
```
