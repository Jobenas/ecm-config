import json
import os

path = os.path.dirname(os.path.abspath(__file__))


def save_to_config(key: str, value: str):
	print(f"Current path: {path}")
	if os.path.exists("config.json"):
		with open("config.json", "r") as config_file:
			config_data = json.load(config_file)

		config_data[key] = value
	else:
		config_data = {key: value}

	with open("config.json", "w") as config_file:
		json.dump(config_data, config_file)


def get_from_config(key: str):
	if os.path.exists("config.json"):
		with open("config.json", "r") as config_file:
			config_data = json.load(config_file)

		if key in config_data:
			return config_data[key]

	return None
