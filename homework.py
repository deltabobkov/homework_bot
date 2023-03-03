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
from exceptions import QueryToApiFail, TelegramMessageSendFail


def check_tokens() -> bool:
    """Проверка доступности переменных."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message: str):
    """Отправка сообщения в телегу."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug("Отправка сообщения в телеграм")
    except telegram.error.TelegramError as error:
        logging.error(f"Ошибка отправки сообщения в телегу {error}")
        raise TelegramMessageSendFail(
            "Бот не смог отправить сообщени в телеграм"
        )
    else:
        logging.debug("Сообщение было успешно отправлено")


def get_api_answer(timestamp: int) -> dict:
    """Запрос к API."""
    payload = {"from_date": timestamp}
    try:
        logging.debug(
            f"Отправляю запрос к API {ENDPOINT} c параметрами {payload}"
        )
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException as error:
        raise QueryToApiFail(f"Невозможно отправить запрос к API {error}")
    finally:
        if response.status_code != HTTPStatus.OK:
            raise requests.exceptions.HTTPError(
                f"Endpoint не доступен. Ошибка {response.status_code}"
            )
    return response.json()


def check_response(response: dict):
    """Проверка ответа от API."""
    if not isinstance(response, dict):
        raise TypeError(f"Неверный тип данных {type(response)}")
    if "homeworks" not in response:
        raise KeyError("Нет ключа homeworks")
    if not isinstance(response["homeworks"], list):
        raise TypeError(f"Неверный тип данных {type(response['homeworks'])}")


def parse_status(homework: dict) -> str:
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
    homework_status_old = ""
    error_message_old = ""

    while True:
        try:
            response = get_api_answer(timestamp)
            timestamp = response["current_date"]
            check_response(response)
            if len(response["homeworks"]) == 0:
                logging.debug("Список домашек пуст")
                send_message(bot, "Нет новых работ")
            else:
                homework_status_new = response.get("homeworks")[0]
                if homework_status_old != homework_status_new["status"]:
                    homework_status_old = homework_status_new["status"]
                    homework_status_send = parse_status(homework_status_new)
                    send_message(bot, homework_status_send)
                else:
                    logging.debug("Статус не изменился")
        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            logging.error(message)
            if message != error_message_old:
                send_message(bot, message)
                error_message_old = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s, %(levelname)s, %(message)s",
        stream=sys.stdout,
    )

    main()
