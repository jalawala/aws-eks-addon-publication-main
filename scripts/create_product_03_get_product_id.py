import sys
import boto3

def get_product_id(product_name):
    # Initialize the AWS Marketplace Catalog client
    client = boto3.client('marketplace-catalog','us-east-1')

    # List products
    response = client.list_entities(Catalog='AWSMarketplace',EntityType='ContainerProduct')

    # Search for the product with the matching name
    for product in response['EntitySummaryList']:
        if product['Name'] == product_name[:72]:
            print(product['EntityId'])
            return

    # Return None if product not found
    return None

if __name__ == "__main__":
    get_product_id(sys.argv[1])
