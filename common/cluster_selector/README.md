# Cluster selector

This chart is only for reuse the same logic to create the list of clusters to deploy an addon based the issue input for
the supported architectures and kubernetes versions.

The list will be added to the `addon-values.yaml` used as input for the others helm charts

## Three steps:

1. Generate values for the original issue. It's done as part of
   the [pipeline](../../.github/workflows/D1-on-addon-success.yaml)

    ```shell
    OUTPUT=example-output-partial-values.yaml
    yq e '.addon.namespace as $namespace | .sellerMarketPlaceAlias as $sellerName | .addon.name as $addonName | .addon.version as $addonVersion | .addon.architectures as $architectures | .addon.kubernetesVersion as $kubernetesVersion | .addon.secretMapping // {} as $secretMapping | { "addonNamespace": $namespace, "sellerName": $sellerName, "addonName": $addonName, "addonVersion": $addonVersion, "architectures": $architectures, "kubernetesVersion":$kubernetesVersion, "secretMapping": $secretMapping }' \
      -oy example-input-issue.json > $OUTPUT
    ```
2. Use that output as input this chart and add it to the input
    ```shell
   INPUT=example-output-partial-values.yaml
   OUTPUT=example-output-with-clusters-values.yaml
   helm template --values=$INPUT --values=../../common/test-addon-values.yaml .
   ```

3. The pipeline will generate the templeate and add the result to the input value for the other charts. 
   Removing the `---` yaml separator is required
   ```shell
   ADDON_VALUES=addon-values.yaml
   sed -i "/---/d" $ADDON_VALUES  
   ```
