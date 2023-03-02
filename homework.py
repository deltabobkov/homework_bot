import logging
import sys
import time
from http import HTTPStatus

import requests
import telegram

from constants import (
    ENDPOINT,
    HEADERS,
    HOMEWORK_VERDICTS,
    PRACTICUM_TOKEN,
    RETRY_PERIOD,
    TELEGRAM_CHAT_ID,
    TELEGRAM_TOKEN,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s, %(levelname)s, %(message)s",
    stream=sys.stdout,
)


def check_tokens():
    """Проверка доступности переменных."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправка сообщения в телегу."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug("Сообщение было отправлено")
    except Exception as error:
        logging.error(f"Ошибка отправки сообщения в телегу {error}")


def get_api_answer(timestamp):
    """Запрос к API."""
    payload = {"from_date": timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException as error:
        logging.error(f"Сбой при запросе к API {error}")
    finally:
        if response.status_code != HTTPStatus.OK:
            logging.error(response.status_code)
            raise requests.exceptions.HTTPError("Endpoint не доступен")
    return response.json()


def check_response(response):
    """Проверка ответа от API."""
    if not isinstance(response, dict):
        raise TypeError(f"Неверный тип данных {type(response)}")
    if "homeworks" not in response:
        raise KeyError("Нет ключа homeworks")
    if not isinstance(response["homeworks"], list):
        raise TypeError(f"Неверный тип данных {type(response['homeworks'])}")
    if len(response["homeworks"]) == 0:
        logging.error("Список пуст")
        raise Exception("Нет данных о домашках")


def parse_status(homework):
    """Передача статуса проверки."""
    if "homework_name" not in homework:
        raise KeyError("Нет ключа homework_name")
    if "status" not in homework:
        raise Exception("Нет статуса проверки работы")
    homework_name = homework["homework_name"]
    homework_status = homework["status"]
    if homework_status not in HOMEWORK_VERDICTS:
        raise Exception(f"Статус проверки не определен {homework_status}")
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical("Нет переменных")
        sys.exit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    hwrk_status_old = ""
    error_message_old = ""

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            if response.get("homeworks"):
                hwrk_status_new = response.get("homeworks")[0]
                if hwrk_status_old != hwrk_status_new["status"]:
                    hwrk_status_old = hwrk_status_new["status"]
                    hwrk_status_send = parse_status(hwrk_status_new)
                    send_message(bot, hwrk_status_send)
                else:
                    logging.debug("Статус не изменился")
        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            logging.error(message)
            if message != error_message_old:
                send_message(bot, message)
                error_message_old = message
        time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    main()
