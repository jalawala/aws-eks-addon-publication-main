import sys
import json
import time
import subprocess
import os


def parse_images(images_file, output_file, addon_timestamp, product_images_repo):
    current_timestamp = str(addon_timestamp)
    print(current_timestamp)

    images_list = []
    with open(images_file, 'r') as file:
        images_string = file.read()
        images_list = json.loads(images_string)

    with open(output_file, 'w') as file:
        file.write('[')
        for image_url in images_list:
            image_repo = image_url.split(':')[0]
            image_tag = image_url.split(':')[1]
            image_url_split_arr = image_repo.split('/')
            image_name = image_url_split_arr[len(image_url_split_arr) - 1]

            if len(image_url_split_arr) >= 2:
                image_owner = image_url_split_arr[len(image_url_split_arr) - 2]
                target_image_url = f"{product_images_repo}:{image_tag}-{image_owner}-{image_name}-{current_timestamp}"
            else:
                target_image_url = f"{product_images_repo}:{image_tag}-{image_name}-{current_timestamp}"

            try:
                # call a bash script that will pull image, re-tag it and push to target
                grepOut = subprocess.run(['bash', 'scripts/convert_addon_01_handle_image_push.sh', image_url, target_image_url])
                grepOut.check_returncode()
            except subprocess.CalledProcessError as err:
                # If returncode is non-zero, raise a CalledProcessError and print this message
                print(f"Could not process image {image_url}. Error code: {err.returncode} with error {err}")
                sys.exit(1)

            # process the mapping
            mapping_entry = {
                "source_repo": image_repo,
                "source_tag": image_tag,
                "target_repo": target_image_url.split(':')[0],
                "target_tag": target_image_url.split(':')[1]
            }
            file.write(json.dumps(mapping_entry))

            if image_url != images_list[len(images_list) - 1]:
                file.write(',')
        file.write(']')


if __name__ == "__main__":
    parse_images(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
