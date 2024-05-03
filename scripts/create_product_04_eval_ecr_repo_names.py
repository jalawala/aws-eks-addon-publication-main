import sys
import boto3
import json
import os

def eval_ecr_repo_names(product_id):
    # Initialize the AWS Marketplace Catalog client
    client = boto3.client('marketplace-catalog','us-east-1')

    # List products
    response = client.describe_entity(Catalog='AWSMarketplace',EntityId=product_id)
    details=json.loads(response['Details'])

    # iterate repositories and print the urls
    for repo in details['Repositories']:
        if (repo['Url'].endswith('-helm')):
           os.environ['PRODUCT_HELM_REPO'] = repo['Url']
        else:
           os.environ['PRODUCT_IMAGES_REPO'] = repo['Url']

    print(f'export PRODUCT_HELM_REPO="{os.environ["PRODUCT_HELM_REPO"]}"')
    print(f'export PRODUCT_IMAGES_REPO="{os.environ["PRODUCT_IMAGES_REPO"]}"')

if __name__ == "__main__":
    eval_ecr_repo_names(sys.argv[1])
