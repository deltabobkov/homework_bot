# Проект Homework Bot

![Python](https://img.shields.io/badge/Python-313131?style=flat&logo=Python&logoColor=white&labelColor=306998)
![Telegram](https://img.shields.io/badge/Telegram%20API-313131?style=flat&logo=telegram&logoColor=ffffff&labelColor=0088CC)
![Visual Studio](https://img.shields.io/badge/VS%20Code-313131?style=flat&logo=visualstudiocode&logoColor=ffffff&labelColor=0098FF)


## Телеграм-бот, который отслеживает статус проекта находящегося на ревью. Работает через API Практикум.Домашка
### Как запустить проект:

1. Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/deltabobkov/homework_bot.git

cd homework_bot
```

2. Cоздать и активировать виртуальное окружение:

```
python -m venv env

source env/Scripts/activate
```

3. Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip

pip install -r requirements.txt
```

4. Создать .env файл в корневой папке проекта, в котором должны содержаться следующие переменные:

```
PRACTICUM_TOKEN =   # токен API Практикума
TELEGRAM_TOKEN =  # Токен телеграм бота, полученого от бота BotFather
TELEGRAM_CHAT_ID =  # ID чата с ботом
```

5. Запустить проект:

```
python homework.py
```
