import sys
import json


def gen_mapping_file(output_file, source_repo, source_tag, target_repo, target_tag):
    with open(output_file, 'w') as file:
        mapping_entry = {
            "source_repo": source_repo,
            "source_tag": source_tag,
            "target_repo": target_repo,
            "target_tag": target_tag
        }
        file.write(json.dumps(mapping_entry))


if __name__ == "__main__":
    gen_mapping_file(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
