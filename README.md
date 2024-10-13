# CryptoBot для Telegram
Телеграм бот, який показує ціни на криптовалюти

[Спробуйте мого бота] (https://t.me/CCryptoBBot)

Про бота
------------
**Простий телеграм-бот, який показує ціну криптовалют. Використовує API Cryptocompare. Бот також працює в групових чатах**

Встановлення
------------
```shell
# Клонування
$ git clone https://github.com/onilyxe/CryptoBot.git

# Змініть робочу директорію на CryptoBot
$ cd CryptoBot
```

Налаштування
------------
**Відкрий `cryptobot.py` у текстовому редакторі та встановіть токен у рядку 17**
```ini
TOKEN = '0000000000:0000000000000000000000000000000000'
```
* `TOKEN` це токен для вашого Telegram-бота. Отримати його можна тут: [BotFather](https://t.me/BotFather)

Запуск
------------
Юзай Python
```shell
# Встановіть залежності
$ python3 -m pip install -r requirements.txt

# Запустити скрипт
$ python3 cryptobot.py
```