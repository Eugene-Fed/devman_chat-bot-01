import time
import requests
import os
import json
import telegram
import logging

from dotenv import load_dotenv


def load_config():
    """
    В корне проекта достаточно много "обязательного мусора" при наличии докера и разного CI/CD. Поэтому удобнее
    `.env` хранить в какой-нибудь папке. По крайней мере на моем последнем проекте он хранился именно в `config/` -
    это было единообразно по всем микросервисам и было вполне удобно.
    """
    dotenv_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    if not os.environ.get('DEVMAN_TOKEN') or not os.environ.get('TG_BOT_TOKEN') or not os.environ.get('TG_CHAT_ID'):
        raise EnvironmentError("You should set your `config/.env` file. Please check README.md.")

    if os.path.exists(config_path):
        return json.load(open(config_path, "r"))
    else:
        raise FileNotFoundError("File `config/config.json` not found. Please check README.md.")


def main():
    logging.basicConfig(
        filename='app.log',  # Чтобы не раздувать структуру папок оставим в учебных целях логфайл в корне.
        filemode='a',
        format='%(asctime)s: %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        level=logging.INFO
    )

    config = load_config()
    devman_token = os.environ['DEVMAN_TOKEN']
    tg_bot_token = os.environ["TG_BOT_TOKEN"]
    tg_chat_id = os.environ["TG_CHAT_ID"]
    tg_bot = telegram.Bot(token=tg_bot_token)
    reviews_url = config["urls"]["user_reviews"]
    reviews_headers = {'Authorization': f'Token {devman_token}'}
    reviews_params = dict()

    while True:
        try:
            response = requests.get(
                reviews_url, headers=reviews_headers, timeout=config["timeout"], params=reviews_params
            )

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            logging.warning(f"Connection Error. Waiting connection for {config['sleep']} seconds.")
            time.sleep(config["sleep"])
            continue

        if response.status_code >= 500:
            logging.warning(f"`{response.text}`. Request will be resend in {config['timeout']} seconds.")
            time.sleep(config['timeout'])
            continue
        elif response.status_code == 404:  # Добавил перехват конкретных кодов согласно ТЗ. Остальные группируются.
            raise requests.exceptions.HTTPError(f"{response.status_code}. Check `user_reviews` in `config.json`.")
        elif response.status_code == 401:
            raise requests.exceptions.HTTPError(f"{response.status_code}. Please check your DEVMAN_TOKEN.")
        elif not response.ok:
            raise requests.exceptions.HTTPError(f"{response.status_code}: `{response.text}`.")

        try:
            resp = response.json()  # Чтобы не впихивать в try/except весь следующий блок кода, проверяем json заранее
        except requests.exceptions.JSONDecodeError:
            print("An unexpected result was returned. Check if DEVMAN_TOKEN and url for user_reviews are correct.")
            break

        if ts := resp.get("timestamp_to_request"):  # Проверка на Timeout сервера
            reviews_params["timestamp"] = ts
            continue

        if attempts := resp.get("new_attempts"):
            for attempt in attempts:
                should_be_rewrite = attempt.get("is_negative")
                review_message = config.get("review_messages")[0] if should_be_rewrite \
                    else config.get("review_messages")[1]
                tg_bot.send_message(
                    text=config.get("message").format(title=attempt.get("lesson_title"),
                                                      url=attempt.get("lesson_url"),
                                                      review=review_message),
                    chat_id=tg_chat_id)
                logging.info("Message sent.")
        if ts := resp.get("last_attempt_timestamp"):  # Поиск таймстампа в ответе с инфой.
            reviews_params["timestamp"] = ts


if __name__ == '__main__':
    main()


