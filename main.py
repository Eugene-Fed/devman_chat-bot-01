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
    print(requests.get(get_reviews, headers=headers).json())


if __name__ == '__main__':
    load_config()
    main(load_config())
