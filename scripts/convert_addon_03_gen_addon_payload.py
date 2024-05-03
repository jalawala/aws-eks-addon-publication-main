import json
import sys


def convert_to_addon_payload(json_issue_path, images_mapping_path, helm_mapping_path, eks_addon_payload_file, product_id):
    with open(json_issue_path, 'r') as f:
        issue = json.load(f)

    with open(helm_mapping_path, 'r') as f:
        helm_mapping = json.load(f)

    images_url = []
    with open(images_mapping_path, 'r') as f:
        mapping_set = json.load(f)
    for mapping in mapping_set:
        images_url.append(mapping['target_repo'] + ':' + mapping['target_tag'])

    seller_alias = issue['sellerName']
    addon_name = issue['addon']['name']
    addon_version = issue['addon']['version']
    addon_type = issue['addon']['type']
    helm_url = helm_mapping['target_repo'] + ":" + helm_mapping['target_tag']
    kubernetes_versions = issue['addon']['kubernetesVersion']
    architectures = issue['addon']['architectures']
    namespace = issue['addon']['namespace']

    print(seller_alias)
    print(addon_name)
    print(addon_version)
    print(addon_type)
    print(helm_url)
    print(images_url)
    print(kubernetes_versions)
    print(architectures)
    print(namespace)
    print(product_id)

    param_list = [
        addon_name,
        addon_version,
        addon_type,
        helm_url,
        images_url,
        kubernetes_versions,
        architectures,
        namespace,
        product_id
    ]

    if check_all_present(param_list):
        print("all params present")
        compatible_k8s_versions = [str(version) for version in kubernetes_versions]
        data = {
            "Catalog": "AWSMarketplace",
            "ChangeSet": [
                {
                    "ChangeType": "AddDeliveryOptions",
                    "Entity": {
                        "Type": "ContainerProduct@1.0",
                        "Identifier": product_id,
                    },
                    "DetailsDocument": {
                        "Version": {
                            "VersionTitle": (f'{seller_alias}-{addon_name}-{addon_version}')[:64],
                            "ReleaseNotes": f'Test product for: {seller_alias}-{addon_name}-{addon_version}',
                        },
                        "DeliveryOptions": [
                            {
                                "DeliveryOptionTitle": (f'{seller_alias}-{addon_name}-{addon_version}')[:72],
                                "Visibility": "Limited",
                                "Details": {
                                    "EksAddOnDeliveryOptionDetails": {
                                        "ContainerImages": images_url,
                                        "HelmChartUri": helm_url,
                                        "Description": f'Test description for: {seller_alias}-{addon_name}-{addon_version}',
                                        "UsageInstructions": f'Test usage instructions for: {seller_alias}-{addon_name}-{addon_version}',
                                        "AddOnName": addon_name,
                                        "AddOnVersion": addon_version,
                                        "AddOnType": addon_type,
                                        "CompatibleKubernetesVersions": compatible_k8s_versions,
                                        "SupportedArchitectures": architectures,
                                        "Namespace": namespace,
                                    }
                                },
                            }
                        ],
                    },
                    "ChangeName": "PublishAddonNew",
                }
            ],
        }
        # Convert the dictionary to JSON format
        json_data = json.dumps(data, indent=2)

        # Save the JSON data to a file
        with open(eks_addon_payload_file, "w") as file:
            file.write(json_data)

        print(f"Successfully created and saved JSON data to {eks_addon_payload_file}")
    else:
        print("Not all params present")
        print("Provided param_list: ", param_list)


def check_all_present(param_list):
    all_present = all(param is not None for param in param_list)
    return all_present


if __name__ == "__main__":
    convert_to_addon_payload(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
