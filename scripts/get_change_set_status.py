import sys

import boto3

# Running locally requires:
# export AWS_DEFAULT_REGION=us-east-1
# export AWS_REGION=us-east-1

mp_catalog_client = boto3.client('marketplace-catalog')

def checkStatus(requestId):
    try:
        change_set_stat = mp_catalog_client.describe_change_set(
            Catalog='AWSMarketplace',
            ChangeSetId=requestId
        )
        print(change_set_stat['Status'])
    except:
        sys.exit(f'Error checking status of request {requestId}')

if __name__ == "__main__":
    checkStatus(sys.argv[1])
