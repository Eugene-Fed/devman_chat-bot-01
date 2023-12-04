import time

import requests
import os
import json

from dotenv import load_dotenv


def load_config():
    dotenv_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    if not os.environ.get('DEVMAN_TOKEN'):
        print('You should set your API token. Please check README.md')
        raise EnvironmentError
    return json.load(open(config_path, "r"))


def main(config):
    token = os.environ['DEVMAN_TOKEN']
    get_reviews = config["urls"]["user_reviews"]
    headers = {'Authorization': f'Token {token}'}
    params = dict()
    while True:
        try:
            print("Send new request")
            response = requests.get(get_reviews, headers=headers, timeout=config["timeout"], params=params)
        except requests.exceptions.ReadTimeout:
            print("Bot generated timeout and created new request.")
            continue
        except requests.exceptions.ConnectionError:
            print("Connection Error. Waiting connection.")
            time.sleep(config["sleep"])
            continue

        if ts := response.json().get("timestamp_to_request"):
            params["timestamp"] = ts
            print(f"Server returned Timeout timestamp {ts}")
        print(response.json())


if __name__ == '__main__':
    load_config()
    main(load_config())
