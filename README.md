# devman_chat-bot-01

## Start and Config
- В папке `config/` необходимо скопировать файл `example.env` и вставить в ту же папку с именем `.env`.
- Указать корректные токены в соответствующие переменные.  
`DEVMAN_TOKEN` - токен пользователя API в Девман
`TG_BOT_TOKEN`- токен ТГ бота
`TG_CHAT_ID` - ID чата в личных сообщениях, в который бот будет отправлять оповещения

## Features
- Получить имя пользователя:
```
updates = bot.get_updates()
firts_name = updates[-1].message.from_user.first_name
```
- Используй файл `config/config.json` для настройки версии апи, задержек и текста отправляемых сообщений.