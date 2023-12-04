import time
import requests
import os
import json
import telegram

from dotenv import load_dotenv
from datetime import datetime


def load_config():
    dotenv_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    if not os.environ.get('DEVMAN_TOKEN') or not os.environ.get('BOT_TOKEN') or not os.environ.get('CHAT_ID'):
        print('You should set your `config/.env` file. Please check README.md')
        raise EnvironmentError
    return json.load(open(config_path, "r"))


def main(config):
    devman_token = os.environ['DEVMAN_TOKEN']
    bot_token = os.environ["BOT_TOKEN"]
    chat_id = os.environ["CHAT_ID"]
    bot = telegram.Bot(token=bot_token)
    reviews_url = config["urls"]["user_reviews"]
    reviews_headers = {'Authorization': f'Token {devman_token}'}
    reviews_params = dict()

    while True:
        try:
            print(f"Sent a new request at {datetime.now()}")
            response = requests.get(
                reviews_url, headers=reviews_headers, timeout=config["timeout"], params=reviews_params
            )
            resp_json = response.json()
        except requests.exceptions.ReadTimeout:
            print("Bot generated timeout and created new request.")
            continue
        except requests.exceptions.ConnectionError:
            print("Connection Error. Waiting connection.")
            time.sleep(config["sleep"])
            continue

        if ts := resp_json.get("timestamp_to_request"):  # Проверка на Timeout сервера
            reviews_params["timestamp"] = ts
            print(f"Server returned Timeout timestamp {ts}")
            continue

        if attempts := resp_json.get("new_attempts"):
            for attempt in attempts:
                should_be_rewrite = attempt.get("is_negative")
                review_message = config.get("review_messages")[0] if should_be_rewrite \
                    else config.get("review_messages")[1]
                bot.send_message(
                    text=config.get("message").format(title=attempt.get("lesson_title"),
                                                      url=attempt.get("lesson_url"),
                                                      review=review_message),
                    chat_id=chat_id)
        if ts := resp_json.get("last_attempt_timestamp"):  # Поиск таймстампа в ответе с инфой по последним изменениям.
            reviews_params["timestamp"] = ts
        else:
            time.sleep(config["timeout"])  # Если его вдруг почему-то нет, принудительно ждем, чтобы не спамить сервак.
        print(resp_json)


if __name__ == '__main__':
    load_config()
    main(load_config())
