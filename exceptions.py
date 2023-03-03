class TelegramMessageSendFail(Exception):
    "Ошибка при отправке сообщения в телеграм"
    pass

class QueryToApiFail(Exception):
    "Ошибка при запросе к API"
    pass