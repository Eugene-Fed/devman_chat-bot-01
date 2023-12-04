# devman_chat-bot-01

## Start and Config
- В папке `config/` необходимо скопировать файл `.env.example` и вставить в ту же папку с именем `.env`.
- Указать корректные токены в соответствующие переменные.

## Features
- Получить имя пользователя:
```
updates = bot.get_updates()
firts_name = updates[-1].message.from_user.first_name
```
