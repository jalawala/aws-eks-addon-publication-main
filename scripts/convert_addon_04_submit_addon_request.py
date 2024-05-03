import sys
import json
import time

import boto3

mp_catalog_client = boto3.client('marketplace-catalog')


def create_eks_addon_delivery_option(prod_id, eks_addon_payload_file, helm_mapping_path):
    print(f"Submitting ADDON {prod_id} with payload: {eks_addon_payload_file}")
    with open(eks_addon_payload_file) as details:
        change_sets = json.load(details)
        change_sets['ChangeSet'][0]['Entity']['Identifier'] = prod_id
        print(change_sets['ChangeSet'][0])

    with open(helm_mapping_path, 'r') as f:
        helm_mapping = json.load(f)

    return action_start_change_set(change_sets['ChangeSet'], "AddOn Request: " + helm_mapping['target_tag'])


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
    check_status_timeout_seconds = 300
    elapsed_time = 0
    delay_seconds = 30
    while change_set_stat['Status'] != 'SUCCEEDED':
        if elapsed_time >= check_status_timeout_seconds:
            print(f'Exiting status check loop after {elapsed_time}s')
            break
        if change_set_stat['Status'] == 'PREPARING' or change_set_stat['Status'] == 'APPLYING':
            print(f'Waiting {delay_seconds}s before next attempt (total waiting: {elapsed_time}s of max {check_status_timeout_seconds}s) ' + change_set_name_arg + "... ")
            # It fails quick for some chart validation, security failures require more time. Then, if all is ok, human checks involved requiere between 1 and 10 days
            elapsed_time += delay_seconds
            time.sleep(delay_seconds)
        if change_set_stat['Status'] == 'FAILED' or change_set_stat['Status'] == 'CANCELLED':
            return {
                'StatusCode': 500,
                'message': 'Error (' + change_set_stat['Status'] + ') while creating PMP from Lambda for ' + change_set_name_arg + json.dumps(
                    change_set_stat),
                'ChangeSetId': change_set['ChangeSetId'],
            }
        change_set_stat = mp_catalog_client.describe_change_set(
            Catalog='AWSMarketplace',
            ChangeSetId=change_set['ChangeSetId']
        )
        print('ChangeSet Status :: ' + change_set_name_arg + ' is ' + json.dumps(change_set_stat))
    return {
        'ChangeSetId': change_set['ChangeSetId'],
        'StatusCode': 201,
    }


if __name__ == "__main__":
    request = create_eks_addon_delivery_option(sys.argv[1], sys.argv[2], sys.argv[3])
    request_id = request['ChangeSetId']
    print(json.dumps(request_id))
    with open(sys.argv[4], 'w') as request_id_file:
        request_id_file.write(json.dumps(request_id))
    if request['StatusCode'] == 500:
        sys.exit(1)
