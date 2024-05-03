import json
import sys
import time


def convert_to_product_payload(json_issue_path, product_payload_file):
    current_timestamp = int(time.time())
    with open(json_issue_path, 'r') as f:
        issue = json.load(f)

    seller_alias = issue['sellerMarketPlaceAlias']
    addon_name = issue['addon']['name']
    account_id = str(issue['accountId'])

    print(seller_alias)
    print(addon_name)

    # max helm release name length is 53
    # for suffix `-{timestamp}-helm` we need 16 characters, so 37 remaining
    chart_name_prefix=(f'{seller_alias}-{addon_name}')[:37]

    param_list = [
        seller_alias,
        addon_name,
        current_timestamp,
        chart_name_prefix
    ]

    if check_all_present(param_list):
        print("all params present")
        data = {
          "Catalog": "AWSMarketplace",
          "ChangeSet": [
            {
              "ChangeType": "CreateProduct",
              "Entity": {
                "Type": "ContainerProduct@1.0"
              },
              "DetailsDocument": {},
              "ChangeName": "CreateProductChange"
            },
            {
              "ChangeType": "UpdateInformation",
              "Entity": {
                "Type": "ContainerProduct@1.0",
                "Identifier": "$CreateProductChange.Entity.Identifier"
              },
              "DetailsDocument": {
                "LogoUrl": "https://awsmp-logos.s3.amazonaws.com/ca60b754fe05a24257176cdbf31c4e0d",
                "Categories": [
                  "Testing"
                ],
                "ProductTitle": (f'TestProduct-EKS-Addon-{seller_alias}-{addon_name}')[:72],
                "AdditionalResources": [],
                "LongDescription": f'This is a product for creating/testing the following EKS Addon: {seller_alias}/{addon_name}',
                "SearchKeywords": [
                  "testing",
                  "eks-addon",
                  seller_alias,
                  addon_name
                ],
                "ShortDescription": f'TestProduct-EKS-Addon-{seller_alias}-{addon_name}',
                "Highlights": [
                  f'Test addon product for {seller_alias}/{addon_name}',
                ],
                "SupportDescription": "No support available",
                "VideoUrls": []
              }
            },
            {
              "ChangeType": "UpdateTargeting",
              "Entity": {
                "Type": "ContainerProduct@1.0",
                "Identifier": "$CreateProductChange.Entity.Identifier"
              },
              "DetailsDocument": {
                "PositiveTargeting": {
                  "BuyerAccounts": [
                    account_id
                  ]
                }
              }
            },
            {
              "ChangeType": "AddRepositories",
              "Entity": {
                "Type": "ContainerProduct@1.0",
                "Identifier": "$CreateProductChange.Entity.Identifier"
              },
              "DetailsDocument": {
                "Repositories": [
                  {
                    "RepositoryName": (f'{chart_name_prefix}-{current_timestamp}-helm').lower(),
                    "RepositoryType": "ECR"
                  },
                  {
                    "RepositoryName": (f'{seller_alias}-{addon_name}-{current_timestamp}-images').lower(),
                    "RepositoryType": "ECR"
                  }
                ]
              }
            },
            {
              "ChangeType": "ReleaseProduct",
              "Entity": {
                "Type": "ContainerProduct@1.0",
                "Identifier": "$CreateProductChange.Entity.Identifier"
              },
              "DetailsDocument": {}
            },
            {
              "ChangeType": "CreateOffer",
              "Entity": {
                "Type": "Offer@1.0"
              },
              "DetailsDocument": {
                "ProductId": "$CreateProductChange.Entity.Identifier"
              },
              "ChangeName": "CreateOfferChange"
            },
            {
              "ChangeType": "UpdateLegalTerms",
              "Entity": {
                "Type": "Offer@1.0",
                "Identifier": "$CreateOfferChange.Entity.Identifier"
              },
              "DetailsDocument": {
                "Terms": [
                  {
                    "Type": "LegalTerm",
                    "Documents": [
                      {
                        "Type": "StandardEula",
                        "Version": "2022-07-14"
                      }
                    ]
                  }
                ]
              }
            },
            {
              "ChangeType": "UpdateSupportTerms",
              "Entity": {
                "Type": "Offer@1.0",
                "Identifier": "$CreateOfferChange.Entity.Identifier"
              },
              "DetailsDocument": {
                "Terms": [
                  {
                    "Type": "SupportTerm",
                    "RefundPolicy": "No refunds"
                  }
                ]
              }
            },
            {
              "ChangeType": "UpdateInformation",
              "Entity": {
                "Type": "Offer@1.0",
                "Identifier": "$CreateOfferChange.Entity.Identifier"
              },
              "DetailsDocument": {
                "Name": "Some container offer Name",
                "Description": "Some interesting container offer description"
              }
            },
            {
              "ChangeType": "ReleaseOffer",
              "Entity": {
                "Type": "Offer@1.0",
                "Identifier": "$CreateOfferChange.Entity.Identifier"
              },
              "DetailsDocument": {}
            }
          ]
        }
        # Convert the dictionary to JSON format
        json_data = json.dumps(data, indent=2)

        # Save the JSON data to a file
        with open(product_payload_file, "w") as file:
            file.write(json_data)

        print(f"Successfully created and saved JSON data to {product_payload_file}")
    else:
        print("Not all params present")
        print("Provided param_list: ", param_list)


def check_all_present(param_list):
    all_present = all(param is not None for param in param_list)
    return all_present


if __name__ == "__main__":
    convert_to_product_payload(sys.argv[1], sys.argv[2])
