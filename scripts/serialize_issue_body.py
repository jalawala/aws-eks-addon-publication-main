import sys
import json
import re
import yaml


def create_json_output(yaml_content, output_json_filename):
    yaml_object = yaml.safe_load(yaml_content.strip())
    with open(output_json_filename, 'w') as file:
        json_string = json.dumps(yaml_object)
        file.write(json_string)


def get_content_from_file(filename):
    with open(filename, 'r') as file:
        file_contents = file.read()
        # cleans up the backticks and everything that is not part of the YAML body
        yaml_pattern = r'```yaml\s*(.*?)\s*```'
        match = re.search(yaml_pattern, file_contents, re.DOTALL)
        if match:
            return match.group(1)
        else:
            return None


if __name__ == "__main__":
    issue_content = get_content_from_file(sys.argv[1])
    create_json_output(issue_content, sys.argv[2])
