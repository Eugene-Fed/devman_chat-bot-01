import time
import requests
import os
import json
import telegram
import logging

from dotenv import load_dotenv
from systemd.journal import JournalHandler


def load_config():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')

    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    if not os.environ.get('DEVMAN_TOKEN') or not os.environ.get('TG_BOT_TOKEN') or not os.environ.get('TG_CHAT_ID'):
        raise EnvironmentError("You should set your `.env` file. Please check README.md.")
    if os.path.exists(config_path):
        return json.load(open(config_path, "r"))
    else:
        raise FileNotFoundError("File `config/config.json` not found. Please check README.md.")


def main():
    logging.basicConfig(
        filename=os.path.join(os.path.dirname(__file__), 'log', 'app.log'),
        filemode='a',
        format='%(asctime)s: %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        level=logging.INFO
    )
    systemd_log = logging.getLogger('systemd_log')
    systemd_log.addHandler(JournalHandler())
    systemd_log.setLevel(logging.INFO)

    config = load_config()
    devman_token = os.environ['DEVMAN_TOKEN']
    tg_bot_token = os.environ["TG_BOT_TOKEN"]
    tg_chat_id = os.environ["TG_CHAT_ID"]
    tg_bot = telegram.Bot(token=tg_bot_token)
    reviews_url = config["urls"]["user_reviews"]
    reviews_headers = {'Authorization': f'Token {devman_token}'}
    reviews_params = dict()

    systemd_log.info("Bot started")  # В журнал
    logging.info("Bot started")  # В папку проекта
    tg_bot.send_message(text="Bot started", chat_id=tg_chat_id)  # В ТГ
    
    while True:
        try:
            response = requests.get(
                reviews_url, headers=reviews_headers, timeout=config["timeout"], params=reviews_params
            )
            response.raise_for_status()
            review_info = response.json()

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            logging.warning(f"Connection Error. Waiting connection for {config['sleep']} seconds.")
            time.sleep(config["sleep"])
            continue
        except requests.exceptions.HTTPError as ex:
            logging.error(f"Server returned: `{ex.response}`.")
            break
        except requests.exceptions.JSONDecodeError:
            logging.error(f"There is no JSON in the server response. "
                          f"Check if DEVMAN_TOKEN and url for user_reviews are correct.")
            break

        if ts := review_info.get("timestamp_to_request"):  # Проверка на Timeout сервера
            reviews_params["timestamp"] = ts
            continue

        if attempts := review_info.get("new_attempts"):
            for attempt in attempts:
                should_be_rewrite = attempt.get("is_negative")
                review_message = config.get("review_messages")[0] if should_be_rewrite \
                    else config.get("review_messages")[1]
                tg_bot.send_message(
                    text=config.get("message").format(title=attempt.get("lesson_title"),
                                                      url=attempt.get("lesson_url"),
                                                      review=review_message),
                    chat_id=tg_chat_id)
                logging.info("Message sent")
        if ts := review_info.get("last_attempt_timestamp"):  # Поиск таймстампа в ответе с инфой.
            reviews_params["timestamp"] = ts


if __name__ == '__main__':
    main()


