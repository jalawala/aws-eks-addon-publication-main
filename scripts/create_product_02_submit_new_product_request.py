import sys
import json
import time

import boto3

mp_catalog_client = boto3.client('marketplace-catalog')


def create_marketplace_product(product_payload_file):
    print(f"Creating new marketplace product with: {product_payload_file}")
    with open(product_payload_file) as details:
        change_sets = json.load(details)
        print(change_sets['ChangeSet'][0])

    return action_start_change_set(change_sets['ChangeSet'], "New product request")


def action_start_change_set(change_set_arg, change_set_name_arg):
    print('Invoking start_change_set ::' + change_set_name_arg)
    change_set = mp_catalog_client.start_change_set(
        Catalog='AWSMarketplace',
        ChangeSet=change_set_arg,
        ChangeSetName=change_set_name_arg

    )
    print('Invoking describe_change_set ::' + change_set_name_arg + ' is ' + json.dumps(change_set))
    change_set_stat = mp_catalog_client.describe_change_set(
        Catalog='AWSMarketplace',
        ChangeSetId=change_set['ChangeSetId']
    )
    current_timestamp = time.time()
    print(str(current_timestamp) + ':: ChangeSet Status :: for ' + change_set_name_arg + ' is '
          + json.dumps(change_set_stat))
    # Loop for checking status on changeSets
    check_status_timeout = 30 * 60
    elapsed_time = 0
    delay_seconds = 30
    while change_set_stat['Status'] != 'SUCCEEDED':
        if elapsed_time > check_status_timeout:
            print(f'Exiting status check loop after {elapsed_time}s')
            break
        if change_set_stat['Status'] == 'PREPARING' or change_set_stat['Status'] == 'APPLYING':
            print('Waiting 10s before next attempt :: ' + change_set_name_arg + "... ")
            # It can take more than 30 min, even hours.
            elapsed_time += delay_seconds
            time.sleep(delay_seconds)
        if change_set_stat['Status'] == 'FAILED' or change_set_stat['Status'] == 'CANCELLED':
            return {
                'StatusCode': 500,
                'message': 'Error (' + change_set_stat['Status'] + ') while creating PMP from Lambda for ' + change_set_name_arg + json.dumps(
                    change_set_stat)
            }
        change_set_stat = mp_catalog_client.describe_change_set(
            Catalog='AWSMarketplace',
            ChangeSetId=change_set['ChangeSetId']
        )
        print('ChangeSet Status :: ' + change_set_name_arg + ' is ' + json.dumps(change_set_stat))
    return change_set['ChangeSetId']


if __name__ == "__main__":
    create_marketplace_product(sys.argv[1])
