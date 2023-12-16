# devman_chat-bot-01

## Start and Config
- В корне необходимо скопировать файл `example.env` и вставить в ту же папку с именем `.env`.
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

## Config example
```
{
  "urls":
  {
    "user_reviews": "https://dvmn.org/api/long_polling/",
  },
  "timeout": 120,
  "sleep": 30,
  "message": "Mentor has checked your work!\nTheme: {title}\nLink: {url}\n\n{review}",
  "review_messages": ["Unfortunately there are errors in the work :(",
    "Everything is fine! You can proceed to the next lesson :)"],
}
```
