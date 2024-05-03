import sys
import os
import json


def replace_images_in_chart(chart_path, mapping_path):
    file_name_list = []
    with open(mapping_path, 'r') as f:
        mapping_set = json.load(f)

    for root, d_names, f_names in os.walk(chart_path):
        for f in f_names:
            if not f.startswith('.') and not f=='Chart.yaml':
                file_name_list.append(os.path.join(root, f))
    # print("fname = %s" %fname)

    for filename in file_name_list:
        for mapping in mapping_set:
            old_repo = mapping['source_repo']
            new_repo = mapping['target_repo']
            old_tag = mapping['source_tag']
            new_tag = mapping['target_tag']
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                s = f.read()
                if old_repo in s:
                    with open(filename, 'w') as f:
                        print(f"Substituting {old_repo} to {new_repo} in {filename}")
                        s = s.replace(old_repo, new_repo)
                        f.write(s)
                if old_tag in s:
                    with open(filename, 'w') as f:
                        print(f"Substituting {old_tag} to {new_tag} in {filename}")
                        s = s.replace(old_tag, new_tag)
                        f.write(s)


if __name__ == "__main__":
    replace_images_in_chart(sys.argv[1], sys.argv[2])
