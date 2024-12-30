import json
import os


def save_to_config(key: str, value: str):
    home_dir = os.path.expanduser('~')
    config_dir = os.path.join(home_dir, 'ECMConfig')

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    config_file_path = os.path.join(config_dir, 'config.json')

    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as config_file:
            config_data = json.load(config_file)
    else:
        config_data = {}

    config_data[key] = value

    with open(config_file_path, 'w') as config_file:
        json.dump(config_data, config_file, indent=4)


def get_from_config(key: str):
    home_dir = os.path.expanduser('~')
    config_dir = os.path.join(home_dir, 'ECMConfig')
    config_file_path = os.path.join(config_dir, 'config.json')

    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as config_file:
            config_data = json.load(config_file)

            if key in config_data:
                return config_data[key]

    return None
